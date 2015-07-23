#! /usr/bin/env python3

import re 
from collections import namedtuple
Mode = namedtuple('Mode', 'freq qpt vectors')

def import_vsim(filename):
    with open(filename,'r') as f:
        f.readline() # Skip header
        # Read in lattice vectors (2-row format) and cast as floats
        cell_vsim = [[float(x) for x in f.readline().split()],
                     [float(x) for x in f.readline().split()]]
        # Read in all remaining non-commented lines as positions/symbols, commented lines to new array
        positions, symbols, commentlines = [], [], []
        for line in f:
            if line[0] != '#' and line[0] != '\!':
                line = line.split()
                position = [float(x) for x in line[0:3]]
                symbol = line[3]
                positions.append(position)
                symbols.append(symbol)
            else:
                commentlines.append(line.strip())

    # remove comment characters and implement linebreaks (linebreak character \)

    for index, line in enumerate(commentlines):
        while line[-1] == '\\':
            line = line[:-1] + commentlines.pop(index+1)[1:]
        commentlines[index] = line[1:]

    # Import data from commentlines
    vibs = []
    for line in commentlines:
        vector_txt = re.search('qpt=\[(.+)\]',line)
        if vector_txt:
            mode_data = vector_txt.group(1).split(';')
            qpt = [float(x) for x in mode_data[0:3]]
            freq = float(mode_data[3])
            vector_list = [float(x) for x in mode_data[4:]]
            vector_set = [vector_list[6*i:6*i+3] for i in range(len(positions))]
            vibs.append(Mode(freq, qpt, vector_set))
            
    return (cell_vsim, positions, symbols, vibs)

if __name__ == "__main__":
    cell, positions, symbols, vibs = import_vsim('gamma_vibs.ascii')

    print(vibs)
