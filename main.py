import bisect
import math
import time

from bitarray import bitarray
from bitarray import util


def get_index_set(bitset: bitarray) -> list:
    index_vals = []
    count = bitset.count()
    index = len(bitset)
    while count > 0:
        index = util.rindex(bitset, 1, 0, index)
        index_vals.insert(0, index)
        count -= 1
    return index_vals


def num_bits_required_to_represent(value: int) -> int:
    assert value >= 0
    if value == 0 or value == 1:
        return 1
    return math.floor(math.log2(value)) + 1


def int_to_bitarray(value: int, length: int) -> bitarray:
    # TODO - inline
    assert value >= 0
    return util.int2ba(value, length)


def bitarray_to_int(bitset: bitarray) -> int:
    # TODO - check. Then inline.
    return util.ba2int(bitset)


def compress(input_bytes, buffer: bitarray, reverse=False) -> int:
    num_bytes = len(input_bytes)
    num_bits_for_num_bytes = num_bits_required_to_represent(num_bytes)

    byte_positions = []
    for i in range(0, 256):
        byte_positions.append([])
    byte_counts = [0] * 256
    position = 0
    for b in input_bytes:
        byte_counts[b] += 1
        byte_positions[b].append(position)
        position += 1

    existence_bitarray = bitarray()
    for c in byte_counts:
        existence_bitarray.append(c > 0)
    buffer += existence_bitarray
    num_compressed_bits = 256

    byte_bitsets = []
    to_remove = []
    for byte_val in range(0, 256):
        to_add = byte_positions[byte_val]
        if len(to_add) > 0:
            bitset = bitarray(num_bytes)
            bitset.setall(0)
            for i in to_add:
                bitset[i] = 1
            for i in to_remove[::-1]:  # remove from the end of bitset to avoid adjusting index values
                bitset.pop(i)
            for i in to_add:
                bisect.insort(to_remove, i)  # add to_add to to_remove, keeping to_remove sorted
            byte_bitsets.append((byte_val, bitset))

    # compute compression index values and update buffer
    total_percentage = 0

    num_bits_for_k = num_bits_required_to_represent(max(byte_counts))
    num_bits_for_k_bitarray = int_to_bitarray(num_bits_for_k, num_bits_for_num_bytes)
    buffer += num_bits_for_k_bitarray
    num_compressed_bits += num_bits_for_num_bytes  # TODO - check this paragraph

    k_elapsed = 0
    for _, bitset in byte_bitsets:
        compression_index = 0
        pos_list = get_index_set(bitset)
        j = 1
        for position in pos_list:
            if position >= j:
                compression_index += C[position][j]
            j += 1

        num_index_bits = num_bits_required_to_represent(compression_index)
        _k = len(pos_list)

        percentage = (100.0 * _k) / num_bytes
        total_percentage += percentage
        max_payload_bits = num_bits_required_to_represent(C[num_bytes - k_elapsed][_k])
        assert max_payload_bits >= num_index_bits
        appendable_data = int_to_bitarray(_k, num_bits_for_k) + int_to_bitarray(compression_index, max_payload_bits)
        num_compressed_bits += len(appendable_data)
        buffer += appendable_data
        k_elapsed += _k

    # try reversing
    if reverse:
        occupied_positions = bitarray(num_bytes)
        occupied_positions.setall(0)
        rehydrated_bytes = [0] * num_bytes
        for byte_val, bitset in byte_bitsets:
            inner_i = 0
            for outer_i in range(0, num_bytes):
                if occupied_positions[outer_i]:
                    continue
                if bitset[inner_i]:
                    rehydrated_bytes[outer_i] = byte_val
                    occupied_positions[outer_i] = 1
                inner_i += 1
        assert rehydrated_bytes == input_bytes
        
    assert total_percentage > 99.8
    assert k_elapsed == num_bytes
    return num_compressed_bits


if __name__ == '__main__':

    # TODO get params from command-line args
    bytes_per_window = 1024
    input_path = 'data/treasure_island.txt'
    output_path = 'data/result.bin'

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

    compression_tic = time.perf_counter()
    total_bytes_read = 0
    total_compressed_bits = 0

    out_buffer_bitarray = bitarray()
    with open(input_path, 'rb') as input_file, open(output_path, 'wb') as output_file:
        in_buffer_bytes = input_file.read(bytes_per_window)
        while in_buffer_bytes:
            total_bytes_read += len(in_buffer_bytes)
            total_compressed_bits += compress(in_buffer_bytes, out_buffer_bitarray)
            rubicon = (len(out_buffer_bitarray) // 8) << 3
            output_file.write(out_buffer_bitarray[:rubicon].tobytes())
            out_buffer_bitarray = out_buffer_bitarray[rubicon:]
            in_buffer_bytes = input_file.read(bytes_per_window)

    compression_toc = time.perf_counter()
    print(f"Compressing took {compression_toc - compression_tic:0.4f} seconds")

    total_bits = total_bytes_read << 3
    print(f'total bytes (raw): {total_bytes_read}')
    total_compressed_bytes = total_compressed_bits // 8
    print(f'total bytes (compressed): {total_compressed_bytes}')
    print(f'space saving: {100 * (1 - total_compressed_bits / total_bits):0.2f}%')
    