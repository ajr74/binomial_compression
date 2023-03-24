import math

from bitarray import bitarray
from bitarray import util as ba_util

from stats_calculator import StatsCalculator

NUM_BYTES_FOR_PERSISTED_PARAMETERS = 2
MAX_PERSISTABLE_PARAMETER_VAL = (1 << (NUM_BYTES_FOR_PERSISTED_PARAMETERS * 8)) - 1


def write_val(_outfile, _calc: StatsCalculator, _val: int):
    """
    Write the supplied non-negative integer value to the specified output file.

    :param _outfile: the output file to write to.
    :param _calc: the stats calculator to update.
    :param _val: the non-negative integer value to write.
    """
    assert _val >= 0
    assert _val <= MAX_PERSISTABLE_PARAMETER_VAL
    write_bytes(_outfile, _calc, _val.to_bytes(NUM_BYTES_FOR_PERSISTED_PARAMETERS, 'big'))


def write_bytes(_outfile, _calc: StatsCalculator, _bytes: bytes):
    """
    Write the supplied bytes to the specified output file.

    :param _outfile: the output file to write to.
    :param _calc: the stats calculator to update.
    :param _bytes: the bytes to write.
    """
    _outfile.write(_bytes)
    _calc.update(_bytes)


def read_val(_infile, _calc: StatsCalculator) -> int:
    """
    Read an integer value from the specified input file.

    :param _infile: the input file to read from.
    :param _calc: the stats calculator to update.
    :return: the integer value read from the input file.
    """
    _result = read_bytes(_infile, _calc, NUM_BYTES_FOR_PERSISTED_PARAMETERS)
    return int.from_bytes(_result, 'big')


def read_bytes(_infile, _calc: StatsCalculator, _num_bytes_to_read: int) -> bytes:
    """
    Read bytes from the specified input file.

    :param _infile: the input file to read from.
    :param _calc: the stats calculator to update.
    :param _num_bytes_to_read: the number of bytes to read.
    :return: the bytes read from the input file.
    """
    _result = _infile.read(_num_bytes_to_read)
    _calc.update(_result)
    return _result


def num_bits_required_to_represent(value: int) -> int:
    """
    Computes the number of bits required to represent the supplied integer value. Note that we swerve the temptation of
    math.ceil(math.log2(value)) since it doesn't work for powers of 2.
    See: https://www.exploringbinary.com/number-of-bits-in-a-decimal-integer/

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
