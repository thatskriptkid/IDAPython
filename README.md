Куча мелких скриптов дял анализа малвари

# IDAPython
Scripts for IDAPython

ida_scripting.py
_help() - for function description

getFuncBnd(ea). Print start and end of function. In:address.


setBpImFunc(im_func_in). Set breakpoints on calls to import function. In:name or part of the name of imported function.


setBpOnEntries(). Set breakpoints on all entry points.

htoc(). Convert hex to char. In: number in hex

getInfo(). Print info about current address

colorize(). Highlights calls and jumps

xor(). xor

seh(). Search and highlights SEH creating code. Print SEH related functions

antiDbgOff(). Disable anti-debug.

printByteOpcodes(). Print byte opcodes in selection

startWithAntiDbgOff(). Start the program, patch BeingDebugged field in PEB,  and suspend on entry

setCurrentEIPHotkey(). Add hotkey for 'Jump to IP' context menu item

