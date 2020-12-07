from parse import *
import os
from utils import *
import networkx

if __name__ == "__main__":
    filenames = sorted(os.listdir("greedy_outputs"))
    for f in filenames:

        G, s = read_input_file(os.path.join("inputs", f[:-3] + "in"))
        start = read_output_dict(os.path.join("greedy_outputs", f))
        flattened = flatten_dict(start)
        assert is_valid_solution(start, G, s, len(set(start.values())))
        assert is_valid_solution(flattened, G, s, len(set(flattened.values())))
        assert calculate_happiness(start, G) == calculate_happiness(flattened, G)
        write_output_file(flattened, os.path.join("flattened_greedy_outputs", f))
