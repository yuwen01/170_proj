import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness, calculate_stress_for_room, calculate_happiness_for_room, \
    convert_dictionary
import os, time, random

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


def estimate(G, s, neighborhood=2, samples_per=15, kept_per=4, loops=100, seed=69):
    return local_search(G, s)


''' the point of this is to get a starting point. Ideally, search radius will decrease over time,
so we don't have such consistent starts. I'm only doing this because I don't know how to randomly
generate a starting solution that meets stress requirements

this algorithm sucks ass
'''


def greedy_solution(G, budget, neighborhood=-1, base=None):
    """
    Hill climbing solution
    Args:
        G:
        budget:
        neighborhood:
        base:

    Returns:

    """
    numStudents = len(G.nodes)
    assignment = {}  # maps student to rooms
    for s in range(numStudents):
        assignment[s] = s

    move = getBestAssignment(G, budget, assignment, numStudents)
    while move:
        student, newRoom = move
        assignment[student] = newRoom
        move = getBestAssignment(G, budget, assignment, numStudents)
    return assignment, len(set(assignment.values()))


def getBestAssignment(G, s, D, maxRooms):
    maxHappiness = calculate_happiness(D, G)
    student = None
    move = None

    for curStudent in range(len(G.nodes)):
        oldRoom = D[curStudent]
        for newRoom in range(maxRooms):
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


def balance(G, budget, assignment):
    # assignment here maps rooms to students
    room_lim = budget / len(assignment)
    new_rooms = {}
    for room, students in assignment.items():
        if calculate_stress_for_room(students, G) > room_lim:
            # originally planned to just yeet the most stress inducing person
            # clearly can't
            # argmax = 0
            # stressor = G.nodes[students[0]]['stress']
            # for i, v in enumerate(students[1:]):
            #     if G.nodes[v]['stress'] > stressor:
            #         stressor = G.nodes[v]['stress']
            #         argmax = i
            first = students.pop()
            assignment[room] = students
            new_rooms[len(assignment) - 1 + len(new_rooms)] = [first]

    assignment.update(new_rooms)


def local_search(G, budget):
    """
    Local Search. Similar to hill climbing but it only needs to find a better neighbor instead
    of the best neighbor
    Args:
        G:
        budget:
    Returns:

    """
    numStudents = len(G.nodes)
    assignment = {}  # maps student to rooms
    for s in range(numStudents):
        assignment[s] = s

    move = getBetterAssignment(G, budget, assignment, numStudents)
    while move:
        student, newRoom = move
        assignment[student] = newRoom
        move = getBetterAssignment(G, budget, assignment, numStudents)
    return assignment, len(set(assignment.values()))


def getBetterAssignment(G, s, D, maxRooms):
    curHappiness = calculate_happiness(D, G)
    student = None
    move = None

    for curStudent in random.shuffle(range(len(G.nodes))):
        oldRoom = D[curStudent]
        for newRoom in random.shuffle(range(maxRooms)):
            D[curStudent] = newRoom
            if is_valid_solution(D, G, s, len(set(D.values()))):
                newHappiness = calculate_happiness(D, G)
                if curHappiness < newHappiness:
                    D[curStudent] = oldRoom
                    return curStudent, newRoom

        D[curStudent] = oldRoom

    if student is None:
        return None
    return student, move


if __name__ == "__main__":
    for fname in os.listdir("inputs/"):
        if "medium" in fname:
            path = os.path.join("inputs", fname)
            G, s = read_input_file(path)

            start = time.time()
            D, k = estimate(G, s)
            end = time.time()

            assert is_valid_solution(D, G, s, k)
            print("Total Happiness: {}".format(calculate_happiness(D, G)))
            print("Solving took {} seconds.".format(end - start))
            if path[-3:] == ".in":
                write_output_file(D, f'estoutputs/{path[7:-3]}.out')
            else:
                write_output_file(D, f'test/test.out')
