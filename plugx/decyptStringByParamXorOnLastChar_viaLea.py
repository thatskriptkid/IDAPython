addr=here()
addr_of_call=addr
ad=idc.prev_head(addr)
while(idc.generate_disasm_line(addr,1).find('lea')==-1 ):
    addr=idc.prev_head(addr)
ad=addr
while(idc.generate_disasm_line(idc.prev_head(addr),1).find('mov')!=-1 ):
    addr=idc.prev_head(addr)
print (hex(addr))
string=''
while(addr!=ad):
    print (idc.generate_disasm_line(addr,1).split(',')[1].split(';')[0].split('h')[0])
    if get_operand_value(addr,1)==0 or idc.generate_disasm_line(addr,1).split(',')[1].find('+')!=-1 or idc.generate_disasm_line(addr,1).split(',')[1].find('m')!=-1 or idc.generate_disasm_line(addr,1).split(',')[1].find(']')!=-1  or idc.generate_disasm_line(addr,1).split(',')[1].find('word')!=-1  or idc.generate_disasm_line(addr,1).split(',')[1].find('r')!=-1 or idc.generate_disasm_line(addr,1).split(',')[1].find('rsi')!=-1 or idc.generate_disasm_line(addr,1).split(',')[1].find('off')!=-1:
        addr=idc.next_head(addr)
        continue
    a=idc.generate_disasm_line(addr,1).split(',')[1].split(';')[0].split('h')[0]
    #print ("a= "+ a)
    for i in range (len(a)-1,1,-2):
        string=string+a[i-1]+a[i]
        #print (a[i-1]+a[i])
    addr=idc.next_head(addr)
#string=string[:-2]
print ("encrypted string", string, "len",len(string) )  
    
size=len(string)
dec_str=''
j=0;
key=int(string,16)%256
for i in range (0,size,2):
    a=int(string[i],16)*16+int(string[i+1],16)
    dec_str=dec_str+chr(a^key)
print (dec_str)
idc.set_cmt(addr_of_call,dec_str,0)
