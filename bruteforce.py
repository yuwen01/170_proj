import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness, calculate_stress_for_room
import time, copy

def bruteForce(G, s):
    bruteForce(G, s, 0)

def bruteForce(G, s, timeoutInSeconds):
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
    bestScore = -1
    start = time.time()
    curAssignment = {}

    def dfs(curAssignment, numAssigned, numRooms):
        nonlocal bestAssignment, bestNumRooms, bestScore
        # End early if timed out and return best solution
        if timeoutInSeconds and time.time() > start + timeoutInSeconds:
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
