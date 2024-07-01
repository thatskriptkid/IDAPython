


import idautils

decrypt_func_addr = 0x002B14D0
txt_filename = ".\\lib_hashes_final_aligned.txt"

def get_hashes_from_push():
    # идет по всем функциям где вызывается импорт API по хэшу
    hashes_from_push = {}
    for addr in CodeRefsTo(decrypt_func_addr,0):
        # находим самый верхний пуш от вызова функции
        call_addr = addr
        while(idc.generate_disasm_line(idc.prev_head(addr),1).find('push')!=-1):
            addr=idc.prev_head(addr)
        hashes_from_push[call_addr] = hex(get_operand_value(addr,0))
    return hashes_from_push


    
def parse_lib_hashes():
    with open(txt_filename, "r") as f:
        lines = f.readlines()
        lib_hashes = [tuple(line.strip().split()) for line in lines]
        return lib_hashes
        
def rename_imports():
    hashes_from_push = get_hashes_from_push()
    lib_hashes = dict(parse_lib_hashes())
    
    for call_addr, value in hashes_from_push.items():
        value_up = value[2:].upper()
        if value_up in lib_hashes:
            print('addr = %s lib_hashes[%s] = %s' % (hex(call_addr), value_up, lib_hashes[value_up]))
            # Set comment on calls
            set_cmt(call_addr, lib_hashes[value_up], False)
            # Rename dword to apiname
            # We take next instruction, and then take address of dword
            ea_dword = (get_operand_value(idc.next_head(call_addr), 0))
            ida_name.set_name(ea_dword, lib_hashes[value_up] + "_" + str(ea_dword), SN_CHECK)
            
'''
6F686                 mov     dword ptr [ebp+var_18], 559C5585h <------------- THIS
.text:73E6F68D                 mov     [ebp+var_14], 5538558Ah
.text:73E6F694                 mov     [ebp+var_10], 551F552Dh
.text:73E6F69B                 mov     [ebp+var_C], 558D552Dh
.text:73E6F6A2                 mov     [ebp+var_8], 55555570h
.text:73E6F6A9                 mov     [ebp+var_4], 5555h
'''
def swap32(x):
    return int.from_bytes(x.to_bytes(4, byteorder='little'), byteorder='big', signed=False)

'''
Справляется со следюущим случаем. Обратите внимание, строки 10003315 и 1000331B
содержат не 4 байта, поэтому значения берутся как 50000000 и 0dff2ffff. Соответственно,
мы должны убрать ff и 00

seg000:100032FD                 push    0Fh
seg000:100032FF                 push    eax
seg000:10003300                 mov     [ebp+var_58], 80E4F197h
seg000:10003307                 mov     [ebp+var_54], 0E1F4DFDEh
seg000:1000330E                 mov     [ebp+var_50], 0FA95E4F3h
seg000:10003315                 mov     [ebp+var_4C], 0DFF2h
seg000:1000331B                 mov     [ebp+var_4A], 50h ; 'P'
seg000:1000331F                 call    strdecode_1000C272
'''
def decrypt_stack_str_mobpopup(ea, rounds):
    r = ''
    for x in range(rounds):
        op = get_operand_value(ea,1)
        op_str = hex(swap32(op))[2:]
        n_byte = 0
        j = 0
        for i in range(4):
            # Костыль. Если придумаете лучше, то дай бог
            if (op_str[j] == '0' and op_str[j+1] == '0') or (op_str[j] == 'f' and op_str[j + 1] == 'f'):
                j += 2
                continue
               
            digit = op_str[j] + op_str[j+1]
            n_byte = int(digit, 16)
            n_byte -= 0x3d
            n_byte &= 0xff # Не забываем эту операцию, нам надо все приравнивать к 1 байту
            n_byte ^= 0xb2
            n_byte &= 0xff
            n_byte += 0x5f
            n_byte &= 0xff
            if n_byte > 0:
                r += chr(n_byte)
            j += 2
        ea = idc.next_head(ea)
    return r

