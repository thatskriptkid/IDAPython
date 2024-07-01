

# Скрипт для переименования импортов. Копируем из x64dbg импорты, они
# в такой форме будут. Могут быть проблемы с пробелами в третьем столбец и 
# там где пусто будет второй столбец будет 00000. Проще подредактировать вручную 

# 1002A304  70A02F06  ./p  mpr.WNetOpenEnumW
# 1002A308  70A03058  X0p  mpr.WNetEnumResourceW
# 1002A30C  70A02DD6  Ö-p  mpr.WNetCloseEnum
# 1002A314  763A1544  D.:v  psapi.EnumProcesses
# 1002A318  763A1408  ..:v  psapi.EnumProcessModules
# 1002A31C  763A13F0  ð.:v  psapi.GetModuleFileNameExW
# 1002A320  763A152C  ,.:v  psapi.GetModuleBaseNameW
# 1002A328  76501E65  e.Pv  shell32.ShellExecuteExW
# 1002A32C  764F9EB8  ¸.Ov  shell32.CommandLineToArgvW
# 1002A334  764823EB  ë#Hv  shlwapi.SHDeleteKeyW
# 1002A338  764AC489  .ÄJv  shlwapi.StrStrA
# 1002A33C  7648C61E  .ÆHv  shlwapi.StrChrA
# 1002A340  764945F7  ÷EIv  shlwapi.PathFileExistsW
# 1002A344  7648D236  6ÒHv  shlwapi.StrChrIA
# 1002A348  7648D288  .ÒHv  shlwapi.StrStrIA
# 1002A350  75148FDF  ß..u  user32.UnhookWindowsHookEx
# 1002A354  751378F2  òx.u  user32.GetMessageW
 
def rename_imports_from_list(api_list_filepath):
    with open(api_list_filepath, 'r', encoding='UTF-8') as _fp:
        for line in _fp:
            lib_addr = int(line.split()[1], 16)
            if not lib_addr:
                continue
            qword_addr = int(line.split()[0], 16)
            print(lib_addr, (line.split()[3]))
            func_name = (line.split()[3]).split('.')[1]
            ida_name.set_name(qword_addr, func_name + "__", SN_CHECK)