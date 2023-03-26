from bitarray import bitarray
from bitarray import util as ba_util

import util
from binomial import Binomial


class WindowCompressor:
    """
    A compressor for a window of arbitrary bytes.
    """

    def __init__(self, binomial_coefficient_cache: Binomial, num_bytes_for_uncompressed_window: int):
        self.bc_cache = binomial_coefficient_cache
        self.max_num_bits_for_window_size = util.num_bits_required_to_represent(num_bytes_for_uncompressed_window)

    def process(self, input_bytes: bytes) -> bytes:
        """
        Compresses the supplied bytes.

        :param input_bytes: the bytes of interest.
        :return: the compressed bytes.
        """
        num_bytes = len(input_bytes)
        num_bits_for_num_bytes = util.num_bits_required_to_represent(num_bytes)

        result = bitarray()
        result += ba_util.int2ba(num_bytes, self.max_num_bits_for_window_size)

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

        num_bits_for_k = util.num_bits_required_to_represent(max(byte_counts))
        num_bits_for_k_bitarray = ba_util.int2ba(num_bits_for_k, num_bits_for_num_bytes)
        result += num_bits_for_k_bitarray

        k_cum = 0
        for _, bitset in byte_bitsets[:-1]:  # last element can be handled by inference
            compression_index = 0
            pos_list = util.get_index_set(bitset)
            j = 1
            for position in pos_list:
                compression_index += self.bc_cache.get(position, j)
                j += 1

            k = len(pos_list)
            max_payload_bits = util.num_bits_required_to_represent(self.bc_cache.get(num_bytes - k_cum, k))
            appendable_data = ba_util.int2ba(k, num_bits_for_k) + ba_util.int2ba(compression_index, max_payload_bits)
            result += appendable_data
            k_cum += k

        return result.tobytes()
