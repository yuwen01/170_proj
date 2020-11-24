import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness, calculate_stress_for_room
import sys

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
