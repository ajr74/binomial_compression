import math
import random
import time

from scipy.special import comb
from bitstream import BitStream
import numpy as np
import matplotlib.pyplot as plt

numBytesInWindow = 8
rehydrate = False
plot_chart = False

byte_positions_cache = {}
bitcount_cache = {}
k_bool_list_cache = {}

part1time = 0
part2time = 0

def bool_list_to_int(bool_list):
    multiplier = 1 << (len(bool_list) -  1)
    result = 0
    for bit in bool_list:
        if bit:
            result += multiplier
        multiplier = multiplier >> 1
    return result

def int_to_bool_list(num, numbits):  # writes HSB first
    return [bool(num & (1<<n)) for n in reversed(range(numbits))]

def write_to_bitstream(num, numbits, bitstream):
    for n in reversed(range(numbits)):
        bitstream.write(bool(num & (1<<n)), bool)

def bitCount(b):
    if b in bitcount_cache:
        return bitcount_cache[b]

    #print("Cache miss!")
    count = 0
    b_before = b
    while b:
        b &= b - 1
        count += 1

    bitcount_cache[b_before] = count
    return count

def binm(i, j):
    #return comb(i, j, exact=True)
    global C
    if i >= j:
        return C[i][j] # or, explicitly: comb(i, j, exact=True)
    return 0


class Window:

    # constructor method
    def __init__(self, k, bytes):
        global part1time, part2time, C
        self.k = k
        self.bytes= bytes
        numbytes = len(bytes)
        numbits = numbytes << 3 #8 * numbytes

        # compression index

        part1_tic = time.perf_counter()
        self.positions = []
        offset = 0
        for byte in bytes:
            if byte in byte_positions_cache:
                for pos in byte_positions_cache[byte]:
                    self.positions.append(offset + pos)
            else:
                _positions = []
                for i in range(8):
                    if byte & (1 << i):
                        _positions.append(i)
                byte_positions_cache[byte] = _positions
                for pos in _positions:
                    self.positions.append(offset + pos)

            offset += 8

        part1_toc = time.perf_counter()
        part1time += (part1_toc - part1_tic)

        part2_tic = time.perf_counter()
        compression_index = 0
        #j = 0
        j = 1
        for position in self.positions:
            compression_index += binm(position, j)
            j += 1
        self.index = compression_index
        part2_toc = time.perf_counter()
        part2time += (part2_toc - part2_tic)

        # rehydrates bytes

        if rehydrate:
            target = self.index
            start = numbits - 1
            num = 0
            self.positions2 = []
            for i in range(self.k, 0, -1):
                for j in range(start, -1, -1):
                    b = binm(j, i)  # make more efficient by using Pascal's identity
                    if b <= target:
                        self.positions2.append(j)
                        num += (1<<j)
                        target = target - b
                        break
                start = start - 1
            self.rehydrate = num

            t = 0
            off = 0
            for byte in self.bytes:
                t += (byte * (1<<off))
                off += 8
            self.t = t


def compression_report(before, after):
    ratio = after * 1.0 / before
    print(f"Compression ratio: {ratio} :: ({1.0/ratio} x compression)")

def shannonEntropy(_counts):
    n = 0.0
    for c in _counts:
        n += c
    ent = 0
    for c in _counts:
        if c > 0:
            p = c / n
            ent += (p * math.log2(p))
    return -ent


tic = time.perf_counter()

numBitsInWindow = 8 *  numBytesInWindow
# populate binomial coefficient lookup table with Pascal's rule

cache_builder_tic = time.perf_counter()
C = [[1]]
for n in range(1, numBitsInWindow+1):
    row=[1]
    for k in range(1, n):
        row.append(C[n-1][k-1] + C[n-1][k])
    row.append(1)
    C.append(row)

cache_builder_toc = time.perf_counter()
print(f"Setting up binomial coefficient cache took {cache_builder_toc - cache_builder_tic:0.4f} seconds")

