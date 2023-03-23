import math
import os
import time

from binomial import Binomial
from bitarray import bitarray
from bitarray import util as ba_util
from stats_calculator import StatsCalculator

COMPRESS = True
DECOMPRESS = True


def get_index_set(bitset: bitarray) -> list:
    index_vals = []
    count = bitset.count()
    index = len(bitset)
    while count > 0:
        index = ba_util.rindex(bitset, 1, 0, index)
        index_vals.append(index)
        count -= 1
    index_vals.reverse()
    return index_vals


def get_index_set2(bitset: bitarray) -> list:
    return [index for index, b in enumerate(bitset) if b]


def compression_index_to_bitarray(index: int, k_val: int, num_bits: int) -> bitarray:
    result = bitarray(num_bits)
    result.setall(0)

    if k_val == 1:
        result[index] = 1
        return result

    target = index
    start = num_bits - 1
    for i in range(k_val, 0, -1):
        for j in range(start, -1, -1):
            b = C.get(j, i) if j >= i else 0
            if b <= target:
                result[j] = 1
                start = j
                target -= b
                break
        start -= 1
    return result


def num_bits_required_to_represent(value: int) -> int:
    return 1 if value == 0 or value == 1 else math.floor(math.log2(value)) + 1


def decompress(input_bytes: bytes, max_num_bits_for_window_size: int) -> bytes:

    input_bits = bitarray()
    input_bits.frombytes(input_bytes)

    start = 0
    finish = max_num_bits_for_window_size
    num_window_bytes = ba_util.ba2int(input_bits[start:finish])
    num_bits_for_max_k = num_bits_required_to_represent(num_window_bytes)

    start = finish
    finish += 256
    existence_bitarray = input_bits[start:finish]

    start = finish
    finish += num_bits_for_max_k
    num_bits_for_each_k_val = ba_util.ba2int(input_bits[start:finish])

    byte_val = 0
    byte_bitsets = []
    k_elapsed = 0

    existence_bitarray_count = existence_bitarray.count()
    counter = 1
    for bit in existence_bitarray:
        if bit:
            if counter < existence_bitarray_count:
                # read k
                start = finish
                finish += num_bits_for_each_k_val
                k = ba_util.ba2int(input_bits[start:finish])
                max_payload_bits = num_bits_required_to_represent(C.get(num_window_bytes - k_elapsed, k))
                # read compression index
                start = finish
                finish += max_payload_bits
                compression_index = ba_util.ba2int(input_bits[start:finish])
                res = compression_index_to_bitarray(compression_index, k, num_window_bytes - k_elapsed)
                byte_bitsets.append((byte_val, res))
                k_elapsed += k
            else:
                # final part can be inferred
                k_last = num_window_bytes - k_elapsed
                res = bitarray(k_last)
                res.setall(1)
                byte_bitsets.append((byte_val, res))
                k_elapsed += k_last
            counter += 1
        byte_val += 1
    assert k_elapsed == num_window_bytes

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
    result += ba_util.int2ba(num_bytes, max_num_bits_for_window_size)

    byte_positions = []
    for _ in range(0, 256):
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

    byte_bitsets = []
    to_remove = []
    for byte_val in range(0, 256):
        to_add = byte_positions[byte_val]
        if len(to_add) > 0:
            bitset = bitarray(num_bytes)
            bitset.setall(0)
            for i in to_add:
                bitset[i] = 1
            for i in to_remove:
                del bitset[i]
            to_remove += to_add
            to_remove.sort(reverse=True)  # maintain in descending order to avoid reindexing as we delete
            byte_bitsets.append((byte_val, bitset))

    num_bits_for_k = num_bits_required_to_represent(max(byte_counts))
    num_bits_for_k_bitarray = ba_util.int2ba(num_bits_for_k, num_bits_for_num_bytes)
    result += num_bits_for_k_bitarray

    k_elapsed = 0
    for _, bitset in byte_bitsets[:-1]:  # last element can be handled by inference
        compression_index = 0
        pos_list = get_index_set(bitset)
        j = 1
        for position in pos_list:
            if position >= j:
                compression_index += C.get(position, j)
            j += 1

        k = len(pos_list)
        max_payload_bits = num_bits_required_to_represent(C.get(num_bytes - k_elapsed, k))
        appendable_data = ba_util.int2ba(k, num_bits_for_k) + ba_util.int2ba(compression_index, max_payload_bits)
        result += appendable_data
        k_elapsed += k

    return result.tobytes()


