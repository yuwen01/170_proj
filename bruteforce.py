import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness, calculate_stress_for_room
import time, copy
import os


def bruteForce(G, s):
    bruteForce(G, s, 0)


def bruteForce(G, s, timeoutInSeconds=1):
    """
    Brute force with backtracking on solution validity
    Args:
        G: Graph representation of the problem
        s: Max Stress
        timeoutInSeconds: The amount of time to run the algorithm.
        0 if you want no timeout

    Returns: Best solution sound so far

    """
    numStudents = len(G.nodes)

    bestAssignment = None
    bestNumRooms = -1
    lastAssignment = None
    bestScore = -1
    start = time.time()
    curAssignment = {}
    timeout = 0

    def dfs(curAssignment, numAssigned, numRooms):
        nonlocal bestAssignment, bestNumRooms, bestScore, timeout, lastAssignment
        # End early if timed out and return best solution
        if timeoutInSeconds and time.time() > start + timeoutInSeconds:
            timeout = -1
            if lastAssignment is None:
                lastAssignment = copy.deepcopy(curAssignment)
            return

        # Ignore assignments with more than "numStudents" rooms.
        if numRooms >= numStudents:
            return

        # If all students are assigned check if assignment is better
        if numAssigned >= numStudents:
            curScore = calculate_happiness(curAssignment, G)
            if curScore > bestScore:
                bestAssignment = copy.deepcopy(curAssignment)
                bestNumRooms = numRooms
                bestScore = curScore
            return

        # Go through all possible room assignments for the next student
        for room in range(numRooms + 1):
            curAssignment[numAssigned] = room
            newNumRooms = max(numRooms, room + 1)

            if is_valid_solution(curAssignment, G, s, newNumRooms):
                dfs(curAssignment, numAssigned + 1, newNumRooms)

        del curAssignment[numAssigned]

    dfs(curAssignment, 0, 0)
    return bestAssignment, bestNumRooms, timeout, lastAssignment


if __name__ == "__main__":
    timeout_fname = "5min_timeout_outputs"
    timeout_fnames = os.listdir("1sec_timeout_outputs")
    output_fnames = os.listdir(timeout_fname)
    solved_fnames = os.listdir("solved")
    for fname in sorted(os.listdir("inputs/")):
        if "medium" in fname and f'{fname[:-3]}.out' not in timeout_fnames and \
                f'{fname[:-3]}.out' not in output_fnames and f'{fname[:-3]}.out' not in solved_fnames:
            print("starting fname: ", fname)
            path = os.path.join("inputs", fname)
            G, s = read_input_file(path)

            start = time.time()
            D, k, t, D_last = bruteForce(G, s)
            end = time.time()
            print(f"Solution: {D}, {k}")

            # Save work done already
            if path[-3:] == ".in":
                write_output_file(D_last, f'{timeout_fname}/cache/{path[7:-3]}last.out')

            if D is None:
                if path[-3:] == ".in":
                    write_output_file({"NO SOLUTION": 1}, f'{timeout_fname}/{path[7:-3]}-no-sol.out')
                    print(fname, " timed out. No solution found.")
                else:
                    write_output_file(D, f'test/test.out')
                continue

            assert is_valid_solution(D, G, s, k)
            print("Total Happiness: {}".format(calculate_happiness(D, G)))
            print("Solving took {} seconds.".format(end - start))
            if t == -1:
                if path[-3:] == ".in":
                    write_output_file(D, f'{timeout_fname}/{path[7:-3]}.out')
                    print(fname, " timed out.")
                else:
                    write_output_file(D, f'test/test.out')
            else:
                if path[-3:] == ".in":
                    write_output_file(D, f'solved/{path[7:-3]}.out')
                else:
                    write_output_file(D, f'test/test.out')
