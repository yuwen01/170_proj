from parse import *
import os
from utils import *
import networkx

def compare_outputs(fname):
    '''
    Compares two dictionaries, and outputs the one with more happiness.
    '''
    dirs = ["test_0_outputs", "test_1_outputs", "test_2_outputs",
            "test_3_outputs", "test_4_outputs", "test_5_outputs",
            "greedy_outputs", ]

    G, s = read_input_file(os.path.join("inputs", fname + ".in"))
    evaluation_file = "eval.txt"
    happinesses = []
    for dir in dirs:
        D = read_output_dict(os.path.join(dir, fname + ".out"))
        happinesses.append(calculate_happiness(D, G))

    zipped = [(dirs[i], happinesses[i]) for i in range(len(dirs))]
    zipped.sort(key=lambda x: x[1])
    with open(eval.txt, "w") as fo:
        for z in zipped:
            fo.write(f'dir: {z[0]} happiness: {z[1]}\n')

if __name__ == "__main__":
    compare_outputs("large-1")
