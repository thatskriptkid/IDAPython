

import sys
import os

in_file = "путь map файл"
out_file = "путь idc файл"

def map2idc(in_file, out_file ):
    with open(out_file, 'w') as fout:
        fout.write('#include <IDC.IDC>\n ')
        fout.write('static main()\n{\n ')
        with open(in_file) as fin:
            for line in fin:
                print(line)
                List = line.split()
                fout.write('\tMakeName(0x%s, "%s");\n' % (List[0], List[1]))
        fout.write('}\n')

def main():
    map2idc(in_file, out_file)

if __name__ == "__main__":
    main()