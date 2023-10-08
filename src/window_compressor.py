import gmpy2
from bitarray import bitarray

import util


class WindowCompressor:
    """
    A compressor for a window of arbitrary bytes.
    """

    def __init__(self, num_bytes_for_uncompressed_window: int):
        self.max_num_bits_for_window_size = util.num_bits_required_to_represent(num_bytes_for_uncompressed_window)

    def process(self, input_bytes: bytes) -> bytes:
        """
        Compresses the supplied bytes.

        :param input_bytes: the bytes of interest.
        :return: the compressed bytes.
        """
        num_bytes = len(input_bytes)
        num_bits_for_num_bytes = util.num_bits_required_to_represent(num_bytes)

        result = util.int_to_bitarray(num_bytes, self.max_num_bits_for_window_size)

        byte_positions = []
        for _ in range(256):
            byte_positions.append([])
        position = 0
        for b in input_bytes:
            byte_positions[b].append(position)
            position += 1

        existence_bitarray = bitarray()
        max_byte_count = 0
        for bp in byte_positions:
            _len = len(bp)
            if _len > max_byte_count:
                max_byte_count = _len
            existence_bitarray.append(_len > 0)

        result += existence_bitarray
        num_bits_for_k = util.num_bits_required_to_represent(max_byte_count)
        num_bits_for_k_bitarray = util.int_to_bitarray(num_bits_for_k, num_bits_for_num_bytes)
        result += num_bits_for_k_bitarray

        index_sets = []
        to_remove = util.empty_bitarray(num_bytes)
        for byte_val in range(256):
            if existence_bitarray[byte_val]:
                bitset = util.empty_bitarray(num_bytes)
                bitset[byte_positions[byte_val]] = 1
                to_remove2 = to_remove | bitset
                del bitset[to_remove]
                to_remove = to_remove2
                index_sets.append(util.get_index_set(bitset))

        k_cum = 0
        for index_set in index_sets[:-1]: # last element can be handled by inference
            compression_index = 0
            j = 1
            for position in index_set:
                compression_index += gmpy2.bincoef(position, j)
                j += 1

            k = len(index_set)
            max_payload_bits = util.num_bits_required_to_represent(gmpy2.bincoef(num_bytes - k_cum, k))
            appendable_data = util.int_to_bitarray(k, num_bits_for_k) + util.int_to_bitarray(compression_index, max_payload_bits)
            result += appendable_data
            k_cum += k

        return result.tobytes()
