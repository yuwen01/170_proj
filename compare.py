from parse import *
import os
import sys
from utils import *
from shutil import copyfile
import networkx

def compare_outputs(fname, raw_dirs, evaluation_file, dest_dir):
    '''
    Compares two dictionaries in all the folders in dirs. cop
    '''
    G, s = read_input_file(os.path.join("inputs", fname + ".in"))
    happinesses = []
    dirs = []
    for dir in raw_dirs:
        ##print(list(os.listdir(dir)))
        if fname + ".out" in os.listdir(dir):
            D = read_output_dict(os.path.join(dir, fname + ".out"))
            happinesses.append(calculate_happiness(D, G))
            dirs.append(dir)

    if happinesses == []:
        return -1
    zipped = [(dirs[i], happinesses[i]) for i in range(len(dirs))]
    zipped.sort(key=lambda x: -x[1])

    final_dir = "final/"
    with open(evaluation_file, "w") as fo:
        fo.write(fname + "\n\n")
        for z in zipped:
            fo.write(f'dir: {z[0]} happiness: {z[1]}\n')
        fo.write("============================\n\n")
        fo.close()

    print(zipped[0][0])
    copyfile(os.path.join(zipped[0][0], fname + ".out"), os.path.join(dest_dir, fname + ".out"))
    return 0

if __name__ == "__main__":
    dirs = ["outputs", "test_4_outputs", "greedy_outputs"]
    evaluation_file = "summary.txt"
    dest_dir = "final/"
    for fname in os.listdir(dirs[0]):
        if compare_outputs(fname[:-4], dirs, evaluation_file, dest_dir) == -1:
            print('nice file, idiot')
            break
