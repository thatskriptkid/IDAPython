# author: Bauyrzhan Dyussekeyev

# Дампит пейлоды из файлов
# суть - ищет начало пейлода (константная строка), и ищет конец.
# так как определить конец base64 строки нельзя, костыль - поиск строки обычно
# идущей за ней 

import argparse
import base64 
import os
import re

parser = argparse.ArgumentParser(prog = 'exchange payloads dumper', description = 'dump payloads')
parser.add_argument('path', help = 'path to folder with files')

args = parser.parse_args()

def dump_payloads(path):
    try:
        res = ''
        with os.scandir(path) as it:
            for entry in it:
                with open(entry.path, 'rb') as fr:
                    s = fr.read()
                    #start = s.find(b'\x77\x00\x45\x00\x79\x00\x69\x00\x48\x00\x30\x00\x41\x00\x41\x00\x51\x00\x41\x00\x41\x00\x41\x00') # wEyiHkAAQAAAP
                    #start = s.find(b'\x77\x00\x45\x00\x79\x00\x69\x00\x47\x00\x6b\x00\x41\x00\x41\x00\x51\x00\x41\x00\x41\x00\x41\x00\x50\x00') # wEyiGkAAQAAAP
                    #start = s.find(b'\x77\x00\x45\x00\x79\x00\x69\x00\x48\x00\x45\x00\x41\x00\x41\x00\x51\x00\x41\x00\x41\x00\x41\x00\x50\x00') # wEyiHEAAQAAAP
                    #start = s.find(b'\x77\x00\x45\x00\x79\x00\x69\x00\x47\x00\x30\x00\x41\x00\x41\x00\x51\x00\x41\x00\x41\x00\x41\x00\x50\x00') # wEyiG0AAQAAAP
                    #start = s.find(b'\x77\x00\x45\x00\x79\x00\x69\x00\x47\x00\x30\x00\x41\x00\x41\x00\x51\x00\x41\x00\x41\x00\x41\x00\x50\x00') # 
                    #start = s.find(b'\x77\x00\x45\x00\x79\x00\x69\x00\x49\x00\x45\x00\x42\x00\x41\x00\x41\x00\x45\x00\x41\x00\x41\x00\x41\x00\x44\x00') 
                    start = s.find(b'\x77\x00\x45\x00\x79\x00\x69\x00\x49\x00\x55\x00\x42\x00') 
                    #tmp_s = re.search(b'\x2f\x00\x77\x00\x45\x00\x79\x00',s) # \wEy
                    #print(hex(tmp_s.start()))
                    
                    #end = s.find(b'\x00\x2d\x2f\x00\x6f\x00\x77\x00\x61\x00\x2f\x00\x61\x00\x75\x00\x74\x00\x68\x00') # /owa/auth 
                    tmp_s = s[start:]
                    end = tmp_s.find(b'\x00\x00')
                    end = end + start
                    #print(hex(start), hex(end))
                    if start == -1 or end == -1:
                        continue
                    fr.seek(start)
                    payload = fr.read(end - start + 1)
                    
                res = payload.decode('utf-16')

                #res = res.replace('wEyiH0AAQAAAP////8BAAAAAAAAAAwCAAAA', '')
                #res = res.replace('wEyiGkAAQAAAP////8BAAAAAAAAAAwCAAAA', '')    
                #res = res.replace('wEyiHEAAQAAAP////8BAAAAAAAAAAwCAAAA', '')  
                res = res.replace('wEyiIUBAAEAAAD////AQAAAAAAAAAMAgAAA', '')                    
                
                decoded = base64.b64decode(res)

                start = decoded.find(b'\x4d\x5a\x90\x00\x03')

                # убераем весь мусор перед заголовком MZ
                res = decoded[start:]

                with open('result\\' + entry.name + '_dumped.bin', 'wb') as output_file:
                    output_file.write(res)
                    
    except Exception as err:
        raise

dump_payloads(args.path)  