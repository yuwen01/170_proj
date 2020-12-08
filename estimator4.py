import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness, calculate_stress_for_room
from findSolution import bruteForce
import os, time, random, math

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
    return simulated_annealing(G, s)


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

    neighbor, isSwap = getBetterNeighbor(G, budget, assignment, numStudents, 0)
    while neighbor:
        student, move, curHappiness = neighbor
        transition(assignment, student, move, isSwap)
        neighbor, isSwap = getBetterNeighbor(G, budget, assignment, numStudents, curHappiness)
    return assignment, len(set(assignment.values())), calculate_happiness(assignment, G)


def simulated_annealing(G, budget, startAssignment=None):
    """
    Simulated Annealing. Similar to hill climbing but it only needs to find a better neighbor instead
    of the best neighbor
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
    neighbor, isSwap = getRandomNeighbor(G, budget, assignment, numStudents)
    while neighbor:
        # iteration += 1
        student, move, newHappiness = neighbor
        temperature *= 0 if temperature < cutoff else decay
        #
        # if iteration % 500 == 0:
        #     print(newHappiness, iteration)

        if temperature > 0:
            # Do simulated annealing

            # delta = -s' - (-s) = s - s' where s is the happiness of the state and
            # the cost function is the negation of the happiness
            delta = curHappiness - newHappiness
            if delta < 0:
                transition(assignment, student, move, isSwap)
                curHappiness = newHappiness
            elif random.uniform(0, 1) < accept_probability(delta, temperature):
                transition(assignment, student, move, isSwap)
                curHappiness = newHappiness
            neighbor, isSwap = getRandomNeighbor(G, budget, assignment, numStudents)
        else:
            # Do local search
            transition(assignment, student, move, isSwap)
            neighbor, isSwap = getBetterNeighbor(G, budget, assignment, numStudents, newHappiness)

    return assignment, len(set(assignment.values())), calculate_happiness(assignment, G)


def transition(D, student, move, isSwap):
    if isSwap:
        D[student], D[move] = D[move], D[student]
    else:
        D[student] = move


def getRandomNeighbor(G, s, D, maxRooms):
    """

    Args:
        G:
        s:
        D:
        maxRooms:

    Returns:
    move, isSwap
    """
    swapFirst = random.uniform(0, 1) < 0.5
    if swapFirst:
        move = getRandomSwap(G, s, D)
        if move is None:
            return getRandomStudentMove(G, s, D, maxRooms), 0
        return move, 1
    else:
        move = getRandomStudentMove(G, s, D, maxRooms)
        if move is None:
            return getRandomSwap(G, s, D), 1
        return move, 0


def getBetterNeighbor(G, s, D, maxRooms, curHappiness):
    """
    
    Args:
        G: 
        s: 
        D: 
        maxRooms: 
        curHappiness: 

    Returns:
    move, isSwap
    """
    swapFirst = random.uniform(0, 1) < 0.5
    if swapFirst:
        move = getBetterSwapAssignment(G, s, D, curHappiness)
        if move is None:
            return getBetterStudentAssignment(G, s, D, maxRooms, curHappiness), 0
        return move, 1
    else:
        move = getBetterStudentAssignment(G, s, D, maxRooms, curHappiness)
        if move is None:
            return getBetterSwapAssignment(G, s, D, curHappiness), 1
        return move, 0


def getRandomStudentMove(G, s, D, maxRooms):
    students = list(range(len(G.nodes)))
    rooms = list(range(maxRooms))
    random.shuffle(students)

    for curStudent in students:
        oldRoom = D[curStudent]
        random.shuffle(rooms)
        for newRoom in rooms:
            D[curStudent] = newRoom
            if is_valid_solution(D, G, s, len(set(D.values()))):
                newHappiness = calculate_happiness(D, G)
                D[curStudent] = oldRoom
                return curStudent, newRoom, newHappiness

        D[curStudent] = oldRoom

    return None


def getRandomSwap(G, s, D):
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
                # print(curHappiness, newHappiness)
                D[curStudent], D[swapStudent] = D[swapStudent], D[curStudent]
                return curStudent, swapStudent, newHappiness
            D[curStudent], D[swapStudent] = D[swapStudent], D[curStudent]

    return None


def getBetterStudentAssignment(G, s, D, maxRooms, curHappiness):
    students = list(range(len(G.nodes)))
    rooms = list(range(maxRooms))
    random.shuffle(students)

    for curStudent in students:
        oldRoom = D[curStudent]
        random.shuffle(rooms)
        for newRoom in rooms:
            D[curStudent] = newRoom
            if is_valid_solution(D, G, s, len(set(D.values()))):
                newHappiness = calculate_happiness(D, G)
                if curHappiness < newHappiness:
                    # print(curHappiness, newHappiness)
                    D[curStudent] = oldRoom
                    return curStudent, newRoom, newHappiness

        D[curStudent] = oldRoom

    return None


def getBetterSwapAssignment(G, s, D, curHappiness):
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

    return None


if __name__ == "__main__":
    repeat = 5
    bruteForceTimeoutInSeconds = 100
    input_dir = "billy2"
    timeout_fname = "submission9"
    timeout_path = f"{timeout_fname}/"
    solved_path = f"{timeout_fname}/"
    for fname in sorted(os.listdir(input_dir), reverse=False):
        isSolved = os.path.isfile(f"{solved_path}{fname[:-3]}.out")
        isComputed = os.path.isfile(f"{timeout_path}{fname[:-3]}.out")
        if "medium" in fname and not isSolved and not isComputed:
            print("Starting fname: ", fname)
            path = os.path.join(input_dir, fname)
            G, s = read_input_file(path)

            start = time.time()
            # Find Starting Assignment
            startAssignment, startRooms, timeout, last = bruteForce(G, s, bruteForceTimeoutInSeconds, None, None)
            cache_output = os.path.join(timeout_path, "cache")
            if startAssignment is None:
                startAssignment = {}
                for s in range(len(G.nodes)):
                    startAssignment[s] = s
                if path[-3:] == ".in":
                    write_output_file(last, os.path.join(cache_output, f"{fname[:-3]}-last.out"))
                else:
                    write_output_file(bestD, f'test/test.out')
            else:
                if path[-3:] == ".in":
                    write_output_file(startAssignment, os.path.join(cache_output, f"{fname[:-3]}.out"))
                else:
                    write_output_file(bestD, f'test/test.out')

            bruteForceEnd = time.time()
            print(f"Brute Force ran in {bruteForceEnd - start} seconds")
            print("Start Assignment: ", startAssignment)

            bestHappiness = -1
            bestD = None
            bestk = None
            for i in range(repeat):
                D, k, curHappiness = simulated_annealing(G, s, startAssignment)
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