import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness, calculate_stress_for_room, calculate_happiness_for_room, convert_dictionary
import sys

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
    return greedy_solution(G, s)

''' the point of this is to get a starting point. Ideally, search radius will decrease over time,
so we don't have such consistent starts. I'm only doing this because I don't know how to randomly 
generate a starting solution that meets stress requirements 

this algorithm sucks ass
'''
def greedy_solution(G, budget, neighborhood=-1, base=None):
    assignment = {0: [0]} # maps rooms to students
    #iterate through every student
    for s in range(1, len(G.nodes)):
        room_lim = budget / len(assignment)
        happinesses = {}
        # iterate through every room.
        # add this student to the room that gives the most happiness without going over the stress limit.
        # if this is impossible, just add another room with this person, and balance. 
        for room, students in assignment.items():
            if calculate_stress_for_room(students + [s], G) < room_lim:
                happinesses[room] = calculate_happiness_for_room(students + [s], G)
        print("ha", happinesses)
        if len(happinesses) == 0:
            print('got here', s)
            assignment[len(assignment)] = [s]
            balance(G, budget, assignment)
        else: 
            currmax = -1
            argmax = -1
            for i, v in happinesses.items():
                if v > currmax:
                    currmax = v
                    argmax = i
            assignment[argmax].append(s)
    print(assignment)
    return convert_dictionary(assignment), len(assignment)
            

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


