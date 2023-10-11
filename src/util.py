from bitarray import bitarray
from bitarray import util as ba_util
import numpy as np

from bytes_analyser import BytesAnalyser

NUM_BYTES_FOR_PERSISTED_PARAMETERS = 2
MAX_PERSISTABLE_PARAMETER_VAL = (1 << (NUM_BYTES_FOR_PERSISTED_PARAMETERS * 8)) - 1


def write_val(_outfile, _analyser: BytesAnalyser, _val: int):
    """
    Write the supplied non-negative integer value to the specified output file.

    :param _outfile: the output file to write to.
    :param _analyser: the bytes analyser to update.
    :param _val: the non-negative integer value to write.
    """
    assert _val >= 0
    assert _val <= MAX_PERSISTABLE_PARAMETER_VAL
    write_bytes(_outfile, _analyser, _val.to_bytes(NUM_BYTES_FOR_PERSISTED_PARAMETERS, 'big'))


def write_bytes(_outfile, _analyser: BytesAnalyser, _bytes: bytes):
    """
    Write the supplied bytes to the specified output file.

    :param _outfile: the output file to write to.
    :param _analyser: the bytes analyser to update.
    :param _bytes: the bytes to write.
    """
    _outfile.write(_bytes)
    _analyser.update(_bytes)


def read_val(_infile, _analyser: BytesAnalyser) -> int:
    """
    Read an integer value from the specified input file.

    :param _infile: the input file to read from.
    :param _analyser: the bytes analyser to update.
    :return: the integer value read from the input file.
    """
    _result = read_bytes(_infile, _analyser, NUM_BYTES_FOR_PERSISTED_PARAMETERS)
    return int.from_bytes(_result, 'big')


def read_bytes(_infile, _bytes_analyser: BytesAnalyser, _num_bytes_to_read: int) -> bytes:
    """
    Read bytes from the specified input file.

    :param _infile: the input file to read from.
    :param _bytes_analyser: the bytes analyser to update.
    :param _num_bytes_to_read: the number of bytes to read.
    :return: the bytes read from the input file.
    """
    _result = _infile.read(_num_bytes_to_read)
    _bytes_analyser.update(_result)
    return _result


def num_bits_required_to_represent(value: int) -> int:
    """
    Computes the number of bits required to represent the supplied integer value. Note that we swerve the temptation of
    math.ceil(math.log2(value)) since it doesn't work for powers of 2.
    See: https://www.exploringbinary.com/number-of-bits-in-a-decimal-integer/

    :param value: the integer value of interest.
    :return: the number of bits required to represent the supplied integer value.
    """
    #return 1 if value == 0 or value == 1 else math.floor(math.log2(value)) + 1
    #return 1 if value < 2 else int(gmpy2.floor(gmpy2.log2(value))) + 1  ## slower, but handles big numbers
    return 1 if value < 2 else value.bit_length()

def get_index_set(bitset: bitarray) -> list:
    """
    Gets the index set of the supplied bitarray object. (A list of positions of "on" bits of the bitarray.)

    :param bitset: the bitarray of interest.
    :return: the index set of the supplied bitarray object.
    """
    return bitset.search(1)

def int_to_bitarray(value: int, length: int) -> bitarray:
    """
    Represents the supplied integer as a bitarray.

    :param value: the integer value of interest.
    :param length: the desired length of the returned bitarray.
    :return: a bitarray representing the supplied integer value.
    """
    #return ba_util.int2ba(value, length)
    return bitarray(format(value, f'0{length}b'))

def int_to_bitstring(value: int, length: int) -> str:
    """
    Represents the supplied integer as a bitstring

    :param value: the integer value of interest.
    :param length: the desired length of the returned string.
    :return: a bitstring representing the supplied integer value.
    """
    return format(value, f'0{length}b')
    #return np.binary_repr(value, length)

def bitarray_to_int(bitset: bitarray) -> int:
    """
    Interprets the supplied bitarray as an integer value.

    :param bitset: the bitarray of interest.
    :return: the integer value associated with the supplied bitarray.
    """
    #return ba_util.ba2int(bitset)
    result = 0
    i = len(bitset) - 1
    for bit in bitset:
        if bit:
            result |= (bit << i)
        i -= 1
    return result

def empty_bitarray(length: int) -> bitarray:
    """
    Generate an empty bitarray object.
    :param length: the length of interest.
    :return: an empty bitarray.
    """
    #return ba_util.zeros(length)
    bitset = bitarray(length)
    bitset.setall(0)
    return bitset

def gosper_rank(bitset: bitarray) -> int:
    """
    Use Gosper's Hack to rank the supplied bitset. The rank is simply the number of iterations before reaching the
    limit. For example, bitset 010110 requires 13 iterations before reaching the limit of 111000.

    :param bitset: the bitset of interest.
    :return: the rank of the supplied bitset.
    """
    mask = ba_util.ba2int(bitset)
    limit = (1 << len(bitset))
    result = -1
    while mask < limit:
        result += 1
        #  Gosper's hack:
        c = mask & -mask
        r = mask + c
        mask = int(((r ^ mask) >> 2) / c) | r
    return result


# Function to find maximum of x and y
def fast_max(x: int, y: int) -> int:
    """
    Compute the maximum of two integers.

    :param x: the first integer of interest.
    :param y: the second integer of interest.
    :return: the maximum of the supplied integers.
    """
    return x ^ ((x ^ y) & -(x < y))

