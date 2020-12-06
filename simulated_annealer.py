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
from parse import read_input_file, write_output_file, read_output_dict
from utils import is_valid_solution, calculate_happiness, \
    calculate_stress_for_room, calculate_happiness_for_room, convert_dictionary
import os
import re
import time
import random
import math

CYCLE_BUDGET = 10000
SAMPLE_SIZE = 10
MODES = 6
def main():
    '''
    Anneal, based on parameters in main. Write to different folders depending on specific parameters
    Timeout is intentional. Want to see how time efficient different algorithms are.
    '''

    # Set alphanumeric key for sorting
    convert = lambda text: int(text) if text.isdigit() else text
    alphanumeric = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]

    # Iterate over files of chosen length in order
    for mode in range(MODES):
        for filename in sorted(os.listdir("inputs/"), key=alphanumeric)[0:SAMPLE_SIZE]:
            if 'large' in filename:
                print("annealing", filename)
                path = os.path.join("inputs/", filename)
                G, s = read_input_file(path)

                #starter = read_output_dict(os.path.join("flattened_greedy_outputs", filename[:-3] + ".out"))
                # Find number of students, probably a better way exists
                with open(path, "r") as fo:
                    n = fo.readline().strip()
                    assert n.isdigit()
                    n = int(n)
                    fo.close()

                starter = {}
                if mode % 3 == 0:
                    starter = read_output_dict(os.path.join("flattened_greedy_outputs", filename[:-3] + ".out"))
                else:
                    for i in range(n):
                        starter[i] = i
                start = time.time()
                D, k = solve(G, s, n, starter)
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
                        write_output_file(D, f'test_{mode}_outputs/{path[7:-3]}.out')
        mode += 1


def solve(G, s, n, starter=None, timeoutInSeconds=180):
    largest_k = find_largest_k(G, s, n) # potentially use this?
    # assignment = {} # maps students to rooms

    # Generate a neighborhood based on greedy solution
    curr_assignment = starter

    # Set current state/assignment to the initial assignment
    i = 0 # counter of how many times to loop, essentially alloted cycle budget
             # TODO: Find an ideal value for i
    starttime = time.time()
    while i < CYCLE_BUDGET and time.time() < timeoutInSeconds:
        # Find the total happiness of the current assignment
        curr_happiness = calculate_happiness(curr_assignment, G)

        curr_neighborhood_size = neighborhood_size(i) #gonna try this for now, then use the function

        new_assignment = random_neighbor(G, s, starter, neighborhood_size(i), merge_prob(i))

        #all_assignments[random.randint(0, len(all_assignments))]
        # Find the total happiness of the new assignment
        new_happiness = calculate_happiness(new_assignment, G)

        delta_happiness = new_happiness - curr_happiness

        # If the new assignment is better, then replace the current assignment
        if delta_happiness > 0:
            curr_assignment = new_assignment
        else:
            # If new assignment is worse, still replace it if we haven't looped
            #   very many times (e.g. i is high)
            # This is because we want to encourage randomizing if we just started
            #   looking at assignments, but discourage it later (but still possible)
            if use_worse(delta_happiness, CYCLE_BUDGET -  i) > random.uniform(0,1):
                curr_assignment = new_assignment

        i += 1

    return curr_assignment, len(set(curr_assignment.values()))

# Pick a random neighbor of starter
def neighborhood_size(t):
    if mode % 2:
        return int(20 * math.exp(-0.004 * t) + 1)
    else:
        return 4

def merge_prob(t):
    if mode % 2:
        return 0.8 * math.exp(-0.003 * t)
    else:
        return 0.1

def use_worse(delta, t):
    return math.exp(-delta/t)

def progress_checker(prog, total):
    for j in range(10):
        if prog == j * total // 10:
            print(f'{j*10}%')
def random_neighbor(G, s, starter, neighborhood, merge_threshold):
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
        for i in range(neighborhood):
            if random.uniform(0, 1) > merge_threshold:
                random_swap(cur)
            else:
                random_merge(cur)
        if is_valid_solution(cur, G, s, len(set(cur.values()))):
            break
    return cur

def random_swap(D):
    lst = random.sample(list(D.keys()), 2)
    v1 = D[lst[0]]
    v2 = D[lst[1]]
    D[lst[0]] = v2
    D[lst[1]] = v1

def random_merge(D):
    lst = random.sample(list(D.keys()), 2)
    D[lst[0]] = D[lst[1]]

def generate_neighborhood(G, n, k, starter, neighborhood=10):
    '''
    Generate all neighborhood of assignments, based at starter, that
    maps n students to at most k rooms.

    Returns a list of dictionary mappings.

    TODO: I don't know how feasible this is considering that we don't want duplicates
          of mappings with only room index differing. It's a much bigger issue with
          large n.

          e.g. For 3 students...
          0 0     is the same as     0 1
          1 1                        1 0
          2 1                        2 0
    '''
    # Maybe try using Cartesian product of two np.arrays (student indexes and room indexes)
    #   and then figure out which assignments are the same but with only room numbers
    #   differing and remove them.
    pass

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
