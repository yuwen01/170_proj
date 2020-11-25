import re
import os
import sys
import random

import utils

import parse

def generate(n, fname, max_stress=100):
    in_file = open(fname, "w")
    in_file.write(f"{n} \n{max_stress}\n")
    for i in range(n):
        for j in range(i + 1, n):
            h = random.random() * 100
            s = random.random() * 100
            line = f"{i} {j} {h:.3f} {s:.3f}\n"
            in_file.write(line)
    
if __name__ == '__main__': 
    if len(sys.argv) != 4: 
        print("need 3 args: number of students, max stress, and filename to write to")
    generate(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))

    
