# Скрипт взят из статьи https://www.gatewatcher.com/wp-content/uploads/2022/03/AgentTesla_rapport_EN.pdf

from PIL import Image
key = "ly2P"
img = Image.open('AsyncCausalityStat.png')
# extract data from the picture
width = img.size[0]
pix = img.load()
data = b''
for i in range(0, width):
    for j in range(0, width):
        for c in [2, 1, 0, 3]:
 data += pix[i, j][c].to_bytes(1, byteorder='little')
size = int.from_bytes(data[:4], 'little')
fdata = data[4:4+size]
# decryption
xor_int = fdata[-1] ^ 112
xor_key = key.encode("utf-16-be")
xor_key_len = len(key) # "bug" here : len(xor_key) = 2*len(key) due to utf16
output = b''
for i in range(0, len(fdata)):
 output += ((fdata[i] ^ xor_int ^ xor_key[i % xor_key_len]) &
0xFF).to_bytes(1, 'little')
output = output[:-1]