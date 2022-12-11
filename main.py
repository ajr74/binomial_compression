from bitarray import bitarray
import bisect
import numpy as np
import math
import time


def process_window(bytes, reverse=False) -> int:
    N = len(bytes)
    byte_positions = []
    for i in range(0, 256):
        byte_positions.append([])
    byteCounts = [0] * 256
    position = 0
    for b in bytes:
        byteCounts[b] += 1
        byte_positions[b].append(position)
        position += 1

    #tic = time.perf_counter()
    byte_bitsets = []
    to_remove = []
    for byte_val in range(0, 256):
        to_add = byte_positions[byte_val]
        if len(to_add) > 0:
            bitset = bitarray(N)
            bitset.setall(0)
            for i in to_add:
                bitset[i] = 1
            for i in to_remove[::-1]:
                bitset.pop(i)
            for i in to_add:
                bisect.insort(to_remove, i)
            byte_bitsets.append((byte_val, bitset))

        #assert k == bits_appended
    #toc = time.perf_counter()
    #print(f"Num bitsets = {len(bitsets)} took {toc - tic:0.4f} seconds")

    # try reversing
    if reverse:
        occupied_positions = bitarray(N)
        occupied_positions.setall(0)
        rehydrated_bytes = [0] * N
        for byte_val, bitset in byte_bitsets:
            inner_i = 0
            for outer_i in range(0, N):
                if occupied_positions[outer_i]:
                    continue
                if bitset[inner_i]:
                    rehydrated_bytes[outer_i] = byte_val
                    occupied_positions[outer_i] = 1
                inner_i += 1
        assert rehydrated_bytes == bytes

    num_compressed_bits = 0
    #log2N = math.ceil(math.log2(N))
    #i = 0
    #k_elapsed = 0
    #total_percentage = 0.0
    #for k in byteCounts:
    #    if k >= 0:
    #        percentage = (100.0 * k) / N
    #        total_percentage += percentage
    #        # payload_bits = math.ceil(math.log2(math.comb(N - k_elapsed, k)))
    #        payload_bits = math.ceil(math.log2(C[N - k_elapsed][k]))
    #        if payload_bits > 0:
    #            compressed_bits = log2N + payload_bits
    #            num_compressed_bits += compressed_bits
    #        k_elapsed += k
    #    i += 1
    #assert total_percentage > 99.8
    return num_compressed_bits


if __name__ == '__main__':

    bytes_per_window = 1024  # -1 for everything in one go

    numBitsInWindow = 8 * bytes_per_window
    # populate binomial coefficient lookup table with Pascal's rule

    cache_builder_tic = time.perf_counter()
    C = [[1]]
    for n in range(1, bytes_per_window + 1):
        row = [1]
        for k in range(1, n):
            row.append(C[n - 1][k - 1] + C[n - 1][k])
        row.append(1)
        C.append(row)

    cache_builder_toc = time.perf_counter()
    print(f"Setting up binomial coefficient cache took {cache_builder_toc - cache_builder_tic:0.4f} seconds")

    estimation_tic = time.perf_counter()
    bytesFromFile = np.fromfile("data/nuix_trust.pdf", dtype="uint8")
    total_bytes_read = 0
    total_compressed_bits = 0
    window_bytes = []
    for b in bytesFromFile:
        total_bytes_read += 1
        window_bytes.append(b)
        if len(window_bytes) == bytes_per_window:
            total_compressed_bits += process_window(window_bytes)
            window_bytes.clear()
    # tidy up last window (if it's not empty)
    if len(window_bytes) > 0:
        print("Last window: NOT empty!")
        total_compressed_bits += process_window(window_bytes)
        window_bytes.clear()
    else:
        print("Last window: empty!")
    estimation_toc = time.perf_counter()
    print(f"Providing estimates took {estimation_toc - estimation_tic:0.4f} seconds")

    total_bits = total_bytes_read << 3
    print(f'total bytes (raw): {total_bytes_read}')
    total_compressed_bytes = total_compressed_bits // 8
    print(f'total bytes (compressed): {total_compressed_bytes}')
    print(f'ratio: {(100.0 * total_compressed_bits)/total_bits:0.2f}%')