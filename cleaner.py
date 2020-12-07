import os
import sys

with open("unfinished_meds.txt") as fp:
    lst = []
    for line in fp:
        fname = line.split()[0]
        lst.append(fname + ".in")

    for f in os.listdir("medium_inputs"):
        if f not in lst:
            os.remove(os.path.join("medium_inputs", f))
