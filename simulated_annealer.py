'''
Use simulated annealing to solve the inputs. Attempts to overcome the drawbacks
of traditional hill climbing (local maxima, ridges, and plateaux).

We start with an alloted time/cycle budget, i. Instead of systematically choosing the
next assignment to look at (always increasing happiness), we use a probabilty
function to determine when to keep the current assignment or use a random assignment.
The probabilty function is:
    P = 1 if happiness(random_assignment) > happiness(current_assignment)   # can mess w this maybe
    P = math.exp( -(happiness(random) - happiness(curr)) / i )

The second part ensures that probability of accepting a random move decreases when
the difference between the random happiness and current happiness increases.

So we want to always accept good moves (high delta), but sometimes allow bad moves
(low delta) with a low probability. Look at graph of y=1/(1+e^-x) for rough estimate
of what P is.

As we start to run out of our alloted cycle budget, i, the probability of choosing
a bad move decreases (since we want to end on maximum, even if it's not the global).
Also note that if i = 0, this essentially becomes a greedy algorithm (only accepting
moves that increase happiness - so should work like estimator.py)

We can skip certain values of k immediately if we know it will result in an
invalid solution (see find_largest_k function).

Usage: python3 simulated_annealer.py
'''

import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness, \
    calculate_stress_for_room, calculate_happiness_for_room, convert_dictionary
import os
import re
import time
import random
import math

def main():
    '''
    Allow user to select whether to use 1. small 2. medium or 3. large inputs
    Outputs will be saved in the /sa_outputs directory
    If an input times out, it will be saved in the /sa_outputs/timedout directory
    '''
    input_length = ''
    print('Choose from the possible input sizes: \n1. Small\n2. Medium\n3. Large')
    selected_num = input("\nEnter the number of your choice: ")

    if selected_num == '1':
        input_length = 'small'
        print('\nLooking for small-{###}.in files in inputs/...')
    elif selected_num == '2':
        input_length = 'medium'
        print('\nLooking for medium-{###}.in files in inputs/...')
    elif selected_num == '3':
        input_length = 'large'
        print('\nLooking for large-{###}.in files in inputs/...')
    else:
        print('\nInvalid selection')
        return
    
    # Set alphanumeric key for sorting
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanumeric = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 

    # Iterate over files of chosen length in order
    for filename in sorted(os.listdir("inputs/"), key=alphanumeric):
        if input_length in filename:
            print(filename)
            path = os.path.join("inputs/", filename)
            G, s = read_input_file(path)

            # Find number of students, probably a better way
            with open(path, "r") as fo:
                n = fo.readline().strip()
                assert n.isdigit()
                n = int(n)
                fo.close()

            start = time.time()
            D, k = solve(G, s, n)
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
                    write_output_file(D, f'sa_outputs/{path[7:-3]}.out')
                # TODO: Write to different folder if timedout
            

def solve(G, s, n):
    largest_k = find_largest_k(G, s, n) # potentially use this?
    # assignment = {} # maps students to rooms

    # TODO: Find a way to generate all possible room assignments
    all_assignments = generate_all_possible_assignments(G, n, largest_k)

    # Set current state/assignment to the initial assignment
    curr_assignment = all_assignments[0]
    i = 1000 # counter of how many times to loop, essentially alloted time budget

    while i > 0:
        # Find the total happiness of the current assignment
        curr_happiness = calculate_happiness()

        # Pick the next assignment randomly from all possible assignments
        # TODO: Keep track of assignments picked (e.g. their indexes) so we don't
        #       randomly choose them again?
        new_assignment = all_assignments[random.randint(0, len(all_assignments))]
        # Find the total happiness of the new assignment
        new_happiness = calculate_happiness()

        delta_happiness = new_happiness - curr_happiness

        # If the new assignment is better, then replace the current assignment
        if delta_happiness > 0:
            curr_assignment = new_assignment
        else:
            # If new assignment is worse, still replace it if we haven't looped
            #   very many times (e.g. i is high)
            # This is because we want to encourage randomizing if we just started
            #   looking at assignments, but discourage it later (but still possible)
            if math.exp(-(delta_happiness)/i) > random.uniform(0,1):
                curr_assignment = new_assignment

        i -= 1

    return curr_assignment, len(set(curr_assignment.values()))

def generate_all_possible_assignments(G, n, k):
    '''
    Generate all possible assignments mapping n students to at most k rooms.

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
    #   and then figure out which assignments are the same, but with only room numbers
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
    # main()

    # Debug for a single input file
    path = 'samples/10.in'
    G, s = read_input_file(path)

    with open(path, "r") as fo:
        n = fo.readline().strip()
        assert n.isdigit()
        n = int(n)
        fo.close()
    find_largest_k(G, s, n)
