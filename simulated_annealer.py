'''
Use simulated annealing to solve the inputs. Attempts to overcome the drawbacks
of traditional hill climbing (local maxima, ridges, and plateaux).

We start with an alloted time/cycle budget, i. Instead of systematically choosing the
next assignment to look at (always increasing happiness), we use a probabilty
function to determine when to keep the current assignment or use a random assignment.
The probabilty function is:
    P = 1 if happiness(random_assignment) > happiness(current_assignment)   # can mess w this maybe
    P = math.exp( -(happiness(random) - happiness(curr)) / i ) otherwise

The second part ensures that probability of accepting a random move decreases when
the difference between the random happiness and current happiness increases.

So we want to always accept good moves (high delta), but sometimes allow bad moves
(low delta) with a low probability. Look at graph of y=1/(1+e^-x) for rough estimate
of what P would be for different delta.

As we start to run out of our alloted cycle budget, i, the probability of choosing
a bad move decreases (since we want to end on maximum, even if it's not the global).
Also note that if i = 0, this essentially becomes a greedy algorithm (only accepting
moves that increase happiness - so should work like estimator.py)

We can skip certain values of k immediately if we know it will result in an
invalid solution (see find_largest_k function).

Usage: python3 simulated_annealer.py
'''
import networkx as nx
from parse import *
from utils import *
import os
import re
import time
import random
import math

CYCLE_BUDGET = 10000000
REPETITIONS = 50
SAMPLE_SIZE = 10

def main():
    '''
    Anneal, based on parameters in main. Write to different folders depending on specific parameters
    Timeout is intentional. Want to see how time efficient different algorithms are.
    '''

    # Set alphanumeric key for sorting
    convert = lambda text: int(text) if text.isdigit() else text
    alphanumeric = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]

    # Iterate over files of chosen length in order
    for filename in sorted(os.listdir("medium_inputs/"), key=alphanumeric)[0:SAMPLE_SIZE]:
        if 'medium' in filename:
            print("annealing", filename)
            path = os.path.join("medium_inputs/", filename)
            G, s = read_input_file(path)

            #starter = read_output_dict(os.path.join("flattened_greedy_outputs", filename[:-3] + ".out"))
            # Find number of students, probably a better way exists
            with open(path, "r") as fo:
                n = fo.readline().strip()
                assert n.isdigit()
                n = int(n)
                fo.close()

            starter = {}
            for i in range(n):
                starter[i] = i

            start = time.time()
            D = starter
            k = n
            for i in range(REPETITIONS):
                ND, Nk = solve(G, s, n, starter=starter)
                if calculate_happiness(ND, G) > calculate_happiness(D, G):
                    D = ND.copy()
                    k = Nk

            end = time.time()
            try:
                assert is_valid_solution(D, G, s, k)
            except:
                print('=====CALCULATED SOLUTION IS INVALID=====')
            finally:
                print("Total Happiness: {}".format(calculate_happiness(D, G)))
                print("Solving took {} seconds".format(end - start))

                # Write output file to sa_outputs/
                if path[-3:] == ".in":
                    write_output_file(D, f'test_outputs/{path[7:-3]}.out')

def solve(G, s, n, starter=None, timeoutInSeconds=5):
    largest_k = find_largest_k(G, s, n) # potentially use this?
    # assignment = {} # maps students to rooms

    # Generate a neighborhood based on greedy solution
    curr_assignment = starter.copy()

    # Set current state/assignment to the initial assignment
    i = 0 # counter of how many times to loop, essentially alloted cycle budget
             # TODO: Find an ideal value for i
    starttime = time.time()
    while i < CYCLE_BUDGET and time.time() < timeoutInSeconds + starttime:
        # Find the total happiness of the current assignment
        curr_happiness = calculate_happiness(curr_assignment, G)
        #print(curr_happiness)
        new_assignment = {}
        # if we started recently, take a move thats likely to result in a new arrangement
        # otherwise, spread out search area, and do a different approach.
        stud, room = randomMove(G, s, curr_assignment, num_rooms(curr_assignment))
        new_assignment = curr_assignment.copy()
        new_assignment[stud] = room

        # Find the total happiness of the new assignment
        new_happiness = calculate_happiness(new_assignment, G)

        delta_happiness = new_happiness - curr_happiness

        # If the new assignment is better, then replace the current assignment
        if delta_happiness >= 0:
            curr_assignment = new_assignment;
        else:
            # If new assignment is worse, still replace it if we haven't looped
            #   very many times (e.g. i is high)
            # This is because we want to encourage randomizing if we just started
            #   looking at assignments, but discourage it later (but still possible)
            if use_worse(delta_happiness, i) > random.uniform(0,1):
                print("SWITCHING ANYWAY LOL=======================")
                curr_assignment = new_assignment
        i += 1
    return curr_assignment, num_rooms(curr_assignment)

def randomMove(G, s, D, maxRooms):
    start = time.time()
    maxHappiness = calculate_happiness(D, G)
    student = None
    move = None
    #print(range(len(G.nodes)))
    for curStudent in random.sample(list(range(len(G.nodes))), len(list(range(len(G.nodes))))):
        oldRoom = D[curStudent]
        for newRoom in random.sample(list(range(maxRooms)), maxRooms):
            D[curStudent] = newRoom
            if is_valid_solution(D, G, s, len(set(D.values()))):
                D[curStudent] = oldRoom
                return curStudent, newRoom

        D[curStudent] = oldRoom

    if student is None:
        return None
    print("random took", time.time() - start)
    return student, move

def use_worse(delta, t):
    return 0.69 * math.exp(-0.03 * t)

def progress_checker(prog, total):
    for j in range(10):
        if prog == j * total // 10:
            print(f'{j*10}%')

def random_neighbor(G, s, starter, neighborhood, merge_threshold=0):
    '''
    A neighbor of an assignment is either a swap of two students, or
    moving one student into another's room
    I figure that merging a student into another's room isn't gonna meet stress
    requirements very often, so I only do that with 20% chance
    '''
    valid = False
    cur = starter.copy()
    while True:
        cur = starter.copy()
        #print(cur)
        movers = random.sample(list(cur.keys()), neighborhood)
        rooms = random.choice(list(cur.values()), neighborhood)
        for i in range(neighborhood):
            cur[movers[i]] = rooms[i]
        if cur == starter:
            continue;
        if is_valid_solution(cur, G, s, len(set(cur.values()))):
            break
    return cur

def find_largest_k(G, s, n):
    '''
    Finds the largest possible value of k (number of rooms) given the requirement
    that S_ij <= S_max / k.
    The maximum room size is k = n where each student is in their own room.
    '''
    num_students = n # probably a better way to find n
    largest_stress = max(dict(G.edges).items(), key=lambda x: x[1]['stress'])[1]['stress']
    largest_k = num_students

    # Counts down from num_students to 1
    for k in range(num_students, 0, -1):
        if largest_stress < s/k:
            largest_k = k
            break

    # For debugging purposes...
    # print("The number of students is: " + str(num_students))
    # print("The largest stress is: " + str(largest_stress))
    # print("The largest possible k is: " + str(largest_k))

    return largest_k

if __name__ == '__main__':
    # Uncomment line below to run on all input files and comment out the debug section
    main()

    # Debug for a single input file
    # path = 'samples/10.in'
    # G, s = read_input_file(path)
    #
    # with open(path, "r") as fo:
    #     n = fo.readline().strip()
    #     assert n.isdigit()
    #     n = int(n)
    #     fo.close()
    # find_largest_k(G, s, n)
    # END Debug for a single input file
