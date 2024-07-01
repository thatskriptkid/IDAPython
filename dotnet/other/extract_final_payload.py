# Скрипт взят из статьи https://www.gatewatcher.com/wp-content/uploads/2022/03/AgentTesla_rapport_EN.pdf

import base64
key = "fSGCorS"
with open("payload3.b64", "r") as f:
 input_b64 = f.read()
input_data = base64.b64decode(input_b64 + ("=" * (len(input_b64) % 4)))
key_data = key.encode("ASCII")
array = [input_data[i] for i in range(0, len(input_data))]
for i in range(0, len(array)+1):
 i1 = array[i % len(array)] ^ key_data[i % len(key_data)]
 i2 = array[(i+1) % len(array)]
 array[i % len(array)] = (i1 - i2 + 256) % 256
output = b''.join([x.to_bytes(1, 'little') for x in array])[:-1]