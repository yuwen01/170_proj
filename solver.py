import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness, calculate_stress_for_room, convert_dictionary
import sys, time, os
from bruteforce import bruteForce
from estimator2 import estimate
from enum import enum

class algorithm(enum):
    BRUTEFORCE = 0
    HILL_CLIMING = 1

def solve(G, s):
    """
    Args:
        G: networkx.Graph
        s: stress_budget
    Returns:
        D: Dictionary mapping for student to breakout room r e.g. {0:2, 1:0, 2:1, 3:2}
        k: Number of breakout rooms
        t: Type of algorithm used
    """

    # TODO: your code here!
    return estimate(G, s)


# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

# if __name__ == '__main__':
#     assert len(sys.argv) == 2
#     path = sys.argv[1]
#     G, s = read_input_file(path)
#
#     start = time.time()
#     D, k = solve(G, s)
#     end = time.time()
#
#     assert is_valid_solution(D, G, s, k)
#     print("Total Happiness: {}".format(calculate_happiness(D, G)))
#     print("Solving took {} seconds.".format(end - start))
#     if path[-3:] == ".in":
#         write_output_file(D, f'{path[:-3]}.out')
#     else:
#         write_output_file(D, f'test/test.out')

# For testing a folder of inputs to create a folder of outputs, you can use glob (need to import it)
if __name__ == "__main__":
    timeout_fnames = os.listdir("1sec_timeout_outputs")
    solved_fnames = os.listdir("solved")
    for fname in sorted(os.listdir("inputs/")):
        if "medium" in fname and f'{fname[:-3]}.out' not in timeout_fnames \
                and f'{fname[:-3]}.out' not in solved_fnames:
            print("starting fname: ", fname)
            path = os.path.join("inputs", fname)
            G, s = read_input_file(path)

            start = time.time()
            D, k, t = solve(G, s)
            end = time.time()
            print(f"Solution: {D}, {k}")
            if D is None:
                if path[-3:] == ".in":
                    write_output_file({"NO SOLUTION": 1}, f'1sec_timeout_outputs/{path[7:-3]}-no-sol.out')
                    print(fname, " timed out. No solution found.")
                else:
                    write_output_file(D, f'test/test.out')
                continue

            assert is_valid_solution(D, G, s, k)
            print("Total Happiness: {}".format(calculate_happiness(D, G)))
            print("Solving took {} seconds.".format(end - start))
            if t == -1:
                if path[-3:] == ".in":
                    write_output_file(D, f'1sec_timeout_outputs/{path[7:-3]}.out')
                    print(fname, " timed out.")
                else:
                    write_output_file(D, f'test/test.out')
            else:
                if path[-3:] == ".in":
                    write_output_file(D, f'solved/{path[7:-3]}.out')
                else:
                    write_output_file(D, f'test/test.out')
