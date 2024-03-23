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
            if (b := gmpy2.bincoef(j, i)) <= target:
                result[j] = 1
                start = j - 1
                target -= b
                break
    return result


def compression_index_to_bitarray_experimental(index: int, k_val: int, num_bits: int) -> bitarray:
    """
    Converts the supplied compression index to a decompressed bitarray. Uses a generator for binomial coefficients.

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
        j_plus_1 = start + 1
        b = int(gmpy2.bincoef(j_plus_1, i))
        for j in range(start, -1, -1):
            if (b := ((j_plus_1-i) * b) // j_plus_1) <= target:
                result[j] = 1
                start = j - 1
                target -= b
                break
            j_plus_1 = j
    return result


class WindowDecompressor:
    """
    A decompressor for a window of compressed bytes.
    """

    def __init__(self, num_bytes_for_uncompressed_window: int):
        self.window_size = num_bytes_for_uncompressed_window

    def process(self, input_bytes: bytes, existence_bitarray: bitarray) -> bytes:
        """
        Decompresses the supplied bytes.

        :param input_bytes: the bytes of interest.
        :param existence_bitarray: the existence bitarray from the previous window.
        :return: the decompressed bytes.
        """
        input_bits = bitarray()
        input_bits.frombytes(input_bytes)

        start = 0
        finish = 1
        if util.bitarray_to_int(input_bits[start:finish]):
            num_window_bytes = self.window_size
        else:
            start = finish
            finish += util.num_bits_required_to_represent(self.window_size)
            num_window_bytes = util.bitarray_to_int(input_bits[start:finish])
        num_bits_for_max_k = util.num_bits_required_to_represent(num_window_bytes)

        start = finish
        finish += 9  # 9 bits to cover the inclusive range [0, 256]
        existence_bitarray_count = util.bitarray_to_int(input_bits[start:finish])

        start = finish
        finish += util.num_bits_required_to_represent(gmpy2.bincoef(256, existence_bitarray_count))
        existence_bitarray_compression_index = util.bitarray_to_int(input_bits[start:finish])
        existence_bitarray ^= compression_index_to_bitarray(existence_bitarray_compression_index, existence_bitarray_count, 256)
        existence_bitarray_count = existence_bitarray.count(1)

        start = finish
        finish += num_bits_for_max_k
        num_bits_for_each_k_val = util.bitarray_to_int(input_bits[start:finish])

        byte_bitsets = []
        k_cum = 0

        counter = 1
        for byte_val in util.get_index_set(existence_bitarray):
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
        assert k_cum == num_window_bytes

        # Original::
        #occupied_positions = util.empty_bitarray(num_window_bytes)
        #rehydrated_bytes = bytearray(num_window_bytes)
        #for byte_val, bitset in byte_bitsets:
        #    inner_i = 0
        #    for outer_i in range(num_window_bytes):
        #        if occupied_positions[outer_i]:
        #            continue
        #        if bitset[inner_i]:
        #            rehydrated_bytes[outer_i] = byte_val
        #            occupied_positions[outer_i] = 1
        #        inner_i += 1

        # Alternative 1 (fastest)::
        unoccupied_positions = util.full_bitarray(num_window_bytes)
        rehydrated_bytes = bytearray(num_window_bytes)
        for byte_val, bitset in byte_bitsets:
            bitset_count = bitset.count(1)
            num_byte_assignments = 0
            for inner_i, outer_i in enumerate(util.get_index_set(unoccupied_positions)):
                if bitset[inner_i]:
                    num_byte_assignments += 1
                    rehydrated_bytes[outer_i] = byte_val
                    unoccupied_positions[outer_i] = 0
                    if num_byte_assignments == bitset_count:
                        break

        # Alternative 2 (fast)::
        #occupied_positions = util.empty_bitarray(num_window_bytes)
        #rehydrated_bytes = bytearray(num_window_bytes)
        #for byte_val, bitset in byte_bitsets:
        #    for inner_i, outer_i in enumerate(util.get_index_set(~occupied_positions)):
        #        if bitset[inner_i]:
        #            rehydrated_bytes[outer_i] = byte_val
        #            occupied_positions[outer_i] = 1


        # Alternative 3 (slowest)::
        #prev_bitset = util.empty_bitarray(num_window_bytes)
        #rehydrated_bytes = bytearray(num_window_bytes)
        #for byte_val, bitset in byte_bitsets:
        #    for i in util.get_index_set(prev_bitset):
        #        bitset.insert(i, 0)
        #    for i in util.get_index_set(bitset):
        #        rehydrated_bytes[i] = byte_val
        #    prev_bitset |= bitset


        # Alternative 4 (slow)::
        #prev_index_set = []
        #rehydrated_bytes = bytearray(num_window_bytes)
        #for byte_val, bitset in byte_bitsets:
        #    for i in prev_index_set:
        #        bitset.insert(i, 0)
        #    for i in util.get_index_set(bitset):
        #        rehydrated_bytes[i] = byte_val
        #        bisect.insort(prev_index_set, i)

        return rehydrated_bytes
