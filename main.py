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


def compression_index_to_bitarray(index: int, k_val: int, num_bits: int) -> bitarray:
    target = index
    start = num_bits - 1
    result = bitarray(num_bits)
    result.setall(0)
    for i in range(k_val, 0, -1):
        for j in range(start, -1, -1):
            b = 0
            if j >= i:
                b = C[j][i]  # TODO util method: binm(j, i)
            if b <= target:
                result[j] = 1
                start = j  # EXPERIMENTAL, but seemingly okay :)
                target -= b
                break
        start -= 1
    return result


def num_bits_required_to_represent(value: int) -> int:
    assert value >= 0
    if value == 0 or value == 1:
        return 1
    return math.floor(math.log2(value)) + 1


def int_to_bitarray(value: int, length: int) -> bitarray:
    # TODO - inline.
    assert value >= 0
    return util.int2ba(value, length)


def bitarray_to_int(bitset: bitarray) -> int:
    # TODO - check. Then inline.
    return util.ba2int(bitset)


def decompress(input_bytes: bytes, max_num_bits_for_window_size: int) -> bytes:

    tmp = bitarray()
    tmp.frombytes(input_bytes)

    start = 0
    finish = max_num_bits_for_window_size
    num_window_bytes = bitarray_to_int(tmp[start:finish])
    num_bits_for_max_k = num_bits_required_to_represent(num_window_bytes)

    start = finish
    finish += 256
    existence_bitarray = tmp[start:finish]

    start = finish
    finish += num_bits_for_max_k
    num_bits_for_each_k_val = bitarray_to_int(tmp[start:finish])

    byte_val = 0
    byte_bitsets = []
    k_elapsed = 0

    for bit in existence_bitarray:
        if bit:
            # read k
            start = finish
            finish += num_bits_for_each_k_val
            _k = bitarray_to_int(tmp[start:finish])
            max_payload_bits = num_bits_required_to_represent(C[num_window_bytes - k_elapsed][_k])

            # read compression index
            start = finish
            finish += max_payload_bits
            compression_index = bitarray_to_int(tmp[start:finish])
            res = compression_index_to_bitarray(compression_index, _k, num_window_bytes - k_elapsed)
            byte_bitsets.append((byte_val, res))
            k_elapsed += _k

        byte_val += 1

    occupied_positions = bitarray(num_window_bytes)
    occupied_positions.setall(0)
    rehydrated_bytes = [0] * num_window_bytes
    for byte_val, bitset in byte_bitsets:
        inner_i = 0
        for outer_i in range(0, num_window_bytes):
            if occupied_positions[outer_i]:
                continue
            if bitset[inner_i]:
                rehydrated_bytes[outer_i] = byte_val
                occupied_positions[outer_i] = 1
            inner_i += 1

    return bytes(rehydrated_bytes)


def compress(input_bytes: bytes, max_num_bits_for_window_size: int) -> bytes:
    num_bytes = len(input_bytes)
    num_bits_for_num_bytes = num_bits_required_to_represent(num_bytes)

    result = bitarray()
    result += int_to_bitarray(num_bytes, max_num_bits_for_window_size)

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
    result += existence_bitarray
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
            for i in to_remove[::-1]:  # Remove from the end of bitset to avoid adjusting index values.
                bitset.pop(i)
            for i in to_add:
                bisect.insort(to_remove, i)  # Add 'to_add' to 'to_remove', keeping 'to_remove' sorted.
            byte_bitsets.append((byte_val, bitset))

    num_bits_for_k = num_bits_required_to_represent(max(byte_counts))
    num_bits_for_k_bitarray = int_to_bitarray(num_bits_for_k, num_bits_for_num_bytes)
    result += num_bits_for_k_bitarray
    num_compressed_bits += num_bits_for_num_bytes  # TODO - check this paragraph.

    k_elapsed = 0
    for _, bitset in byte_bitsets:
        compression_index = 0
        pos_list = get_index_set(bitset)
        j = 1
        for position in pos_list:
            if position >= j:
                compression_index += C[position][j]
            j += 1

        _k = len(pos_list)
        max_payload_bits = num_bits_required_to_represent(C[num_bytes - k_elapsed][_k])
        appendable_data = int_to_bitarray(_k, num_bits_for_k) + int_to_bitarray(compression_index, max_payload_bits)  # TODO - do we need to write the last payload? It's seemingly always 0.
        num_compressed_bits += len(appendable_data)
        result += appendable_data
        k_elapsed += _k

    return result.tobytes()


if __name__ == '__main__':

    # TODO get params from command-line args.
    bytes_per_window = 1024 * 2
    num_bits_for_bytes_per_window = num_bits_required_to_represent(bytes_per_window)
    input_path = 'data/result1.bin'
    output_path = 'data/result.bin'
    reassemble_path = 'data/reassemble.bin'

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
    total_compressed_bytes = 0
    num_bytes_for_writing_num_window_bytes = 2

    with open(input_path, 'rb') as input_file, open(output_path, 'wb') as output_file:
        in_buffer_bytes = input_file.read(bytes_per_window)
        while in_buffer_bytes:
            total_bytes_read += len(in_buffer_bytes)
            compressed_bytes = compress(in_buffer_bytes, num_bits_for_bytes_per_window)
            num_compressed_bytes = len(compressed_bytes)
            total_compressed_bytes += num_bytes_for_writing_num_window_bytes + num_compressed_bytes
            num_compressed_bytes_as_bytes = num_compressed_bytes.to_bytes(num_bytes_for_writing_num_window_bytes, 'big')
            output_file.write(num_compressed_bytes_as_bytes)
            output_file.write(compressed_bytes)
            in_buffer_bytes = input_file.read(bytes_per_window)

    compression_toc = time.perf_counter()
    print(f"Compressing took {compression_toc - compression_tic:0.4f} seconds")

    total_bits = total_bytes_read << 3
    print(f'total bytes (raw): {total_bytes_read}')
    print(f'total bytes (compressed): {total_compressed_bytes}')
    print(f'space saving: {100 * (1 - total_compressed_bytes / total_bytes_read):0.2f}%')

    # Try reading back

    num_bytes_read = 0
    decompression_tic = time.perf_counter()
    with open(output_path, 'rb') as output_file, open(reassemble_path, 'wb') as reassemble_file:
        size_bytes = output_file.read(2)
        while size_bytes:
            size = int.from_bytes(size_bytes, 'big')
            payload_bytes = output_file.read(size)
            num_bytes_read += 2 + len(payload_bytes)
            reassemble_file.write(decompress(payload_bytes, num_bits_for_bytes_per_window))
            size_bytes = output_file.read(2)

    decompression_toc = time.perf_counter()
    print(f"Decompressing took {decompression_toc - decompression_tic:0.4f} seconds")

    print(f"Num bytes read back in: {num_bytes_read}")
