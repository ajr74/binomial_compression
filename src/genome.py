import numpy as np
from bitarray import bitarray

bytesFromFile = np.fromfile("data/E.coli", dtype="uint8")  # Canterbury corpus
total_bytes_read = 0
total_compressed_bits = 0
window_bytes = []
bitset = bitarray()
for b in bytesFromFile:
    if b == 97:
        bitset.append(0)
        bitset.append(0)
    elif b == 99:
        bitset.append(0)
        bitset.append(1)
    elif b == 103:
        bitset.append(1)
        bitset.append(0)
    elif b == 116:
        bitset.append(1)
        bitset.append(1)
    total_bytes_read += 1

my_bytes = bitset.tobytes()

with open("data/E.coli.sensible", "wb") as binary_file:
    # Write bytes to file
    binary_file.write(my_bytes)
