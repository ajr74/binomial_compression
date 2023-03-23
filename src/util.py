import math

from bitarray import bitarray
from bitarray import util as ba_util


def num_bits_required_to_represent(value: int) -> int:
    """
    Computes the number of bits required to represent the supplied integer value. Note that we swerve the temptation of
    math.ceil(math.log2(value)) since it doesn't work for powers of 2.

    :param value: the integer value of interest.
    :return: the number of bits required to represent the supplied integer value.
    """
    return 1 if value == 0 or value == 1 else math.floor(math.log2(value)) + 1


def get_index_set(bitset: bitarray) -> list:
    """
    Gets the index set of the supplied bitarray object. (A list of positions of "on" bits of the bitarray.)

    :param bitset: the bitarray of interest.
    :return: the index set of the supplied bitarray object.
    """
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
    """
    A seemingly slower variant of get_index_set().

    :param bitset: the bitarray of interest.
    :return: the index set of the supplied bitarray object.
    """
    return [index for index, b in enumerate(bitset) if b]
