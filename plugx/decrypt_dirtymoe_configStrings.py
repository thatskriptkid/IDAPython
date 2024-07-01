'''
## Алгоритм работы скрипта
1. Проверка первого блока из 256 байт (пропуская сигнатурные 8 байт) на нелувое значение
2. Считывание длинны названия файла, а затем самого названия
3. Считывание размера файла, а затем тела файла
4. Запись считанных файлов в отдельные файлы с префиксом "raw_{Название файла}"
5. Расшифровка полученных объектов, и запись их в отдельные файлы с префиксом "decrypted_{Название файла}"
6. Распаковка расшифрованных файлов методом zlib, запись их  в отдельные файлы "{Название файла}"
7. Удаление временных объектов с префиксами "raw_" и "decrypted_".
В итоге скрипт расшифровывает полезную нагрузку с заголовком 0x797876 содержащую в себе несколько зашифрованных модулей данного семейства

## Описание структуры пейлоада
Заголовок полезной нагрузки 0x797876 также является ключом шифрования. Заголовок состоит из 8 байтов: 3 в виде ключа и сигнатуры объекта, 5 - резервных. Следующие 256 байтов относятся к названию зашифрованного файла, первый байт – длина названия, затем следует само название. Далее расположены 4 байта содержащие размер файла в little-endian формате, после чего следует само тело зашифрованного файла, соответствующее размеру, указанному ранее. Следующие объекты конкатенированы в этом же формате, начиная с 256 байтов названия.

'''

import base64
import sys
#usage: decrypt_dirtymoe_configStrings.py [e] or [d] [string]
key = [1, 0x2E, 0x49, 0x9D]

def encrypt_str(maString):
	baString = bytearray(maString)
	baLen = len(baString)
	for r in range(3):
		baString[0]  = (baString[0] + key[1]) & 0xFF
		for i in range(1, baLen):
			baString[i] = ((baString[i-1] + baString[i]) & 0xFF) ^ key[3]
		baString[baLen-1] = (baString[baLen-1] + key[0]) & 0xFF
		for j in range(baLen-2, -1,  -1):
			baString[j] = ((baString[j+1] + baString[j]) & 0xFF) ^ key[2]
	print(base64.b64encode(bytearray(baString)))
	
def decrypt_str(maString):
	baString = bytearray(base64.b64decode(maString))
	baLen = len(baString)
	for r in range(3):
		for i in range(0, baLen-1):
			baString[i] = ((baString[i] ^ key[2]) - baString[i+1]) & 0xFF
		baString[baLen-1] = (baString[baLen-1] - key[0]) & 0xFF
		for j in range(baLen-1, 0, -1):
			baString[j] = ((baString[j] ^ key[3]) - baString[j-1]) & 0xFF
		baString[0]  = (baString[0] - key[1]) & 0xFF
	print(baString)

def main():
	func = sys.argv[1]
	maString = sys.argv[2]
	if func == "e":
		encrypt_str(maString)
	elif func == "d":
		decrypt_str(maString)
	else:
		print("*.py [e] or [d] [string]")


if __name__ == '__main__':
	main()
