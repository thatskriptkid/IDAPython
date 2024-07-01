

import idautils

# Скрипт для поиска Switch во всем коде

text_seg = idaapi.get_segm_by_name('.text')
for head_ea in idautils.Heads(text_seg.start_ea, text_seg.end_ea):
    if ida_bytes.is_code(ida_bytes.get_full_flags(head_ea)):
        si = ida_nalt.switch_info_t()
        if (ida_nalt.get_switch_info(si, head_ea) is not None):
            print(hex(si.startea))