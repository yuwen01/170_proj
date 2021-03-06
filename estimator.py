import networkx as nx
from parse import *
from utils import *
import sys
import os
import time
import random
import math

''' simulated annealing bay bee
G: the graph of the students and their breakout rooms
samples_per: how many members are in each generation
kept_per: how many solutions to keep in each generation
loops: how many generations to process
seed: seed for the rng

TODO: This is just gradient descent atm, probably should add a chance to consider
horrible solutions for reasons described in textbook

also i am clearly not going to have time to finish this tonight i am so tired
'''


def estimate(G, s):
    return greedy_solution(G, s)


def greedy_solution(G, budget):
    """
    Hill climbing solution

    Returns:

    """
    numStudents = len(G.nodes)
    assignment = {}  # maps student to rooms
    for s in range(numStudents):
        assignment[s] = s

    counter = 0
    timeout = 480
    move = getBetterAssignment(G, budget, assignment, numStudents)
    start = time.time()
    good = 1
    while good and time.time() < start + timeout:
        good = getBetterAssignment(G, budget, assignment, numStudents)
        counter += 1
    return assignment, len(set(assignment.values()))

def schedule(t):
    return 0.49 * math.exp(-0.07 * t)

def randomMove(G, s, D, maxRooms):
    start = time.time()
    maxHappiness = calculate_happiness(D, G)
    student = None
    move = None
    random_students = random.sample(list(range(len(G.nodes))), len(list(range(len(G.nodes)))))
    random_rooms = random.sample(list(range(maxRooms)), maxRooms)
    #print(range(len(G.nodes)))
    for curStudent in random_students:
        oldRoom = D[curStudent]
        for newRoom in random_rooms:
            D[curStudent] = newRoom
            if is_valid_solution(D, G, s, len(set(D.values()))):
                D[curStudent] = oldRoom
                return curStudent, newRoom

        D[curStudent] = oldRoom

    if student is None:
        return None
    print("random took", time.time() - start)
    return student, move

def getBetterAssignment(G, s, D, maxRooms):
    start = time.time()
    maxHappiness = calculate_happiness(D, G)
    student = None
    move = None
    backup = D.copy()
    for curStudent in list(range(len(G.nodes))):
        oldRoom = D[curStudent]
        for newRoom in list(range(maxRooms)):
            D[curStudent] = newRoom
            if is_valid_solution(D, G, s, len(set(D.values()))):
                newHappiness = calculate_happiness(D, G)
                if maxHappiness < newHappiness:
                    maxHappiness = newHappiness
                    student = curStudent
                    move = newRoom

        D[curStudent] = oldRoom

    single_swap_max_hap = maxHappiness
    assert D == backup
    best_pair = (-1, -1)

    for stud1 in range(len(G.nodes)):
        for stud2 in range(stud1 + 1, len(G.nodes)):
            if D[stud1] == D[stud2]:
                continue
            D[stud1], D[stud2] = D[stud2], D[stud1]
            if is_valid_solution(D, G, s, len(set(D.values()))):
                newHappiness = calculate_happiness(D, G)
                if newHappiness < maxHappiness:
                    maxHappiness = newHappiness
                    best_pair = (stud1, stud2)
            D[stud1], D[stud2] = D[stud2], D[stud1]

    if student == None and best_pair == (-1, -1):
        return 0
    assert D == backup
    if maxHappiness > single_swap_max_hap:
        stud1, stud2 = best_pair[0], best_pair[1]
        D[stud1], D[stud2] = D[stud2], D[stud1]
    else:
        D[student] = move

    return 1

if __name__ == "__main__":
    for fname in sorted(os.listdir("shits_/")):
        if fname[:-3] + ".out" not in os.listdir("twowide"):
            print('pseudo greedying', fname)
            path = os.path.join("shits_", fname)
            G, s = read_input_file(path)

            start = time.time()
            D, k = estimate(G, s)
            end = time.time()

            assert is_valid_solution(D, G, s, k)
            print("Total Happiness: {}".format(calculate_happiness(D, G)))
            print("Solving took {} seconds.".format(end - start))
            if path[-3:] == ".in":
                write_output_file(D, f'twowide/{path[7:-3]}.out')
            else:
                write_output_file(D, f'test/test.out')
