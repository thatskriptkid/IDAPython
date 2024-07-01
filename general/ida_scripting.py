# -*- coding: utf-8 -*-
from idautils import *
from idaapi import *
from idc import *
import idautils

im_func = ""
seh_imports =['AbnormalTermination', 'AddVectoredContinueHandler', 'AddVectoredExceptionHandler', 'GetExceptionCode', 'GetExceptionInformation',
				'RaiseException', 'RemoveVectoredContinueHandler',  'RemoveVectoredExceptionHandler', 'RtlAddGrowableFunctionTable', 'RtlDeleteGrowableFunctionTable',
				'RtlGrowFunctionTable', 'SetUnhandledExceptionFilter', 'UnhandledExceptionFilter', 'VectoredHandler']

def _help():
	print "getFuncBnd(ea). Print start and end of function. In:address.\n"
	print "setBpImFunc(im_func_in). Set breakpoints on calls to import function. In:name or part of the name of imported function.\n"
	print "setBpOnEntries(). Set breakpoints on all entry points.\n"
	print "htoc(). Convert hex to char. In: number in hex\n"
	print "getInfo(). Print info about current address\n"
	print "colorize(). Highlights calls and jumps\n"
	print "xor()\n"
	print "seh(). Search and highlights SEH creating code. Print SEH related functions\n"
	print "antiDbgOff(). Disable anti-debug.\n"
	print "printByteOpcodes(). Print byte opcodes in selection\n"
	print "startWithAntiDbgOff(). Start the program, patch BeingDebugged field in PEB,  and suspend on entry\n"
	print "setCurrentEIPHotkey(). Add hotkey for 'Jump to IP' context menu item"

def bpOnDLLFunc():
	start = get_segm_by_name('ntdll').startEA
	end = get_segm_by_name('ntdll').endEA
	heads = list(Heads(start, end))
	print heads

def startWithAntiDbgOff():
	#Стартует приложение!
	RunTo(BeginEA());
	GetDebuggerEvent(WFNE_SUSP, -1);
	# На старте, EBX содержит адрес структуры PEB.
	ebx_addr = idc.GetRegValue('EBX')
	PatchByte(ebx_addr + 2, 0);
	print "BeingDebugged field in PEB patched!"

def printByteOpcodes():
	start = idc.SelStart()
	end = idc.SelEnd()

	print hex(start), hex(end)

	while (start < end): 
		print hex(idc.Byte(start))
		start = idc.NextAddr(start)

def kernelbaseDbgOff(startEA):
	'''
	Суть такова. Мы ищем функцию IsDebuggerPresent в kernelbase.dll. Мы должны сделать так, чтобы она возвращала 0.
	Ищем мы ее с помощью бинароного поиска. Тело этой функции, полностью указано в pattern.
	В результате мы получим адрес начала функции. Ищем от этого места, адрес инструкции ret.
	Ставим conditional brakepoint на возврат, условие - обнуление EAX. Что является обходом
	данного анти-отладочного приема.
	'''
	
	'''
	KERNELBASE:75642C98 64 A1 18 00 00 00 mov     eax, large fs:18h
	KERNELBASE:75642C9E 8B 40 30          mov     eax, [eax+30h]
	KERNELBASE:75642CA1 0F B6 40 02       movzx   eax, byte ptr [eax+2]
	KERNELBASE:75642CA5 C3                retn
	'''
	cnd='EAX=0'
	pattern = '64 A1 18 00 00 00 8B 40 30 0F B6 40 02 C3'
	print "Searching IsDebuggerPresent implementation"
				
	fnd_addr = idc.FindBinary(startEA, SEARCH_DOWN, pattern);
				
	if (fnd_addr != idc.BADADDR):
		print hex(fnd_addr), idc.GetDisasm(fnd_addr)
		#	KERNELBASE:75642CA5 C3                retn
		pattern = 'C3'
		print 'Searching ret...'
		ret_addr = idc.FindBinary(fnd_addr, SEARCH_DOWN, pattern);
		
		if ret_addr != idc.BADADDR:
			print hex(ret_addr), idc.GetDisasm(ret_addr)
		
		idc.AddBpt(ret_addr)
		#SetBptAttr(ret_addr, BPTATTR_BRK, 0x0);  #don't stop
		idc.SetBptCnd(ret_addr, cnd)
		
def textDbgOff(startEA):
	'''
	Вторая антиотладочная техника. Считывания значения поля BeingDebugged.
	
	.text:00401622 64 A1 30 00 00 00 mov     eax, large fs:30h ; Получает адрес PEB'а
	.text:00401628 0F B6 40 02       movzx   eax, byte ptr [eax+2] ; BeingDeb
	'''
	cnd='EAX=0'
	pattern = '64 A1 30 00 00 00 0F B6 40 02'
	
	print "Searching BeingDebugged extracting code..."
	
	fnd_addr = idc.FindBinary(startEA, SEARCH_DOWN, pattern);
	
	if (fnd_addr != idc.BADADDR):
		end = idc.GetFunctionAttr(fnd_addr, FUNCATTR_END)
		
		print hex(fnd_addr), idc.GetDisasm(fnd_addr)
		
		#Ищем инструкцию через одну. Так как следующая инструкция это зануления поля BeingDebugged
		# check_addr - адрес инструкции, где идет эта проверка
		check_addr = idc.NextHead(idc.NextHead(fnd_addr, end), end)
		print hex(check_addr), idc.GetDisasm(check_addr)
		
		idc.AddBpt(check_addr)
		#SetBptAttr(check_addr, BPT_BRK, 0);  #don't stop
		idc.SetBptCnd(check_addr, cnd)
		
