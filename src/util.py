import math

from bitarray import bitarray
from bitarray import util as ba_util


def num_bits_required_to_represent(value: int) -> int:
    return 1 if value == 0 or value == 1 else math.floor(math.log2(value)) + 1


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
