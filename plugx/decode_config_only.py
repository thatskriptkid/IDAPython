import argparse

''' 
If you have boot.cfg in malware directory, use this script. Usage: python decode_config_only.py <boot.cfg>
''' 
parser = argparse.ArgumentParser(prog = 'decrypt config')
parser.add_argument('cfg_path')
args = parser.parse_args()

output_filename = 'decoded_cfg.bin'

cfg_data = []
with open(args.cfg_path, 'rb') as fcfg:
    cfg_data = fcfg.read()

key = ((cfg_data[3]*0x100 + cfg_data[2])*0x100 + cfg_data[1])*0x100 + cfg_data[0]
print('Config decrypt key: ' + hex(key))
mask = 0xFFFFFFFF
odin = dva = tri = chet = key
decrypted = len(cfg_data)*[0x0]
for i in range(0, len(cfg_data)):
    odin = (odin + (odin >> 3) - 0x11111111) & mask
    dva = (dva + (dva >> 5) - 0x22222222) & mask
    tri = (tri + 0x33333333 - (tri << 7)) & mask
    chet = (chet + 0x44444444 - (chet << 9)) & mask		
    decrypted[i] = (cfg_data[i] ^ (odin + dva + (tri & 0xFF) + (chet & 0xFF))) & 0xFF

with open(output_filename, 'wb') as fo:
    fo.write(bytearray(decrypted))
