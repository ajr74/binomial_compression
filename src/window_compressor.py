import gmpy2

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

        byte_positions = [[] for _ in range(256)]
        for position, b in enumerate(input_bytes):
            byte_positions[b].append(position)


        existence_bitarray = util.empty_bitarray(256)
        max_byte_count = 0
        index_sets = []
        to_remove = util.empty_bitarray(num_bytes)
        for i, positions in enumerate(byte_positions):
            if positions:
                existence_bitarray[i] = 1
                max_byte_count = util.fast_max(max_byte_count, len(positions))
                bitset = util.empty_bitarray(num_bytes)
                bitset[positions] = 1
                to_remove2 = to_remove | bitset
                del bitset[to_remove]
                to_remove = to_remove2
                index_sets.append(util.get_index_set(bitset))

        result += existence_bitarray
        num_bits_for_k = util.num_bits_required_to_represent(max_byte_count)
        num_bits_for_k_bitstring = util.int_to_bitstring(num_bits_for_k, num_bits_for_num_bytes)
        result.extend(num_bits_for_k_bitstring)

        k_cum = 0
        for index_set in index_sets[:-1]: # last element can be handled by inference
            compression_index = 0
            for j, position in enumerate(index_set, 1):
                compression_index += gmpy2.bincoef(position, j)
            # Slightly slower:
            #compression_index = sum(gmpy2.bincoef(position, j) for j, position in enumerate(index_set, 1))

            k = len(index_set)
            max_payload_bits = util.num_bits_required_to_represent(gmpy2.bincoef(num_bytes - k_cum, k))
            result.extend(util.int_to_bitstring(k, num_bits_for_k) + util.int_to_bitstring(compression_index, max_payload_bits))
            k_cum += k
        return result.tobytes()