def decrypt_stack_str(ea, rounds):
    r = ''
    for x in range(rounds):
        op = get_operand_value(ea,1)
        op_str = hex(swap32(op))[2:]
        n_byte = 0
        j = 0
        for i in range(4):
            digit = op_str[j] + op_str[j+1]
            n_byte = int(digit, 16)
            n_byte += 0x22
            n_byte ^= 0x33
            n_byte -= 0x44
            if n_byte > 0:
                r += chr(n_byte)
            j += 2
        ea = idc.next_head(ea)
    print(r)

#widechar
def decrypt_stack_str_v2(ea, rounds):
    r = ''
    for x in range(rounds):
        op = get_operand_value(ea,1)
        op_str = hex(swap32(op))[2:]
        n_byte = 0
        j = 0
        #print(op_str)
        for i in range(4):
            digit = op_str[j] + op_str[j+1]
            
            n_byte = int(digit, 16)
            n_byte += 0xc3
            n_byte &= 0xff # take only 1 byte. example 0x80 + 0xc3 = 0x143, we should take 1 byte only (0x43)
            n_byte ^= 0xb2
            n_byte &= 0xff
            n_byte -= 0xa1
            n_byte &= 0xff
            if n_byte > 0:
                r += chr(n_byte)
            #print(r)
            j += 2
        ea = idc.next_head(ea)
    print(r)

def decrypt_stack_str_v2_2(ea, rounds):
    r = ''
    for x in range(rounds):
        op = get_operand_value(ea,1)
        op_str = hex(swap32(op))[2:]
        n_byte = 0
        j = 0
        #print(op_str)
        for i in range(4):
            digit = op_str[j] + op_str[j+1]
            
            n_byte = int(digit, 16)
            n_byte -= 0x3d
            n_byte &= 0xff # take only 1 byte. example 0x80 + 0xc3 = 0x143, we should take 1 byte only (0x43)
            n_byte ^= 0xb2
            n_byte &= 0xff
            n_byte += 0x5f
            n_byte &= 0xff
            if n_byte > 0:
                r += chr(n_byte)
            #print(r)
            j += 2
        ea = idc.next_head(ea)
    return r
    
# convert x64dbg addr -> IDA static addr
# example: trans_addr(0x002B2B60, 0x2b0000, 0x73E60000)
def trans_addr(x64dbg_addr, x64dbg_img_base, ida_img_base):
    rva = x64dbg_addr - x64dbg_img_base
    ida_addr = ida_img_base + rva
    idaapi.jumpto(ida_addr)

#from learn 8
def get_api_hash():
    name = "LoadLibrary"
    hash_val = 0

    for i, c in enumerate(name):
       if i & 1:
           v6 = (~(ord(c) ^ (hash_val >> 5) ^ (hash_val << 11))) & 0xffffffff
       else:
           v6 = (ord(c) ^ (hash_val >> 3) ^ (hash_val << 7)) & 0xffffffff
       hash_val ^= v6

    hash_val = hash_val & 0x7fffffff
    print(hex(hash_val))
    
# DEED
ROL2 = lambda val, r_bits, max_bits=8: \
    (val << r_bits%max_bits) & (2**max_bits-1) | \
    ((val & (2**max_bits-1)) >> (max_bits-(r_bits%max_bits)))
 
# Rotate right. Set max_bits to 8.
ROR2 = lambda val, r_bits, max_bits=8: \
    ((val & (2**max_bits-1)) >> r_bits%max_bits) | \
    (val << (max_bits-(r_bits%max_bits)) & (2**max_bits-1))
    
    
