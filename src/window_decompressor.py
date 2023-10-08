import gmpy2
from bitarray import bitarray

import util


def compression_index_to_bitarray(index: int, k_val: int, num_bits: int) -> bitarray:
    """
    Converts the supplied compression index to a decompressed bitarray.

    :param index: the index value of interest.
    :param k_val: the k parameter of interest.
    :param num_bits: the number of bits for the resultant bitarray.
    :return: the decompressed index as a bitarray.
    """
    result = util.empty_bitarray(num_bits)

    if k_val == 1:
        result[index] = 1
        return result

    target = index
    start = num_bits - 1
    for i in range(k_val, 0, -1):
        for j in range(start, -1, -1):
            b = gmpy2.bincoef(j, i)
            if b <= target:
                result[j] = 1
                start = j
                target -= b
                break
        start -= 1
    return result


class WindowDecompressor:
    """
    A decompressor for a window of compressed bytes.
    """

    def __init__(self, num_bytes_for_uncompressed_window: int):
        self.max_num_bits_for_window_size = util.num_bits_required_to_represent(num_bytes_for_uncompressed_window)

    def process(self, input_bytes: bytes) -> bytes:
        """
        Decompresses the supplied bytes.

        :param input_bytes: the bytes of interest.
        :return: the decompressed bytes.
        """
        input_bits = bitarray()
        input_bits.frombytes(input_bytes)

        start = 0
        finish = self.max_num_bits_for_window_size
        num_window_bytes = util.bitarray_to_int(input_bits[start:finish])
        num_bits_for_max_k = util.num_bits_required_to_represent(num_window_bytes)

        start = finish
        finish += 256
        existence_bitarray = input_bits[start:finish]

        start = finish
        finish += num_bits_for_max_k
        num_bits_for_each_k_val = util.bitarray_to_int(input_bits[start:finish])

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
                    k = util.bitarray_to_int(input_bits[start:finish])
                    max_payload_bits = util.num_bits_required_to_represent(gmpy2.bincoef(num_window_bytes - k_cum, k))
                    # read compression index
                    start = finish
                    finish += max_payload_bits
                    compression_index = util.bitarray_to_int(input_bits[start:finish])
                    result = compression_index_to_bitarray(compression_index, k, num_window_bytes - k_cum)
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

        occupied_positions = util.empty_bitarray(num_window_bytes)
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