cache_builder_tic = time.perf_counter()
C2 = [[1]]
for n in range(1, numBitsInWindow+1):
    row=[1]
    for k in range(1, (n//2) + 1 ):
        kindex = min(k,len(C2[n-1]) - 1)
        #row.append(C2[n-1][k-1] + C2[n-1][k])
        row.append(C2[n-1][k-1] + C2[n-1][kindex])
    C2.append(row)

cache_builder_toc = time.perf_counter()
print(f"Setting up symmetrised binomial coefficient cache took {cache_builder_toc - cache_builder_tic:0.4f} seconds")


bytesFromFile = np.fromfile("sample_5184×3456.pbm", dtype = "uint8")

byteCounts = []
for i in range(256):
    byteCounts.append(0)

counts = []
count = 0
i = 0
windows = []
windowBytes = []
numbytesprocessed = 0
reading_tic = time.perf_counter()
for fileByte in bytesFromFile:
    numbytesprocessed += 1
    #if numbytesprocessed % (1024 * 10) == 0:
    #    print(f"Bytes processed {numbytesprocessed}")
    if i == 0:
        windowBytes = []
    windowBytes.append(fileByte)
    byteCounts[fileByte] += 1
    i += 1
    count += bitCount(fileByte)
    if i == numBytesInWindow:
        counts.append(count)
        window = Window(count, windowBytes)
        windows.append(window)
        count = 0
        i = 0

reading_toc = time.perf_counter()
print(f"Reading to windows took {reading_toc - reading_tic:0.4f} seconds")
print(f"Number of counts: {len(counts)}")


# print the result
print('Shannon entropy: %.3f bits' % shannonEntropy(byteCounts))
smallest = min(counts)
largest = max(counts)
print(f"smallest k: {smallest}")
print(f"largest k: {largest}")


log2Nplus1 = math.log2(numBitsInWindow + 1)
ceilLog2Nplus1 = math.ceil(log2Nplus1)
print(f"ceilk: {ceilLog2Nplus1}")
before = 0
after = 0
for k in counts:
    before += numBitsInWindow
    binomial = math.comb(numBitsInWindow, k)
    cost = ceilLog2Nplus1 + math.ceil(math.log2(binomial))
    after += cost
    #print(f"cost: {cost} ({numBitsInWindow})")
print(f"Before: {math.ceil(before/8)} bytes")
print(f"After: {math.ceil(after/8)} bytes")
compression_report(before, after)

# write to a stream
stream = BitStream()
prevK = -1
persistence_tic = time.perf_counter()
for window in windows:
    k_bool_list = []
    if window.k in k_bool_list_cache:
        k_bool_list = k_bool_list_cache[window.k]
    else:
        k_bool_list = int_to_bool_list(window.k, ceilLog2Nplus1)
        k_bool_list_cache[window.k] = k_bool_list
    num_payload_bits = math.ceil(math.log2(binm(numBitsInWindow, window.k)))
    payload_bool_list = int_to_bool_list(window.index, num_payload_bits)

    if prevK != 0 and prevK != numBitsInWindow:  # TODO add RLE for k=0, K=N
    #if prevK != 0:
    #if True:
        #write_to_bitstream(window.k, ceilLog2Nplus1, stream)
        #write_to_bitstream(window.index, num_payload_bits, stream)
        for foo in k_bool_list:
            stream.write(foo, bool)
        for foo2 in payload_bool_list:
            stream.write(foo2, bool)

    prevK = window.k
persistence_toc = time.perf_counter()
print(f"Setting up stream took {persistence_toc - persistence_tic:0.4f} seconds")

#my_lovely_bytes = stream.read(bytes)
num_stream_bits = stream.__len__()
num_stream_bytes = math.ceil(num_stream_bits / 8)

writing_to_disk_tic = time.perf_counter()
myfile = open("no_k_nor_N.bin", "wb")
for i in range(num_stream_bytes-1):  # write everything except for the straggling bits (TODO)
    #print(f"Stream length: {stream.__len__()}")
    bitstream_byte = stream.read(bytes, 1)
    myfile.write(bitstream_byte)
myfile.close()
writing_to_disk_toc = time.perf_counter()
print(f"Writing stream bytes to disk took {writing_to_disk_toc - writing_to_disk_tic:0.4f} seconds")

toc = time.perf_counter()
print(f"Compression took {toc - tic:0.4f} seconds")

if plot_chart:
    ## Create histogram dataset
    hist_array, bin_array = np.histogram(counts, np.arange(1 + numBitsInWindow))

    ## Set some configurations for the chart
    plt.figure(figsize=[10, 5])
    plt.xlim(min(bin_array), max(bin_array))
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Edge Values', fontsize=20)
    plt.ylabel('Histogram Values', fontsize=20)
    plt.title('Histogram Chart', fontsize=25)

    ## Create the chart
    plt.bar(bin_array[:-1], hist_array, width=0.5, color='blue')
    # Display the chart
    plt.show()