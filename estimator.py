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
    move = getBetterAssignment(G, budget, assignment, numStudents)
    while move:
        student, newRoom = move
        assignment[student] = newRoom
        if (random.random() > schedule(counter)):
            move = getBetterAssignment(G, budget, assignment, numStudents)
        else:
            move = randomMove(G, budget, assignment, numStudents)
        counter += 1
    print("COUNTER IS ", counter)
    return assignment, len(set(assignment.values()))

def schedule(t):
    return 0.49 * math.exp(-0.07 * t) + 0.005

def randomMove(G, s, D, maxRooms):
    start = time.time()
    curStudent = None
    newRoom = None
    while True:
        curStudent = random.choice(range(len(G.nodes)))
        oldRoom = D[curStudent]
        newRoom = random.choice(list(range(maxRooms)))
        if oldRoom == newRoom:
            continue
        D[curStudent] = newRoom
        if is_valid_solution(D, G, s, num_rooms(D)):
            D[curStudent] = oldRoom
            break
    print("random took", time.time() - start, "seconds")
    return curStudent, newRoom

def getBetterAssignment(G, s, D, maxRooms):
    maxHappiness = calculate_happiness(D, G)
    student = None
    move = None

    for curStudent in random.sample(list(range(len(G.nodes))), len(G.nodes)):
        oldRoom = D[curStudent]
        for newRoom in random.sample(list(range(maxRooms)), maxRooms):
            D[curStudent] = newRoom
            if is_valid_solution(D, G, s, len(set(D.values()))):
                newHappiness = calculate_happiness(D, G)
                if maxHappiness < newHappiness:
                    maxHappiness = newHappiness
                    student = curStudent
                    move = newRoom

        D[curStudent] = oldRoom

    if student is None:
        return None
    return student, move

if __name__ == "__main__":
    for fname in sorted(os.listdir("inputs/")):
        if fname[:-3] + ".out" not in os.listdir("test_4_outputs"):
            print('pseudo greedying', fname)
            path = os.path.join("inputs", fname)
            G, s = read_input_file(path)

            start = time.time()
            D, k = estimate(G, s)
            end = time.time()

            assert is_valid_solution(D, G, s, k)
            print("Total Happiness: {}".format(calculate_happiness(D, G)))
            print("Solving took {} seconds.".format(end - start))
            if path[-3:] == ".in":
                write_output_file(D, f'test_4_outputs/{path[7:-3]}.out')
            else:
                write_output_file(D, f'test/test.out')
