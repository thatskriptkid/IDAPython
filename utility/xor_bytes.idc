// ida script
// XOR n patch byte 

auto src, dst, len, i, byteat, xorred;

src = ask_addr(0, "Src: ");
dst = ask_addr(0, "Dst: ");
len = ask_addr(0, "Len: ");

Message("Source = %x, Destination = %x, Length = %x\n", src, dst, len);

for (i = 0; i < len; i++) {
	byteat = get_db_byte(src+i);
	xorred = byteat ^ 0x2d;
	patch_byte(dst+i, xorred);
}
