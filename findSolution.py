import networkx as nx
from parse import read_input_file, write_output_file, read_output_dict
from utils import is_valid_solution, calculate_happiness, calculate_stress_for_room
import time, copy
import os


def bruteForce(G, s):
    bruteForce(G, s, 0)


def bruteForce(G, s, timeoutInSeconds=300, cachedSolution=None, cachedAssignment=None):
    """
    Brute force with backtracking on solution validity. Return first valid solution.
    Args:
        G: Graph representation of the problem
        s: Max Stress
        timeoutInSeconds: The amount of time to run the algorithm.
        0 if you want no timeout
        cachedSolution: A dictionary of the cached best solution found so far.
        cachedAssignment: A dictionary of a cached assignment to start from.

    Returns: First valid solution found

    """
    numStudents = len(G.nodes)

    bestAssignment = cachedSolution
    bestNumRooms = -1
    if bestAssignment is not None:
        uniqueRooms = set()
        for value in bestAssignment.values():
            uniqueRooms.add(value)
        bestNumRooms = len(uniqueRooms)

    lastAssignment = None
    bestScore = -1 if bestAssignment is None \
        else calculate_happiness(bestAssignment, G)
    start = time.time()
    curAssignment = {}
    timeout = 0

    def dfs(curAssignment, numAssigned, numRooms):
        nonlocal bestAssignment, bestNumRooms, bestScore, timeout, lastAssignment, cachedAssignment
        # Ignore assignments with more than "numStudents" rooms.
        if numRooms >= numStudents:
            return

        # Clear cachedAssignment once we finish in to cached assignment.
        if cachedAssignment is not None and curAssignment == cachedAssignment:
            cachedAssignment = None

        # If all students are assigned check if assignment is better
        if numAssigned >= numStudents:
            curScore = calculate_happiness(curAssignment, G)
            if curScore > bestScore:
                bestAssignment = copy.deepcopy(curAssignment)
                bestNumRooms = numRooms
                bestScore = curScore
                print("Best Score: ", bestScore)
            return

        # End early if timed out and return best solution
        if timeoutInSeconds and time.time() > start + timeoutInSeconds:
            timeout = -1
            if lastAssignment is None:
                lastAssignment = copy.deepcopy(curAssignment)
            return

        # Define starting room. Only nonzero when there is a cached assignment
        minRoom = 0
        if cachedAssignment is not None and numAssigned in cachedAssignment:
            minRoom = cachedAssignment[numAssigned]
            # print("Cached", numAssigned, minRoom)

        # Go through all possible room assignments for the next student
        for room in range(minRoom, numRooms + 1):
            curAssignment[numAssigned] = room
            newNumRooms = max(numRooms, room + 1)

            if is_valid_solution(curAssignment, G, s, newNumRooms):
                dfs(curAssignment, numAssigned + 1, newNumRooms)

        del curAssignment[numAssigned]

    dfs(curAssignment, 0, 0)
    return bestAssignment, bestNumRooms, timeout, lastAssignment


if __name__ == "__main__":
    timeout_in_seconds = 600
    input_dir = "shits_"
    timeout_fname = "10min_timeout_outputs"
    cache_path = "5min_timeout_outputs2"
    timeout_path = f"{timeout_fname}/"
    solved_path = "solved/"
    for fname in sorted(os.listdir(input_dir), reverse=False):
        isSolved = os.path.isfile(f"{solved_path}{fname[:-3]}.out")
        isComputed = os.path.isfile(f"{timeout_path}{fname[:-3]}.out")
        if "medium-16.in" in fname and not isSolved and not isComputed:
            print("starting fname: ", fname)
            path = os.path.join(input_dir, fname)
            G, s = read_input_file(path)

            start = time.time()
            # Use Cache if available
            cachedSolution = None
            cachedAssignment = None
            cachedSolutionFile = os.path.join(cache_path, f"{fname[:-3]}.out")
            cachedAssignmentFile = os.path.join(cache_path, "cache", f"{fname[:-3]}last.out")
            if os.path.isfile(cachedSolutionFile) and os.path.isfile(cachedAssignmentFile):
                print("Using caches: ", cachedSolutionFile, cachedAssignmentFile)
                cachedSolution = read_output_dict(cachedSolutionFile)
                cachedAssignment = read_output_dict(cachedAssignmentFile)
                print(cachedSolution)
                print(cachedAssignment)

            D, k, t, D_last = bruteForce(G, s, timeout_in_seconds, cachedSolution, cachedAssignment)
            end = time.time()
            print(f"Solution: {D}, {k}")

            # Save work done already
            if path[-3:] == ".in" and D_last is not None:
                write_output_file(D_last, f'{timeout_fname}/cache/{fname[:-3]}last.out')

            if D is None:
                if path[-3:] == ".in":
                    write_output_file({"NO SOLUTION": 1}, f'{timeout_fname}/{fname[:-3]}-no-sol.out')
                    print(fname, " timed out. No solution found.")
                else:
                    write_output_file(D, f'test/test.out')
                continue

            assert is_valid_solution(D, G, s, k)
            print("Total Happiness: {}".format(calculate_happiness(D, G)))
            print("Solving took {} seconds.".format(end - start))
            if t == -1:
                if path[-3:] == ".in":
                    write_output_file(D, f'{timeout_fname}/{fname[:-3]}.out')
                    print(fname, " timed out.")
                else:
                    write_output_file(D, f'test/test.out')
            else:
                if path[-3:] == ".in":
                    write_output_file(D, f'solved/{fname[:-3]}.out')
                else:
                    write_output_file(D, f'test/test.out')