def deed_decrypt_data(crypted_str_ea):
    # 30 - это достаточная длина для имени любой функции
    # можно любое число использовать
    # & 0xff - это необходимо, чтобы превращать числа в 1 байтные и 
    # только тогда вся арифметика будет правильной
    crypted_data = list(get_bytes(crypted_str_ea, 0x100))
    #print(crypted_data)
    plain_data = ''
    v3 = crypted_data[0]
    v8 = v3 & 0xff
    for i in range(0, 30):
        v7 = crypted_data[i+1] & 0xff
        v5 = ROL2(v3, 3)
        t = (v3 ^ v7) & 0xff
        t &= 0xff
        if t == 0:
            break
        plain_data += chr(t)
        #print('v3 = %s, v5 (after ROL) = %s, v7 = %s, plain_data[i] = %s' % (hex(v3), hex(v5), hex(v7),chr(plain_data[i])))
        v3 = ((v3 * v3 + v5 * v5) ^ ROR2(v3 * v5, 3)) + v8
        v3 &= 0xff
        v8 = v3 & 0xff
    return plain_data
    #print(plain_data)

def deed_decrypt_data_big(crypted_str_ea):
    # 0x322 длина всего конфига
    # можно любое число использовать
    # & 0xff - это необходимо, чтобы превращать числа в 1 байтные и 
    # только тогда вся арифметика будет правильной
    crypted_data = list(get_bytes(crypted_str_ea, 0x322))
    #print(crypted_data)
    plain_data = ''
    v3 = crypted_data[0]
    v8 = v3 & 0xff
    for i in range(0, 0x322):
        v7 = crypted_data[i+1] & 0xff
        if v7 == 0:
            print(plain_data)
            crypted_str_ea = crypted_str_ea + i
            crypted_str_ea += 2
            deed_decrypt_data_big(crypted_str_ea)
            break
        v5 = ROL2(v3, 3)
        t = (v3 ^ v7) & 0xff
        t &= 0xff
        plain_data += chr(t)
        #print('v3 = %s, v5 (after ROL) = %s, v7 = %s, plain_data[i] = %s' % (hex(v3), hex(v5), hex(v7),chr(plain_data[i])))
        v3 = ((v3 * v3 + v5 * v5) ^ ROR2(v3 * v5, 3)) + v8
        v3 &= 0xff
        v8 = v3 & 0xff
    return plain_data
    #print(plain_data)
    
# пример вызова
# deed_decrypt_data_custom("DD 43 CD 4B BA D0 6E E4 E7 07 01 00 04 00 0C 00")
def deed_decrypt_data_custom(crypted_str):
    crypted_data = list(crypted_str.split(' '))
    #print(crypted_data)
    plain_data = ''
    v3 = int(crypted_data[0], 16)
    v8 = v3 & 0xff
    for i in range(0, len(crypted_data)-1):
        v7 = int(crypted_data[i+1], 16) & 0xff
        v5 = ROL2(v3, 3)
        t = (v3 ^ v7) & 0xff
        t &= 0xff
        if t == 0:
            break
        plain_data += chr(t)
        #print('v3 = %s, v5 (after ROL) = %s, v7 = %s, plain_data[i] = %s' % (hex(v3), hex(v5), hex(v7),chr(plain_data[i])))
        v3 = ((v3 * v3 + v5 * v5) ^ ROR2(v3 * v5, 3)) + v8
        v3 &= 0xff
        v8 = v3 & 0xff
    return plain_data
    #print(plain_data)
    
def deed_decrypt_data_len(crypted_str_ea, blob_len):
    # 30 - это достаточная длина для имени любой функции
    # можно любое число использовать
    # & 0xff - это необходимо, чтобы превращать числа в 1 байтные и 
    # только тогда вся арифметика будет правильной
    crypted_data = list(get_bytes(crypted_str_ea, blob_len))
    plain_data = ''
    v3 = crypted_data[0]
    v8 = v3 & 0xff
    for i in range(0, blob_len):
        v7 = crypted_data[i+1] & 0xff
        v5 = ROL2(v3, 3)
        t = (v3 ^ v7) & 0xff
        t &= 0xff
        if t == 0:
            break
        plain_data += chr(t)
        #print('v3 = %s, v5 (after ROL) = %s, v7 = %s, plain_data[i] = %s' % (hex(v3), hex(v5), hex(v7),chr(plain_data[i])))
        v3 = ((v3 * v3 + v5 * v5) ^ ROR2(v3 * v5, 3)) + v8
        v3 &= 0xff
        v8 = v3 & 0xff
    return plain_data
    #print(plain_data)
    
