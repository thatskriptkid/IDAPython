

import os
import argparse
from os import listdir
from os.path import isfile, join

from dotnetfile import DotNetPE

'''
https://github.com/pan-unit42/dotnetfile
https://pan-unit42.github.io/dotnetfile/
https://unit42.paloaltonetworks.com/dotnetfile/
'''
default_output = join(os.getcwd(), 'output.txt')

parser = argparse.ArgumentParser(prog='dotnetfile_dump.py', description='Show .NET header information of assembly.')
parser.add_argument(dest='input_file', type=str, help='Absolute file path of .NET assembly. or dir')
parser.add_argument('-d', action='store_true', help = 'directory')
parser.add_argument('-o', '--output_filename', help = 'output filename')
args = parser.parse_args()

output = default_output

def process_dir(path):
    for file_path in listdir(path):
        # check if current file_path is a file
        full_path = os.path.join(path, file_path)
        if isfile(full_path):
                process_file(full_path)
        
def process_file(path):
    with open(output, 'a') as fo:
        dotnet_file = DotNetPE(path)
        
        available_tables = dotnet_file.existent_metadata_tables()
        
        if 'TypeRef' in available_tables:
            type_ref = dotnet_file.TypeRef.get_typeref_hash(dotnet_file.Type.Hash.SHA256, False, True)
            fo.write(path + '\n')
            fo.write(type_ref + '\n')
    
def main():
    try:
        if args.output_filename:
            global output
            output = args.output_filename
        if args.d:
            process_dir(args.input_file)
        else:
            if not os.path.isabs(args.input_file):
                print('[-] Please provide absolute file path of .NET assembly.')
                return
            process_file(args.input_file)
            
    except Exception as err:
        print(f"{err=}, {type(err)=}")
        raise
    finally:
        print('\nProcessing done\n')

if __name__ == '__main__':
    main()
