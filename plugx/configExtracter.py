import os
import sys
import struct
from functools import partial

'''
usage: python configExtracter.py <DLL_file> <payload> <output_file>
'''

def first_case(payload_name, xor_key, sub_key):
	print('Payload decode:')
	print('xor ' + hex(xor_key) + ' sub ' + hex(sub_key))
	bigTuple = ()
	f = open(payload_name, "rb")
	f.seek(0x13)
	block = f.read(1)
	while block != b"":
		unpacked = struct.unpack("B", block)
		bigTuple = bigTuple + unpacked
		if f.tell() == 0x1937:
			break
		block = f.read(1)
	f.close()
	newArr = len(bigTuple)*[0x0]
	for i in range(0, len(bigTuple)):
		temp = (bigTuple[i] ^ xor_key) - sub_key 
		newArr[i] = temp & 0xFF
	return newArr
	
def second_case(payload_name, add_key, xor_key, sub_key):
	print('Payload decode:')
	print('add ' + hex(add_key) + ' xor ' + hex(xor_key) + ' sub ' + hex(sub_key))
	bigTuple = ()
	f = open(payload_name, "rb")
	f.seek(0x13)
	block = f.read(1)
	while block != b"":
		unpacked = struct.unpack("B", block)
		bigTuple = bigTuple + unpacked
		if f.tell() == 0x1937:
			break
		block = f.read(1)
	f.close()
	newArr = len(bigTuple)*[0x0]
	for i in range(0, len(bigTuple)):
		temp = ((bigTuple[i] + add_key) ^ xor_key) - sub_key
		newArr[i] = temp & 0xFF
	return newArr
	
def main():
	dll_file = sys.argv[1]
	payload_name = sys.argv[2]
	if len(sys.argv) == 4:
		output_file = sys.argv[3]
	else:
		output_file = 'decrypted_config'
	
	#Stage 1: read DLL, determine decode algorithm

	flag_case = 0
	add_key = xor_key = sub_key = 0
	with open(dll_file, 'rb') as f:
		block = f.read(1)
		while block != b"":
			curByte = int.from_bytes( block, "big" )
			if curByte == 0x80:
				curOffset = f.tell()
				block = f.read(2) #F1<xor_key> or 07<add_key>
				n1 = int.from_bytes( block, "little" )
				block = f.read(2) #80E9 or 8037
				n2 = int.from_bytes( block, "big" )
				block = f.read(1) #<sub_key> or <xor_key>
				n3 = int.from_bytes( block, "big" )
				block = f.read(2) #802F
				n4 = int.from_bytes( block, "big" )
				block = f.read(1) #<sub_key>
				n5 = int.from_bytes( block, "big" )
				if ((n1 & 0xFF) == 0xF1) and n2 == 0x80E9:
					flag_case = 1
					xor_key = (n1 >> 8)
					sub_key = n3
				elif ((n1 & 0xFF) == 0x07) and (n2 == 0x8037) and (n4 == 0x802F): 
					flag_case = 2
					add_key = (n1 >> 8)
					xor_key = n3
					sub_key = n5
				else:
					f.seek(curOffset)
						
			block = f.read(1)
	
	
	#Stage 2: Decode payload
	if flag_case == 0:
		print('Could not find decode keys')
		sys.exit()
	if flag_case == 1:
		newArr = first_case(payload_name, xor_key, sub_key)
	if flag_case == 2:
		newArr = second_case(payload_name, add_key, xor_key, sub_key)
	
	#Stage 3: Extracting configs
	key = ((newArr[3]*0x100 + newArr[2])*0x100 + newArr[1])*0x100 + newArr[0]
	print('Config decrypt key: ' + hex(key))
	
	mask = 0xFFFFFFFF
	odin = dva = tri = chet = key
	decrypted = len(newArr)*[0x0]
	for i in range(0, len(newArr)):
		odin = (odin + (odin >> 3) - 0x11111111) & mask
		dva = (dva + (dva >> 5) - 0x22222222) & mask
		tri = (tri + 0x33333333 - (tri << 7)) & mask
		chet = (chet + 0x44444444 - (chet << 9)) & mask		
		decrypted[i] = (newArr[i] ^ (odin + dva + (tri & 0xFF) + (chet & 0xFF))) & 0xFF
	
	dec_f = open(output_file, 'wb')
	for i in decrypted:
		dec_f.write( bytes([i]))
	dec_f.close()
	
	
	print('done')
	
		
		
		
if __name__ == '__main__':
    main()
