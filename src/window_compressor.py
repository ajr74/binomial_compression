import gmpy2
from bitarray import bitarray

import util


def index_set_to_compression_index(index_set: list) -> int:
    """
    Compute a compression index for the index set of a bitarray.
    :param index_set: the index set of interest.
    :return: a compression index for the supplied index set.
    """
    compression_index = 0
    for j, position in enumerate(index_set, 1):
        compression_index += gmpy2.bincoef(position, j)
    # Slightly slower:
    # compression_index = sum(gmpy2.bincoef(position, j) for j, position in enumerate(index_set, 1))
    return compression_index


def index_set_to_compression_index_alternative(index_set: list) -> int:
    """
    Compute a compression index for the index set of a bitarray. No calls to gmpy2.bincoef, instead falling factorials.
    :param index_set: the index set of interest.
    :return: a compression index for the supplied index set.
    """
    j = len(index_set)
    compression_index = 0

    multiplier = 1
    for position in reversed(index_set):
        compression_index += (multiplier * util.falling_factorial(position, j))
        multiplier *= j
        j -= 1
    compression_index //= gmpy2.fac(len(index_set))
    return compression_index


class WindowCompressor:
    """
    A compressor for a window of arbitrary bytes.
    """

    def __init__(self, num_bytes_for_uncompressed_window: int):
        self.window_size = num_bytes_for_uncompressed_window

    def process(self, input_bytes: bytes, existence_index_set: set) -> bytes:
        """
        Compresses the supplied bytes.

        :param input_bytes: the bytes of interest.
        :param existence_index_set: the existence index set from the previous window.
        :return: the compressed bytes.
        """
        num_bytes = len(input_bytes)
        num_bits_for_num_bytes = util.num_bits_required_to_represent(num_bytes)

        if num_bytes == self.window_size:
            result = bitarray('1')
        else:
            result = bitarray('0') + util.int_to_bitarray(num_bytes, util.num_bits_required_to_represent(self.window_size))

        byte_positions = [[] for _ in range(256)]
        for position, b in enumerate(input_bytes):
            byte_positions[b].append(position)

        existence_index_list = list(existence_index_set)
        max_byte_count = 0
        index_sets = []
        to_remove = util.empty_bitarray(num_bytes)
        for b, positions in enumerate(byte_positions):
            if positions:
                if b in existence_index_set:
                    existence_index_list.remove(b)
                else:
                    existence_index_list.append(b)
                existence_index_set.add(b)
                max_byte_count = util.fast_max(max_byte_count, len(positions))
                bitset = util.empty_bitarray(num_bytes)
                bitset[positions] = 1
                to_remove2 = to_remove | bitset
                del bitset[to_remove]
                to_remove = to_remove2
                index_sets.append(util.get_index_set(bitset))
            else:
                existence_index_set.discard(b)

        existence_index_list.sort()
        existence_count = len(existence_index_list)
        max_compression_index_bits = util.num_bits_required_to_represent(gmpy2.bincoef(256, existence_count))
        existence_compression_index = index_set_to_compression_index(existence_index_list)
        # 9 bits to cover the inclusive range [0, 256] for existence_bitarray_count
        result.extend(util.int_to_bitstring(existence_count, 9) +
                      util.int_to_bitstring(existence_compression_index, max_compression_index_bits))

        num_bits_for_k = util.num_bits_required_to_represent(max_byte_count)
        num_bits_for_k_bitstring = util.int_to_bitstring(num_bits_for_k, num_bits_for_num_bytes)
        result.extend(num_bits_for_k_bitstring)

        n_payload = num_bytes
        for index_set in index_sets[:-1]:  # last element can be handled by inference
            compression_index = index_set_to_compression_index(index_set)
            k = len(index_set)
            max_payload_bits = util.num_bits_required_to_represent(gmpy2.bincoef(n_payload, k))
            result.extend(util.int_to_bitstring(k, num_bits_for_k) + util.int_to_bitstring(compression_index, max_payload_bits))
            n_payload -= k
        return result.tobytes()