if __name__ == '__main__':

    # TODO get params from command-line args.
    bytes_per_window = 1024
    num_bits_for_bytes_per_window = num_bits_required_to_represent(bytes_per_window)
    input_path = 'data/bible.txt'
    output_path = 'data/result.bin'
    reassemble_path = 'data/reassemble.bin'

    cache_builder_tic = time.perf_counter()
    C = Binomial(bytes_per_window + 1)
    cache_builder_toc = time.perf_counter()
    print(f"Setting up binomial coefficient cache took {cache_builder_toc - cache_builder_tic:0.4f} seconds")

    if COMPRESS:
        compression_tic = time.perf_counter()
        total_bytes_read = 0
        total_compressed_bytes = 0
        num_bytes_for_writing_num_window_bytes = 2
        in_stats = StatsCalculator()
        out_stats = StatsCalculator()

        with open(input_path, 'rb') as input_file, open(output_path, 'wb') as output_file:
            in_buffer_bytes = input_file.read(bytes_per_window)
            in_stats.update(in_buffer_bytes)
            while in_buffer_bytes:
                total_bytes_read += len(in_buffer_bytes)
                compressed_bytes = compress(in_buffer_bytes, num_bits_for_bytes_per_window)
                num_compressed_bytes = len(compressed_bytes)
                total_compressed_bytes += num_bytes_for_writing_num_window_bytes + num_compressed_bytes
                num_compressed_bytes_as_bytes = num_compressed_bytes.to_bytes(num_bytes_for_writing_num_window_bytes, 'big')
                output_file.write(num_compressed_bytes_as_bytes)
                out_stats.update(num_compressed_bytes_as_bytes)
                output_file.write(compressed_bytes)
                out_stats.update(compressed_bytes)
                in_buffer_bytes = input_file.read(bytes_per_window)
                in_stats.update(in_buffer_bytes)
            original_md5_bytes = in_stats.compute_md5_bytes()
            output_file.write(original_md5_bytes)  # append the original 16-byte MD5 to the very end of the file.
            out_stats.update(original_md5_bytes)
            total_compressed_bytes += 16

        print(f'Input MD5: {in_stats.compute_md5_hex()}')
        print(f'Input Shannon entropy: {in_stats.compute_shannon_entropy():0.6f}')
        print(f'Output MD5: {out_stats.compute_md5_hex()}')
        print(f'Output Shannon entropy: {out_stats.compute_shannon_entropy():0.6f}')

        compression_toc = time.perf_counter()
        print(f"Compressing took {compression_toc - compression_tic:0.4f} seconds")

        print(f'total bytes (raw): {total_bytes_read}')
        print(f'total bytes (compressed): {total_compressed_bytes}')
        print(f'space saving: {100 * (1 - total_compressed_bytes / total_bytes_read):0.2f}%')

    # Try reading back

    if DECOMPRESS:
        num_bytes_read = 0
        decompression_tic = time.perf_counter()
        file_size = os.stat(output_path).st_size
        rehydrate_stats = StatsCalculator()
        with open(output_path, 'rb') as output_file, open(reassemble_path, 'wb') as reassemble_file:
            size_bytes = output_file.read(2)  # TODO remove hard-coded stuff
            while size_bytes:
                size = int.from_bytes(size_bytes, 'big')
                payload_bytes = output_file.read(size)
                num_bytes_read += 2 + len(payload_bytes)  # TODO remove hard-coded stuff
                decompressed_bytes = decompress(payload_bytes, num_bits_for_bytes_per_window)
                rehydrate_stats.update(decompressed_bytes)
                reassemble_file.write(decompressed_bytes)
                if num_bytes_read == file_size - 16:
                    published_digest_bytes = output_file.read(16)
                    num_bytes_read += 16
                size_bytes = output_file.read(2)  # TODO remove hard-coded stuff
            computed_digest_bytes = rehydrate_stats.compute_md5_bytes()

        assert computed_digest_bytes == published_digest_bytes
        decompression_toc = time.perf_counter()
        print(f'Decompressing took {decompression_toc - decompression_tic:0.4f} seconds')
        print(f'Reconstituted MD5: {rehydrate_stats.compute_md5_hex()}')

        print(f"Num compressed bytes read back in: {num_bytes_read}")
