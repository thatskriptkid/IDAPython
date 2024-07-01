import sys
import zlib
import os

def main():
	analysis_file  = sys.argv[1]
	arr_pl_names = []
	extracted = []
	#Считать первые 256(0x100) байтов: первый байт=len_name(длинна имени), последующие=name_pl(имя файла)
	with open(analysis_file, 'rb') as sysL:
		sysL.seek(8)
		byArr_100 = bytearray(sysL.read(0x100))
		while byArr_100 !=b"":
			len_name = byArr_100[0]+1
			name_pl = byArr_100[1:len_name]
			n_pl = str(name_pl)
			len_pl = bytearray(sysL.read(4))
			len_pl = len_pl[2]*0x10000 + len_pl[1]*0x100 + len_pl[0]
			extracted = bytearray(sysL.read(len_pl))
			if len_pl == 0:
				break
			arr_pl_names.append(n_pl)
			with open('raw_' + n_pl, 'wb') as wf:
				wf.write(bytearray(extracted))
			byArr_100 = bytearray(sysL.read(0x100))
	print(arr_pl_names)
	#Расшифровка пейлоада
	for my_pl in arr_pl_names:
		arr_PL = []
		with open('raw_' + my_pl, 'rb') as f, open('decrypted_' + my_pl, 'wb') as wf:
			arr_PL = bytearray(f.read())
			for x in range(3):
				for i in range(len(arr_PL)-1):
					arr_PL[i] = ((arr_PL[i] ^ 0x78) - arr_PL[i+1]) & 0xFF
				for j in range(len(arr_PL)-1, 0,  -1):
					arr_PL[j] = ((arr_PL[j] ^ 0x79) - arr_PL[j-1]) & 0xFF
				arr_PL[0] = (arr_PL[0] - 0x76) & 0xFF
			wf.write(bytearray(arr_PL))
		with open('decrypted_' + my_pl, 'rb') as f, open(my_pl, 'wb') as wf:
			str_PL = f.read()
            #Распаковать расшифрованный пейлоад, метод: zlib
			decompressed_ =  zlib.decompress(str_PL)
			wf.write(decompressed_)	
		os.remove('raw_' + my_pl)	
		os.remove('decrypted_' + my_pl)
if __name__ == '__main__':
	main()
