#предварительно в IDA необходимо добавить Write права у сегмента если их нет: Edit > Segment > Edit Segment
#и изменить настройки Hex-Rays чтобы показывались const строки
#Edit -> Plugins -> Hex-Rays Decompiler -> options -> analysis option 1 -> print only const strings literals
#подробнее можно узнать здесь: https://hex-rays.com/blog/igors-tip-of-the-week-56-string-literals-in-pseudocode/
import idautils
import idc
import idaapi
import ida_bytes
#define STRTYPE_TERMCHR   (STRWIDTH_1B|STRLYT_TERMCHR<<STRLYT_SHIFT)
#Получить все строки которые распознает IDA
sc = idautils.Strings()
for s in sc:
	#вывести строку на экран
	print(s)
	strlen = idaapi.get_byte(s.ea-4)
	#Undefine смещение, чтобы отделить строку от структуры _top, Len, Text
	ida_bytes.del_items(s.ea-8, 0, 1, None)
	#Ре-распознать строку
	idaapi.create_strlit(s.ea, strlen+1, STRTYPE_TERMCHR)
	#Дать название смещению по которой находится строка, далее понадобится
	idc.set_name(s.ea, "str_%08X" % s.ea, ida_name.SN_FORCE)
	addr_name = idc.get_name(s.ea)
	#вывести адрес и название смещения
	print(hex(s.ea), addr_name)
	#изменить тип строки на const чтобы декомпилятор Hex-Rays смог вывести строки в исходном виде
	idc.SetType(s.ea,"const char " + addr_name + "[" + str(strlen) + "]")
	
	