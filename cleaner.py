import os
import sys

with open("unfinished_meds.txt") as fp:
    lst = []
    for line in fp:
        fname, rank = line.split()[0], line.split()[1]
        if float(rank) > 90:
            lst.append(fname + ".in")

    for f in os.listdir("shitters"):
        if f not in lst:
            os.remove(os.path.join("shitters", f))
