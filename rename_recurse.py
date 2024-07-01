import idaapi
import idautils
import idc

def rename_sub_functions(ea, prefix="zinflate_"):
    """
    Рекурсивно переименовывает все функции, начинающиеся с "sub", вызываемые из указанной функции.
    
    :param ea: Адрес начала функции.
    :param prefix: Префикс для новых имен функций.
    """
    visited = set()

    def rename_function_recursive(ea):
        if ea in visited:
            return
        visited.add(ea)

        # Получаем имя функции
        func_name = idc.get_func_name(ea)

        # Переименовываем функцию, если она начинается с "sub"
        if func_name.startswith("sub_"):
            new_name = prefix + func_name[4:]  # Убираем "sub_" и добавляем префикс
            idc.set_name(ea, new_name, idc.SN_AUTO)

        # Проходим по всем инструкциям в функции
        for head in idautils.FuncItems(ea):
            # Проверяем, является ли инструкция вызовом другой функции
            if idc.print_insn_mnem(head) in ["call", "jmp"]:
                called_func = idc.get_operand_value(head, 0)
                if idc.get_func_name(called_func).startswith("sub_"):
                    rename_function_recursive(called_func)

    rename_function_recursive(ea)

# Пример использования: укажите адрес функции, внутри которой нужно рекурсивно переименовывать функции
start_ea = 0x4615d0
rename_sub_functions(start_ea)
