import pefile
import argparse
import subprocess
import os
import datetime
from datetime import timezone
from OpenSSL import crypto
from OpenSSL.crypto import _lib, _ffi, X509
import re
import hashlib
import math

# результат сохраняется в тот путь, откуда вызывается скрипт
# pip install -r requirements.txt
# Перед запуском указать путь к floss https://github.com/mandiant/flare-floss

# ---------------------------------------------------------------
# глобальные переменные
BUF_SIZE = 4096
result_filename = os.path.join(os.getcwd(), 'file_info.txt')
floss_path = 'D:\\Tools\\floss-v1.7.0-windows\\floss.exe'
floss_str_output_filename = os.path.join(os.getcwd(), 'floss_str_output.txt')
floss_ida_output_filename = os.path.join(os.getcwd(), 'floss_ida_output.py')
# ставит комментарии на декомпилированный код, работает даже в 7.6
cmt_method = """def setCommentToDecompilation(comment, address):
    try:
        cfunc = idaapi.decompile(address)
        
        
        eamap = cfunc.get_eamap()
        decompObjAddr = eamap[address][0].ea

        tl = idaapi.treeloc_t()
        tl.ea = decompObjAddr
        
        commentSet = False
        for itp in range(idaapi.ITP_SEMI, idaapi.ITP_COLON):
            tl.itp = itp    
            cfunc.set_user_cmt(tl, comment)
            cfunc.save_user_cmts()
            unused = cfunc.__str__()
            if not cfunc.has_orphan_cmts():
                commentSet = True
                cfunc.save_user_cmts()
                break
            cfunc.del_orphan_cmts()
    except:
        pass
"""
# ---------------------------------------------------------------

parser = argparse.ArgumentParser(prog = 'file info', description = 'get var info about PE')
parser.add_argument('path')
parser.add_argument('-s', action='store_true', help = 'generate ida script')
parser.add_argument('-f', action='store_true', help = 'processing with floss')
parser.add_argument('-sc', action='store_true', help = 'a file is shellcode')
args = parser.parse_args()

# Вычисление энтропии
def get_entropy(data):
    # 256 different possible values
    possible = dict(((chr(x), 0) for x in range(0, 256)))

    for byte in data:
        possible[chr(byte)] +=1

    data_len = len(data)
    entropy = 0.0

    # compute
    for i in possible:
        if possible[i] == 0:
            continue

        p = float(possible[i] / data_len)
        entropy -= p * math.log(p, 2)
    return entropy
    
# вывод тулзы floss в файл
def floss_str_dump():
    print('floss | string dumping...')
    try:
        with open(floss_str_output_filename, 'w') as fsd:
            proc_args = (floss_path, args.path)
            subprocess.run(proc_args, stdout = fsd, stderr = subprocess.DEVNULL)
    except Exception as err:
        print(f"floss | Unexpected {err=}, {type(err)=}")
        raise
    finally:
        print('floss | string dumped')

# generate IDA script
def floss_gen_ida():
    print('floss | generating ida script')
    try:
        proc_args = (floss_path, args.path, '-i', floss_ida_output_filename)
        subprocess.run(proc_args, stdout = subprocess.DEVNULL, stderr = subprocess.STDOUT)
        patch_floss_ida_script()
            
    except Exception as err:
        print(f" floss | Unexpected {err=}, {type(err)=}")
        raise
    finally:
        print('floss | ida script genereated!')
        
# тип файла: {PE32, PE64, PE32 DLL, PE64 DLL}
def get_pe_type(pe):
    try:
        pe_filetype = 'PE' 
        if pe.FILE_HEADER.Machine == 0x014c:
            pe_filetype += '32'
        if pe.FILE_HEADER.Machine == 0x8664:
            pe_filetype += '64'
    # почему отнимаем 0x2000:
    # https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_file_header
    # IMAGE_FILE_DLL 0x2000
    # The image is a DLL file. While it is an executable file, it cannot be run directly.
        if pe.FILE_HEADER.Characteristics - 0x2000 >= 0:
            pe_filetype += ' DLL' 
        return pe_filetype
    except Exception:
        raise


# подписан или нет. если подписан, достает сертификаты библиотекой pyopenssl (обертка питона над openssl)
# даже если файл не подписан, у dictionary будет key - pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_SECURITY']

