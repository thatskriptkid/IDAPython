
# Удаляет столбцы

import argparse
import os

default_output = os.path.join(os.getcwd(), 'output.txt')
parser = argparse.ArgumentParser(prog = 'clear columns', description = 'delete unnecessary columns in text file')
parser.add_argument('path')
args = parser.parse_args()

try:
    with open(default_output, 'w') as fo:
        with open(args.path, 'r') as fi:
            for l in fi.readlines():
                fo.write(l.split(' ', maxsplit = 2)[2])
                
except Exception as err:
    print(f"{err=}, {type(err)=}")
    raise