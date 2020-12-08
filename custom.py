import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness, calculate_stress_for_room, calculate_happiness_for_room, \
    convert_dictionary
import os, time, random, math


def large_96(G, budget):
    """
    Solution for large-96.in. Uses local search with swaps as neighbors
    Returns:

    """
    numStudents = len(G.nodes)
    assignment = {}  # maps student to rooms
    for s in range(numStudents):
        assignment[s] = s // 2

    move = getBetterAssignment(G, budget, assignment, 0)
    while move:
        student, swapStudent, curHappiness = move
        assignment[student], assignment[swapStudent] = assignment[swapStudent], assignment[student]
        move = getBetterAssignment(G, budget, assignment, curHappiness)
    return assignment, len(set(assignment.values())), calculate_happiness(assignment, G)


def large_96_sa(G, budget, startAssignment=None):
    """
    Solution for large-96.in. Uses simulated annealing with swaps as neighbors
    Args:
        G:
        budget:
    Returns:

    """
    numStudents = len(G.nodes)
    assignment = startAssignment  # maps student to rooms
    if assignment is None:
        assignment = {}
        for s in range(numStudents):
            assignment[s] = s

    def accept_probability(delta, temperature):
        if temperature == 0:
            return 0
        else:
            return math.exp(-delta / temperature)

    # iteration = -1
    temperature = 50
    decay = 0.9949
    cutoff = 0.3
    curHappiness = 0
    move = getRandomMove(G, budget, assignment, numStudents)
    while move:
        # iteration += 1
        student, swapStudent, newHappiness = move
        temperature *= 0 if temperature < cutoff else decay

        # if iteration % 500 == 0:
        #     print(newHappiness, iteration)

        if temperature > 0:
            # Do simulated annealing

            # delta = -s' - (-s) = s - s' where s is the happiness of the state and
            # the cost function is the negation of the happiness
            delta = curHappiness - newHappiness
            if delta < 0:
                assignment[student], assignment[swapStudent] = assignment[swapStudent], assignment[student]
                curHappiness = newHappiness
            elif random.uniform(0, 1) < accept_probability(delta, temperature):
                assignment[student], assignment[swapStudent] = assignment[swapStudent], assignment[student]
                curHappiness = newHappiness
            move = getRandomMove(G, budget, assignment, numStudents)
        else:
            # Do local search
            assignment[student], assignment[swapStudent] = assignment[swapStudent], assignment[student]
            move = getBetterAssignment(G, budget, assignment, numStudents, newHappiness)

    return assignment, len(set(assignment.values())), calculate_happiness(assignment, G)


def getRandomMove(G, s, D):
    student = None
    move = None
    student1 = list(range(len(G.nodes)))
    student2 = list(range(len(G.nodes)))
    random.shuffle(student1)

    for curStudent in student1:
        student2.remove(curStudent)
        random.shuffle(student2)
        for swapStudent in student2:
            D[curStudent], D[swapStudent] = D[swapStudent], D[curStudent]
            if is_valid_solution(D, G, s, len(set(D.values()))):
                newHappiness = calculate_happiness(D, G)
                D[curStudent], D[swapStudent] = D[swapStudent], D[curStudent]
                return curStudent, swapStudent, newHappiness
            D[curStudent], D[swapStudent] = D[swapStudent], D[curStudent]

    if student is None:
        return None
    return student, move


def getBetterAssignment(G, s, D, curHappiness):
    student = None
    move = None
    student1 = list(range(len(G.nodes)))
    student2 = list(range(len(G.nodes)))
    random.shuffle(student1)

    for curStudent in student1:
        student2.remove(curStudent)
        random.shuffle(student2)
        for swapStudent in student2:
            D[curStudent], D[swapStudent] = D[swapStudent], D[curStudent]
            if is_valid_solution(D, G, s, len(set(D.values()))):
                newHappiness = calculate_happiness(D, G)
                if curHappiness < newHappiness:
                    # print(curHappiness, newHappiness)
                    D[curStudent], D[swapStudent] = D[swapStudent], D[curStudent]
                    return curStudent, swapStudent, newHappiness
            D[curStudent], D[swapStudent] = D[swapStudent], D[curStudent]

    if student is None:
        return None
    return student, move


if __name__ == "__main__":
    repeat = 2
    input_dir = "shits_"
    timeout_fname = "custom"
    timeout_path = f"{timeout_fname}/"
    solved_path = f"{timeout_fname}/"
    for fname in sorted(os.listdir(input_dir), reverse=True):
        isSolved = os.path.isfile(f"{solved_path}{fname[:-3]}.out")
        isComputed = os.path.isfile(f"{timeout_path}{fname[:-3]}.out")
        if "large-112" in fname and not isSolved and not isComputed:
            print("Starting fname: ", fname)
            path = os.path.join(input_dir, fname)
            G, s = read_input_file(path)

            start = time.time()
            bestHappiness = -1
            bestD = None
            bestk = None
            for i in range(repeat):
                D, k, curHappiness = large_96(G, s)
                if bestHappiness < curHappiness:
                    bestD = D.copy()
                    bestk = k
                    bestHappiness = curHappiness

            end = time.time()

            assert is_valid_solution(bestD, G, s, bestk)
            print("Total Happiness: {}".format(calculate_happiness(bestD, G)))
            print(f"Solving {fname} took {end - start} seconds.")
            if path[-3:] == ".in":
                write_output_file(bestD, f'{solved_path}{fname[:-3]}.out')
            else:
                write_output_file(bestD, f'test/test.out')