def antiDbgOff():
	
	KERNELBASE = get_segm_by_name('KERNELBASE')
	TEXT = get_segm_by_name('.text')
	
	if (KERNELBASE is None) or (TEXT is None):
		print "Program is stopped or dont have TEXT or KERNELBASE segments"
	else:
		kernelbaseDbgOff(KERNELBASE.startEA)
		textDbgOff(TEXT.startEA)

def imp_cb_seh(ea, name, ord):
	if (ea != BADADDR):
		global seh_imports
		for i in seh_imports:
			if (name == i):
				print "\n%s 0x%08x" % (name, ea)
	else:
		print "invalid address 0x%x %s" % (ea, name)	
	# True -> Continue enumeration
	# False -> Stop enumeration
	return True
	
def printSehImports():
	imports = get_import_module_qty()

	for i in xrange(0, imports):
		name = get_import_module_name(i)
		if (not name):
			print "Failed to get import module name for #%d" % i
			continue
		enum_import_names(i, imp_cb_seh)

def seh():
	print "Searching places where SEH are set..."
	founds = []
	
	for seg in idautils.Segments():
		heads = list(Heads(SegStart(seg), SegEnd(seg)))
		for i,ea in enumerate(heads):
			mnem = GetMnem(ea)
			
			if (mnem == 'push') and ('fs:0' in GetOpnd(ea, 0)) and ('security_cookie' not in GetOpnd(heads[i+1], 1)):
				SetColor(ea, CIC_ITEM, 0xFF00FF)
				SetColor(heads[i-1], CIC_ITEM, 0xFF00FF)
				SetColor(heads[i+1], CIC_ITEM, 0xFF00FF)
				
				founds.append(hex(ea))
				MakeComm(heads[i-1], "SEH CREATING")
				
	print "Finished. Addresses were highlighted", founds
	printSehImports()
	
def xor(a, b):
	print hex(a^b)

def colorize():
	for seg in idautils.Segments():
		heads = Heads(SegStart(seg), SegEnd(seg))
		
		funcCalls = []
		jumps = []
		
		for i in heads:
			mnem = GetMnem(i)
			
			if mnem == "call":
				SetColor(i, CIC_ITEM, 0x00FFFF)
				
			if 'j' in mnem:
				SetColor(i, CIC_ITEM, 0xA9A9A9)
				
	for func in idautils.Functions():
		flags = idc.GetFunctionFlags(func)

		#THUNK - function that call another function
		if (flags & FUNC_LIB) or (flags & FUNC_THUNK):
			continue

		#FuncItem - addresses of each instruction within function
		dism_addr = list(idautils.FuncItems(func))

		for line in dism_addr:
			m = idc.GetMnem(line)
			if (m == 'call') or (m == 'jmp'):
				op = idc.GetOpType(line, 0)
				if (op == o_reg):
					#print "0x% x % s" % (line, idc.GetDisasm(line))
					SetColor(line, CIC_ITEM, 0x00BFFF)

def htoc(h):
	print chr(int(h))

def getFuncBnd(ea):
	if (ea != BADADDR):
		func_start = GetFunctionAttr(ea, FUNCATTR_START)
		func_end = GetFunctionAttr(ea, FUNCATTR_END)
		if (func_start == BADADDR) or (func_end == BADADDR):
			print "Address 0x%08x is not in function" % ea
		else:
			print "Start:0x%08x End:0x%08x", func_start, func_end
	else:
		print "Address is invalid"

def imp_cb_im_func(ea, name, ord):
	if (ea != BADADDR):
		global im_func
		if (im_func in name.lower()):
			if GetFunctionAttr(ea, FUNCATTR_START) != BADADDR:
				idc.AddBpt(ea)
			else:
				for xref in XrefsTo(ea, 0):
					#print xref.type, XrefTypeName(xref.type),'from', hex(xref.frm), 'to', hex(xref.to)
					idc.AddBpt(xref.frm)# add bp on each call to imported function
	else:
		print "invalid address 0x%x %s" % (ea, name)	
	# True -> Continue enumeration
	# False -> Stop enumeration
	return True

def setBpImFunc(im_func_in):
	global im_func
	im_func = im_func_in.lower()
	imports = get_import_module_qty()

	for i in xrange(0, ):
		name = get_import_module_name(i)
		if (not name):
			print "Failed to get import module name for #%d" % i
			continue
		enum_import_names(i, imp_cb_im_func)

def setBpOnEntries():
	#List of tuples (index, ordinal, ea, name)
	entries = list(idautils.Entries())
	
	if (len(entries) == 0):
		print "No entry points!"
	else:
		for entry in entries:
			ea = entry[2]
			idc.AddBpt(ea)
			print "Bp on %s(0x%08x) set " % (entry[3], ea) 

def getInfo():
	ea = idc.ScreenEA() # here()
	if (ea != BADADDR):
		print "Current address:0x%x" % ea
		print idc.SegName(ea)
		print "Current instruction:%s" % idc.GetDisasm(ea)
		print "Mnemonic: %s" % idc.GetMnem(ea) 
		print "First operand: %s" % idc.GetOpnd(ea, 0) 
		print "Second operand: %s" % idc.GetOpnd(ea, 1)
	else:
		print "Address is not valid"

def jumpToEIP():
	jumpto(GetRegValue('EIP'))
	
def setCurrentEIPHotkey():
	idaapi.CompileLine('static key_1() { RunPythonStatement("jumpToEIP()"); }')
	AddHotkey("1", 'key_1')

print "big_ban initializing..."
setCurrentEIPHotkey()
print "Color scheme: Gray=jmps, yellow=calls, orange=dynamic jmps/calls" 
colorize()
seh()
print "big_ban initialized"