# ea_wrap_func = 001D0DBC
'''
edx - адрес начала зашифрованной строки. mov edx может находится где угодно сверху
mov     edx, 1D76B4h
mov     ecx, 1D7D70h
call    get_proc_addr_sub_1D0DBC

если в регистры кладется dword, функция все равно будет работать корректно
#netSocket:001A2263                 mov     edx, offset dword_1AA45C
#netSocket:001A2268                 mov     ecx, offset dword_1AABBC
#netSocket:001A226D                 call    sub_1A2140

get_operand_value(dword_1AA45C) вернет 0x1AA45C
'''
def deed_rename_imports(ea_wrap_func):
    for addr in CodeRefsTo(ea_wrap_func,0):
        #print('xref addr = %s' % hex(addr))
        call_addr = addr
        addr=idc.prev_head(addr)
        while get_operand_value(addr,0) != 0x2:  # лайфхак - сам регистр edx равен 0x2 (незнаю почему)
            addr = idc.prev_head(addr)
        crypted_str_ea = get_operand_value(addr, 1)
        
        plain_str = deed_decrypt_data(crypted_str_ea)
        print('addr = %s, str = %s' % (hex(call_addr), plain_str))
        
        #set_cmt(call_addr, plain_str, False)
        setCommentToDecompilation(plain_str, call_addr)
        #ida_name.set_name(ea_dword, lib_hashes[value_up] + "_" + str(ea_dword), SN_CHECK)
        #break
        #print('second mov addr = %s, edx_val = %s' % (hex(addr), hex(edx_val)))





def setCommentToDecompilation(comment, address):
    #Works in IDA 6.9 - May not work in IDA 7
    #see https://www.hex-rays.com/products/decompiler/manual/sdk/hexrays_8hpp_source.shtml used structures, const and functions
    try:
        cfunc = idaapi.decompile(address)
        
        #get the line of the decompilation for this address
        
        eamap = cfunc.get_eamap()
        decompObjAddr = eamap[address][0].ea

        #get a ctree location object to place a comment there
        tl = idaapi.treeloc_t()
        tl.ea = decompObjAddr
        
        commentSet = False
        #since the public documentation on IDAs APIs is crap and I don't know any other way, we have to brute force the item preciser
        #we do this by setting the comments with different idaapi.ITP_* types until our comment does not create an orphaned comment
        for itp in range(idaapi.ITP_SEMI, idaapi.ITP_COLON):
            tl.itp = itp    
            cfunc.set_user_cmt(tl, comment)
            cfunc.save_user_cmts()
            #apparently you have to cast cfunc to a string, to make it update itself
            unused = cfunc.__str__()
            if not cfunc.has_orphan_cmts():
                commentSet = True
                cfunc.save_user_cmts()
                break
            cfunc.del_orphan_cmts()
    except:
        pass

#/DEED

# mscoree
'''
example
000000000037C000  000007FEFEC14590  .EÁþþ...  advapi32.RegOpenCurrentUser
000000000037C008  000007FEFEC70FC0  À.Çþþ...  "L‹ЬHѓмhH‹„$А"
000000000037C010  000007FEFEC1A7E0  à§Áþþ...  advapi32.CloseServiceHandle
000000000037C018  000007FEFEC3A4C0  À¤Ãþþ...  "L‹ЬHѓмxH‹„$а"
000000000037C020  000007FEFEC249EC  ìIÂþþ...  advapi32.DeleteService
000000000037C028  000007FEFEC104D8  Ø.Áþþ...  advapi32.CryptReleaseContext
000000000037C030  000007FEFEC0AC1C  .¬Àþþ...  advapi32.CryptAcquireContextA
000000000037C038  000007FEFEC10400  ..Áþþ...  advapi32.CryptGenRandom
'''

