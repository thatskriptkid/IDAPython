import os
import sys
import struct
import lznt1
#usage: plugx_pe_reconstructor.py <PLugX Payload File>
MASK = 0xFFFFFFFF

def lil_end_l(e_struct):
	return struct.unpack("<l", e_struct)[0] & MASK

def lil_end_h(e_struct):
	return struct.unpack("<h", e_struct)[0] & 0xFFFF
	
def w_lil_end_l(w_bytes):
	return struct.pack("<L", w_bytes)

def w_lil_end_h(w_bytes):
	return struct.pack("<h", w_bytes)
	
#--START PL RECONSTRUCTOR--
def pl_reconstructor(sample_pe, addr_arr):
	addr_e_lfanew = addr_arr[0]
	addr_dwVirtualAddress = addr_arr[1]
	addr_dwRawSize = addr_arr[2]
	addr_wNumberOfSections = addr_arr[3]
	addr_SectionAlignment = addr_arr[4]
	addr_SizeOfImage = addr_arr[5]
	addr_SizeOfHeaders = addr_arr[6]
	addr_dwAddressOfEntryPoint = addr_arr[7]
	with  open(sample_pe, 'rb') as pl_rf, open("pe_" + sample_pe, 'rb') as pe_rf, open("reconstructed_" + sample_pe, "wb") as wf:
		temp = bytearray(pe_rf.read())
		wf.write(bytearray(temp))
		temp = bytearray(pl_rf.read())
		wf.seek(0)
		#create MZ
		mz_header = 0x5A4D
		pe_header = 0x4550
		wf.write(w_lil_end_h(mz_header))
		#--start e_lfanew
		pl_rf.seek(addr_e_lfanew)
		pe_rf.seek(0x3C)
		wf.seek(0x3C)
		e_lfanew_const = lil_end_l(pl_rf.read(4))
		e_lfanew = lil_end_l(pe_rf.read(4))
		e_lfanew = (e_lfanew + e_lfanew_const) & MASK
		wf.write(w_lil_end_l(e_lfanew))
		#--end e_lfanew
		#add PE
		wf.seek(e_lfanew)
		wf.write(w_lil_end_h(pe_header))
		#--start wNumberOfSections
		pl_rf.seek(addr_wNumberOfSections)
		pe_rf.seek(e_lfanew + 6)
		wf.seek(e_lfanew + 6)
		wNumberOfSections_const = lil_end_h(pl_rf.read(2))
		wNumberOfSections = lil_end_h(pe_rf.read(2))
		wNumberOfSections = (wNumberOfSections - wNumberOfSections_const) & 0xFFFF
		wf.write(w_lil_end_h(wNumberOfSections))
		#--start SizeOfOptionalHeader
		pe_rf.seek(e_lfanew + 0x14)
		SizeOfOptionalHeader = lil_end_h(pe_rf.read(2))
		#--start SectionAlignment
		pl_rf.seek(addr_SectionAlignment)
		pe_rf.seek(e_lfanew + 0x38)
		wf.seek(e_lfanew + 0x38)
		SectionAlignment_const = lil_end_l(pl_rf.read(4))
		SectionAlignment = lil_end_l(pe_rf.read(4))
		SectionAlignment = (SectionAlignment - SectionAlignment_const) & MASK
		wf.write(w_lil_end_l(SectionAlignment))
		#--start SizeOfImage
		pl_rf.seek(addr_SizeOfImage)
		pe_rf.seek(e_lfanew + 0x50)
		wf.seek(e_lfanew + 0x50)
		SizeOfImage_const = lil_end_l(pl_rf.read(4))
		SizeOfImage = lil_end_l(pe_rf.read(4))
		SizeOfImage = (SizeOfImage + SizeOfImage_const) & MASK
		wf.write(w_lil_end_l(SizeOfImage))
		#--start SizeOfHeaders
		pl_rf.seek(addr_SizeOfHeaders)
		pe_rf.seek(e_lfanew + 0x54)
		wf.seek(e_lfanew + 0x54)
		SizeOfHeaders_const = lil_end_l(pl_rf.read(4))
		SizeOfHeaders = lil_end_l(pe_rf.read(4))
		SizeOfHeaders = (SizeOfHeaders - SizeOfHeaders_const) & MASK
		wf.write(w_lil_end_l(SizeOfHeaders))
		sections_start = e_lfanew + SizeOfOptionalHeader + 0x18
		#Section AddressOfEntryPoint
		pl_rf.seek(addr_dwAddressOfEntryPoint)
		pe_rf.seek(e_lfanew+0x28)
		wf.seek(e_lfanew+0x28)
		dwAddressOfEntryPoint_const = lil_end_l(pl_rf.read(4))
		dwAddressOfEntryPoint = (lil_end_l(pe_rf.read(4)) + dwAddressOfEntryPoint_const) & MASK
		wf.write(w_lil_end_l(dwAddressOfEntryPoint))	
		#--START SECTIONS
		#get const values
		pl_rf.seek(addr_dwVirtualAddress)
		dwVirtualAddress_const = lil_end_l(pl_rf.read(4))
		pl_rf.seek(addr_dwRawSize)
		dwRawSize_const = lil_end_l(pl_rf.read(4))
		for section in range(0, wNumberOfSections):
			pe_rf.seek(sections_start + 0xC)
			wf.seek(sections_start + 0xC)
			dwVirtualAddress = (lil_end_l(pe_rf.read(4)) + dwVirtualAddress_const) & MASK
			dwRawSize = (lil_end_l(pe_rf.read(4)) - dwRawSize_const) & MASK
			#--set new pe
			wf.write(w_lil_end_l(dwVirtualAddress))
			wf.write(w_lil_end_l(dwRawSize))
			sections_start = sections_start + 0x28
		#--END SECTIONS
