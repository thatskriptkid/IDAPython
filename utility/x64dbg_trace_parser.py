

import argparse

# пример скрипта для парсинга трейса x64dbg
# в данном случае скрипт берет инструкции идущие после ret и игнориует call  

parser = argparse.ArgumentParser(prog = 'trace parser', description = 'trace parser')
parser.add_argument('path')
args = parser.parse_args()

path = args.path

fp = False

with open(path, "r") as f:
    with open(path + "_parsed.txt", "w") as fw:
        for l in f:
            if fp and "call" not in l:
                fw.write(l)
                fp = False
            if "ret" in l:
                fp = True