def pars_api_list(fp):
    with open(fp, 'r', encoding='UTF-8') as _fp:
        for line in _fp:
            qword_addr = int(line.split()[0], 16)
            func_name = (line.split()[3]).split('.')[1]
            print(func_name)

def mscoree_rename_imports(api_list_filepath):
    with open(api_list_filepath, 'r', encoding='UTF-8') as _fp:
        for line in _fp:
            qword_addr = int(line.split()[0], 16)
            func_name = (line.split()[3]).split('.')[1]
            old_name = ida_name.get_name(qword_addr)
            ida_name.set_name(qword_addr, func_name + "_" + old_name, SN_CHECK)

#/mscoree      


# advsql case (aspack)

# Расшифровка строк и установка комментариев на функции вида
# seg000:1000BE17                 push    32h ; '2'
# seg000:1000BE19                 push    eax
# seg000:1000BE1A                 mov     dword ptr [ebp+Format], 508C508Ch
# seg000:1000BE21                 mov     [ebp+var_44], 508C50BAh
# seg000:1000BE28                 mov     [ebp+var_40], 50955080h
# seg000:1000BE2F                 mov     [ebp+var_3C], 50915080h
# seg000:1000BE36                 mov     [ebp+var_38], 507E508Ch
# seg000:1000BE3D                 mov     [ebp+var_34], 509A5081h
# seg000:1000BE44                 mov     [ebp+var_30], 508D50EFh
# seg000:1000BE4B                 mov     [ebp+var_2C], 50EF5083h
# seg000:1000BE52                 mov     [ebp+var_28], 50835081h
# seg000:1000BE59                 mov     [ebp+var_24], 507E5091h
# seg000:1000BE60                 mov     [ebp+var_20], 50B150B8h
# seg000:1000BE67                 mov     [ebp+var_1C], 50B550F4h
# seg000:1000BE6E                 mov     [ebp+var_18], 5050h
# seg000:1000BE74                 call    decrypt_str_1000C272
#
# количество итераций равно длина строки разделить на 4 без остатка

def advsql_print_strings(ea_decrypt_func):
    ea_stack_str = 0x0
    flag = 0
    stack_str_rounds = 0
    for addr in CodeRefsTo(ea_decrypt_func, 0):
        call_addr = addr
        addr = idc.prev_head(addr)
        # проходимся снизу вверх по первого пуша
        while(idc.generate_disasm_line(addr,1).find('push') == -1): # пока инстуркция не push
            # seg000:100021DD                 mov     [ebp+var_E4], ebx
            # seg000:100021E3                 mov     [ebp+var_DC], esi
            # seg000:100021E9                 mov     dword ptr [ebp+Format], 508C508Ch
            # seg000:100021F0                 mov     [ebp+var_44], 508C50BAh
            #print('check addr' , hex(addr))
            if get_operand_value(addr, 1) > 0x10: # этот костыл ьнеобходим, так как помимо значений на стеке может быть типа mov X, EBX и т.д.
                ea_stack_str = addr
                flag = 1
                stack_str_rounds += 1
            addr = idc.prev_head(addr)
            
        if not flag:
            ea_stack_str = addr
        #прыгаем еще на две инстуркции вверх
        addr=idc.prev_head(idc.prev_head(addr))
        #print(hex(call_addr), hex(stack_str_rounds), hex(ea_stack_str))
        plain_str = decrypt_stack_str_v2_2(ea_stack_str, stack_str_rounds)
        if plain_str != '':
            print(hex(call_addr), plain_str)
        
        ea_stack_str = 0
        stack_str_rounds = 0
        flag = 0
        