#--END PL RECONSTRUCTOR--
	
	
def main():
	mask  = 0xFF
	payload_name = sys.argv[1]
	key_string = []
	key_arr = [0x0]*0x100
	addr_arr = [0x0]*8
	isBroken = False
	with open(payload_name, "rb") as key_pl:
		n1 = bytearray(key_pl.read())
		c = 0
		key_patch_byte = key_patch_location = 0
		for i in range(0, len(n1) - 0x10):
			if n1[i] == 0xC6 and n1[i+1] == 0x45:
				key_string.append(n1[i+3])
				c = c + 1
				if (n1[i+4] != 0xC6):
					if c > 0x10:
						break
					else:
						c = 0
						key_string = []
				i = i + 2
		for i in range(0, len(n1)-0xA):
			x = n1[i]
			y = i+5
			for j in range(1, 5):
				x = x << 8
				x = x + n1[i+j]
			if n1[i] == 0xC6 and n1[i+1] == 0x44 and n1[i+2] == 0x05:
				key_patch_byte = n1[i+4]
				key_patch_location = n1[i-1]
			if x == 0x55088D840A:
				addr_arr[0] = y 
			if x == 0x55EC8D840A:
				addr_arr[1] = y
			if x == 0x8b511081EA:
				addr_arr[2] = y
			if x == 0xB7480681E9:
				addr_arr[3] = y
			if x == 0x8B513881EA:
				addr_arr[4] = y
			if x == 0x8B485081C1:
				addr_arr[5] = y
			if x == 0xF48B42542D:
				addr_arr[6] = y 
			if x == 0x45F88D8C10:
				addr_arr[7] = y 
			if x == 0xCCCCCCCCCC:
				pl_start = y
	key_string = key_string[:-1]
	if key_patch_byte != 0:
		key_string[key_patch_location] = key_patch_byte
	T1 = T2 = 0
	for k in range(0, len(key_arr)):
		key_arr[k] = k
	for j in range(0, len(key_arr)):
		T2 = (T2 + key_arr[j] + key_string[T1]) & mask
		T3 = key_arr[j]
		key_arr[j] = key_arr[T2]
		key_arr[T2] = T3
		T1 = (T1 + 1) % len(key_string)
	
	with open(payload_name, "rb") as rf, open("pe_"+payload_name, "wb") as wf:
		rf.seek(pl_start+4)
		unpacked_fileSize = lil_end_l(rf.read(4))
		pl = bytearray(rf.read())
		T1 = T2 = T3 = T4 = 0
		for i in range(0, len(pl)):
			T1 = (T1 + 1) & mask
			T2 = (T2 + key_arr[T1]) & mask
			T3 = key_arr[T1]
			key_arr[T1] = key_arr[T2]
			key_arr[T2] = T3
			T4 = (key_arr[T2] + key_arr[T1]) & mask
			pl[i] = (pl[i] ^ key_arr[T4])
		#Decompress payload using LZNT1 algorithm(API:RtlDecompressBuffer)
		wf.write(lznt1.decompress(bytearray(pl)))
		wf.truncate(unpacked_fileSize)
	with open("pe_"+payload_name, "rb") as rf:
		MZ = bytearray(rf.read(2))
		if MZ != "MZ":
			isBroken = True
	if(isBroken):
		pl_reconstructor(payload_name, addr_arr)
	
if __name__ == '__main__':
    main()
