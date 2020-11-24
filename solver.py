import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness, calculate_stress_for_room
import sys


def solve(G, s):
    """
    Args:
        G: networkx.Graph
        s: stress_budget
    Returns:
        D: Dictionary mapping for student to breakout room r e.g. {0:2, 1:0, 2:1, 3:2}
        k: Number of breakout rooms
    """

    #TODO: your code here!
    return bruteForce(G, s)


def bruteForce(G, s):
    numStudents = len(G.nodes)

    bestAssignment = None
    bestNumRooms = -1
    bestScore = -1

    curAssignment = {}

    def dfs(curAssignment, numAssigned, numRooms):
        nonlocal bestAssignment, bestNumRooms, bestScore
        # Ignore assignments with more than "numStudents" rooms.
        if numRooms >= numStudents:
            return

        # If all students are assigned check if assignment is better
        if numAssigned >= numStudents:
            curScore = calculate_happiness(curAssignment, G)
            if curScore > bestScore:
                bestAssignment = curAssignment.copy()
                bestNumRooms = numRooms
                bestScore = curScore
            return

        # Go through all possible room assignments for the next student
        for room in range(numRooms + 1):
            curAssignment[numAssigned] = room
            newNumRooms = max(numRooms, room + 1)

            # # Check if assignment is valid so far
            # roomAssignments = {}
            # for i in range(numAssigned + 1):
            #     curRoom = curAssignment[i]
            #     if curRoom not in roomAssignments:
            #         roomAssignments[curRoom] = [i]
            #     else:
            #         roomAssignments[curRoom].append(i)
            #
            # maxRoomStress = s / newNumRooms
            # isValid = True
            # print(roomAssignments)
            # for breakoutRoom in roomAssignments:
            #     isValid &= maxRoomStress < calculate_stress_for_room(breakoutRoom, G)

            if is_valid_solution(curAssignment, G, s, newNumRooms):
                dfs(curAssignment, numAssigned + 1, newNumRooms)

        del curAssignment[numAssigned]

    dfs(curAssignment, 0, 0)
    return bestAssignment, bestNumRooms

# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

if __name__ == '__main__':
    assert len(sys.argv) == 2
    path = sys.argv[1]
    G, s = read_input_file(path)
    D, k = solve(G, s)
    assert is_valid_solution(D, G, s, k)
    print("Total Happiness: {}".format(calculate_happiness(D, G)))
    write_output_file(D, 'test/test.out')


# For testing a folder of inputs to create a folder of outputs, you can use glob (need to import it)
# if __name__ == '__main__':
#     inputs = glob.glob('file_path/inputs/*')
#     for input_path in inputs:
#         output_path = 'file_path/outputs/' + basename(normpath(input_path))[:-3] + '.out'
#         G, s = read_input_file(input_path, 100)
#         D, k = solve(G, s)
#         assert is_valid_solution(D, G, s, k)
#         cost_t = calculate_happiness(T)
#         write_output_file(D, output_path)