def advsql_rename_imports(ea_decrypt_func):
    ea_stack_str = 0x0
    flag = 0
    stack_str_rounds = 0
    for addr in CodeRefsTo(ea_decrypt_func, 0):
        call_addr = addr
        addr = idc.prev_head(addr)
        # проходимся снизу вверх по первого пуша
        while(idc.generate_disasm_line(addr,1).find('push') == -1): # пока инстуркция не push
            # seg000:100021DD                 mov     [ebp+var_E4], ebx
            # seg000:100021E3                 mov     [ebp+var_DC], esi
            # seg000:100021E9                 mov     dword ptr [ebp+Format], 508C508Ch
            # seg000:100021F0                 mov     [ebp+var_44], 508C50BAh
            #print('check addr' , hex(addr))
            if get_operand_value(addr, 1) > 0x10: # этот костыл ьнеобходим, так как помимо значений на стеке может быть типа mov X, EBX и т.д.
                ea_stack_str = addr
                flag = 1
                stack_str_rounds += 1
            addr = idc.prev_head(addr)
            
        if not flag:
            ea_stack_str = addr
        #прыгаем еще на две инстуркции вверх
        addr=idc.prev_head(idc.prev_head(addr))
        #print(hex(call_addr), hex(stack_str_rounds), hex(ea_stack_str))
        plain_str = decrypt_stack_str_v2_2(ea_stack_str, stack_str_rounds)
        
        if plain_str == '':
            print(hex(call_addr))
        setCommentToDecompilation(plain_str, call_addr)
        
        ea_stack_str = 0
        stack_str_rounds = 0
        flag = 0
    
# /advsql

   
def colorize():
	for seg in idautils.Segments():
		heads = Heads(idc.get_segm_start(seg), idc.get_segm_end(seg))
		
		funcCalls = []
		jumps = []
		
		for i in heads:
			mnem = idc.print_insn_mnem(i)
			
			if mnem == "call":
				idc.set_color(i, CIC_ITEM, 0x00FFFF)
				
			if 'j' in mnem:
				idc.set_color(i, CIC_ITEM, 0xA9A9A9)
				
	for func in idautils.Functions():
		flags = idc.get_func_attr(func, FUNCATTR_FLAGS)

		#THUNK - function that call another function
		if (flags & FUNC_LIB) or (flags & FUNC_THUNK):
			continue

		#FuncItem - addresses of each instruction within function
		dism_addr = list(idautils.FuncItems(func))

		for line in dism_addr:
			m = idc.print_insn_mnem(line)
			if (m == 'call') or (m == 'jmp'):
				op = idc.get_operand_type(line, 0)
				if (op == o_reg):
					#print "0x% x % s" % (line, idc.GetDisasm(line))
					idc.set_color(line, CIC_ITEM, 0x00BFFF)

#EMLPRO
def get_hashes_from_push_emlpro():
    # идет по всем функциям где вызывается импорт API по хэшу
    hashes_from_push = {}
    for addr in CodeRefsTo(decrypt_func_addr,0):
        # находим третий пуш от вызова функции
        call_addr = addr
        i = 0
        while(i < 3):
            prev_addr = idc.prev_head(addr)
            if (idc.generate_disasm_line(prev_addr,1).find('push') == 0):
                i += 1
            addr = prev_addr
        hashes_from_push[call_addr] = hex(get_operand_value(addr,0))
    return hashes_from_push

def rename_imports_emlpro():
    hashes_from_push = get_hashes_from_push()
    lib_hashes = dict(parse_lib_hashes())
    
    for call_addr, value in hashes_from_push.items():
        value_up = value[2:].upper()
        if value_up in lib_hashes:
            print('addr = %s lib_hashes[%s] = %s' % (hex(call_addr), value_up, lib_hashes[value_up]))
            # Set comment on calls
            setCommentToDecompilation(lib_hashes[value_up], call_addr)
            # Rename dword to apiname
            # We take next instruction, and then take address of dword
            ea_dword = (get_operand_value(idc.next_head(call_addr), 0))
            ida_name.set_name(ea_dword, lib_hashes[value_up] + "_" + str(ea_dword), SN_CHECK)

#EMLPRO