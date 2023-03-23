from bitarray import bitarray
from bitarray import util as ba_util

import util
from binomial import Binomial


class Decompressor:

    def __init__(self, binomial_coefficient_cache: Binomial):
        self.bc_cache = binomial_coefficient_cache

    def compression_index_to_bitarray(self, index: int, k_val: int, num_bits: int) -> bitarray:
        result = bitarray(num_bits)
        result.setall(0)

        if k_val == 1:
            result[index] = 1
            return result

        target = index
        start = num_bits - 1
        for i in range(k_val, 0, -1):
            for j in range(start, -1, -1):
                b = self.bc_cache.get(j, i) if j >= i else 0
                if b <= target:
                    result[j] = 1
                    start = j
                    target -= b
                    break
            start -= 1
        return result

    def decompress(self, input_bytes: bytes, max_num_bits_for_window_size: int) -> bytes:

        input_bits = bitarray()
        input_bits.frombytes(input_bytes)

        start = 0
        finish = max_num_bits_for_window_size
        num_window_bytes = ba_util.ba2int(input_bits[start:finish])
        num_bits_for_max_k = util.num_bits_required_to_represent(num_window_bytes)

        start = finish
        finish += 256
        existence_bitarray = input_bits[start:finish]

        start = finish
        finish += num_bits_for_max_k
        num_bits_for_each_k_val = ba_util.ba2int(input_bits[start:finish])

        byte_val = 0
        byte_bitsets = []
        k_cum = 0

        existence_bitarray_count = existence_bitarray.count()
        counter = 1
        for bit in existence_bitarray:
            if bit:
                if counter < existence_bitarray_count:
                    # read k
                    start = finish
                    finish += num_bits_for_each_k_val
                    k = ba_util.ba2int(input_bits[start:finish])
                    max_payload_bits = util.num_bits_required_to_represent(self.bc_cache.get(num_window_bytes - k_cum, k))
                    # read compression index
                    start = finish
                    finish += max_payload_bits
                    compression_index = ba_util.ba2int(input_bits[start:finish])
                    result = self.compression_index_to_bitarray(compression_index, k, num_window_bytes - k_cum)
                    byte_bitsets.append((byte_val, result))
                    k_cum += k
                else:
                    # final part can be inferred
                    k_last = num_window_bytes - k_cum
                    result = bitarray(k_last)
                    result.setall(1)
                    byte_bitsets.append((byte_val, result))
                    k_cum += k_last
                counter += 1
            byte_val += 1
        assert k_cum == num_window_bytes

        occupied_positions = bitarray(num_window_bytes)
        occupied_positions.setall(0)
        rehydrated_bytes = bytearray(num_window_bytes)
        for byte_val, bitset in byte_bitsets:
            inner_i = 0
            for outer_i in range(0, num_window_bytes):
                if occupied_positions[outer_i]:
                    continue
                if bitset[inner_i]:
                    rehydrated_bytes[outer_i] = byte_val
                    occupied_positions[outer_i] = 1
                inner_i += 1

        return rehydrated_bytes