def get_certificates(self):
    try:
        certs = _ffi.NULL
        if self.type_is_signed():
            certs = self._pkcs7.d.sign.cert
        elif self.type_is_signedAndEnveloped():
            certs = self._pkcs7.d.signed_and_enveloped.cert

        pycerts = []
        for i in range(_lib.sk_X509_num(certs)):
            pycert = X509.__new__(X509)
            pycert._x509 = _lib.sk_X509_value(certs, i)
            pycerts.append(pycert)

        if not pycerts:
            return None
        return tuple(pycerts)
    except Exception:
        raise
    
def get_sign(pe):
    try:
        result = ''
        entry_security = pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_SECURITY']]
        if entry_security.Size > 0:
            result = 'Да\n'
            signature = pe.write()[entry_security.VirtualAddress + 8 :]

            pkcs = crypto.load_pkcs7_data(crypto.FILETYPE_ASN1, bytes(signature))
            certs = get_certificates(pkcs)

            for cert in certs:
                c = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
                a = crypto.load_certificate(crypto.FILETYPE_PEM, c)
                # get data from parsed cert
                result += str(a.get_subject())
                result += '\n'
        else:
            result = 'Нет\n'
        return result
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        pass

# нам надо пропатчить скрипт флоса так, чтобы он ставил комменты на декомпилированный код
def patch_floss_ida_script():
    try:
        data = ''
        with open(floss_ida_output_filename, 'r+') as fd:
            data = fd.read()
            fd.seek(0)
            data += '\n'
            data += cmt_method
            # исключаем оригинальный метод из списка замены
            data = re.sub('def AppendComment', 'def garbage', data)
            data = re.sub('AppendComment', 'setCommentToDecompilation', data)
            fd.write(data)
    except Exception:
        raise

def get_hashes():

    hashes = {}
    
    try:
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()
        with open(args.path, "rb") as f:
            
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                md5.update(data)
                sha1.update(data)
                sha256.update(data)
                
        hashes['md5'] = md5.hexdigest()
        hashes['sha1'] = sha1.hexdigest()
        hashes['sha256'] = sha256.hexdigest()
        
        return hashes
    except:
        raise
        
def pe_info():
    try:
        pe = pefile.PE(args.path)
        with open(result_filename, "w+") as f:
        
            f.write('Filename: %s\n' % os.path.basename(args.path))
            
            hashes = get_hashes()
            f.write('MD5: %s\n' % hashes['md5'])
            f.write('SHA-1: %s\n' %  hashes['sha1'])
            f.write('SHA-256: %s\n' %  hashes['sha256'])
            
            f.write('File size: %d\n' % os.path.getsize(args.path))
            
            dt_ts = str(datetime.datetime.fromtimestamp(pe.FILE_HEADER.TimeDateStamp, tz=timezone.utc))
            f.write('Метка времени: %s\n' % dt_ts.rstrip('+00:00')) 
            
            f.write('Filetype: %s\n' % get_pe_type(pe))
            
            f.write('Подписан?: %s' % get_sign(pe))
            
            f.write("[*]MD5/энтропия хэши секций:\n")
            for sec in pe.sections:
                # rstrip - костыль, так как pefile нам выдает имена секций с \x00\x00\x00 на конце
                sec_name = sec.Name.decode('utf-8').rstrip('\x00')
                f.write("%s\n" % sec_name) 
                f.write('%s\n' % sec.get_hash_md5())
                f.write("%s\n" % str(get_entropy(sec.get_data())))

            f.write('[*] Imphash:\n')
            f.write(pe.get_imphash() + '\n')

            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                f.write('[*] Импорты\n') 
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    dll_name = entry.dll.decode('utf-8')
                    f.write('[*]' + dll_name + '\n')
                    for func in entry.imports:
                        if func.name != None:
                            f.write("%s\n" % (func.name.decode('utf-8')))

            if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
                f.write('[*] Экспорты\n')
                if pe.DIRECTORY_ENTRY_EXPORT.symbols:
                    for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                        if exp.name != None:
                            f.write(exp.name.decode('utf-8') + "\n")
                            
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise

# если переданный файл - шеллкод, а не полноценный PE
def sc_info():
    try:
        with open(result_filename, "w+") as f:

            f.write('Filename: %s\n' % os.path.basename(args.path))

            hashes = get_hashes()
            f.write('MD5: %s\n' % hashes['md5'])

            f.write('SHA-1: %s\n' %  hashes['sha1'])

            f.write('File size: %d\n' % os.path.getsize(args.path))
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
        
print('file info dumping...')
if args.sc:
    sc_info()
else:
    pe_info()
    if args.f:
        floss_str_dump()
    if args.s:
        floss_gen_ida()
print('file info dumped')