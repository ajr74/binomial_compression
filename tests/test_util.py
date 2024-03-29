import gmpy2
from bitarray import bitarray

import util


def test_num_bits_required_to_represent_0():
    assert util.num_bits_required_to_represent(0) == 1


def test_num_bits_required_to_represent_1():
    assert util.num_bits_required_to_represent(1) == 1


def test_num_bits_required_to_represent_small():
    assert util.num_bits_required_to_represent(101) == 7


def test_num_bits_required_to_represent_medium():
    assert util.num_bits_required_to_represent(58836830) == 26


def test_num_bits_required_to_represent_power_of_2():
    assert util.num_bits_required_to_represent(32768) == 16


def test_num_bits_required_to_represent_large():
    assert util.num_bits_required_to_represent(908982380823098239287298972983923) == 110


def test_get_index_set_empty():
    assert util.get_index_set(bitarray()) == []


def test_get_index_set_all_ones():
    assert util.get_index_set(bitarray('11111')) == [0, 1, 2, 3, 4]


def test_get_index_set_all_zeroes():
    assert util.get_index_set(bitarray('00000')) == []


def test_get_index_set_low_cardinality():
    assert util.get_index_set(bitarray('00000101000')) == [5, 7]


def test_get_index_set_high_cardinality():
    assert util.get_index_set(bitarray('11101001111')) == [0, 1, 2, 4, 7, 8, 9, 10]


def test_gosper_rank():
    assert util.gosper_rank(bitarray('000111')) == 19
    assert util.gosper_rank(bitarray('010110')) == 13
    assert util.gosper_rank(bitarray('111000')) == 0


def test_binomial_coefficients_n_less_than_k():
    assert gmpy2.bincoef(5, 10) == 0


def test_bitarray_to_int_zero():
    assert util.bitarray_to_int(bitarray('00000')) == 0


def test_bitarray_to_int_nonzero():
    assert util.bitarray_to_int(bitarray('01100010001110101011000111')) == 25750215


def test_int_to_bitarray_zero():
    assert util.int_to_bitarray(0, 5) == bitarray('00000')


def test_int_to_bitarray_non_zero():
    assert util.int_to_bitarray(25750215, 28) == bitarray('0001100010001110101011000111')


def test_int_to_bitstring_zero():
    assert util.int_to_bitstring(0, 5) == '00000'


def test_int_to_bitstring_non_zero():
    assert util.int_to_bitstring(25750215, 28) == '0001100010001110101011000111'


def test_empty_bitarray():
    bitset = util.empty_bitarray(17)
    assert bitset.count(1) == 0
    assert bitset.count(0) == 17


def test_fast_max():
    assert util.fast_max(11, 5) == 11
    assert util.fast_max(5, 11) == 11
    assert util.fast_max(11, 11) == 11


def test_full_bitarray():
    bitset = util.full_bitarray(13)
    assert bitset.count(1) == 13
    assert bitset.count(0) == 0


def test_falling_factorial():
    assert util.falling_factorial(5, 0) == 1
    assert util.falling_factorial(5, 1) == 5
    assert util.falling_factorial(5, 2) == 20
    assert util.falling_factorial(5, 3) == 60
    assert util.falling_factorial(5, 4) == 120
    assert util.falling_factorial(5, 5) == 120
    assert util.falling_factorial(5, 6) == 0
    assert util.falling_factorial(5, 42) == 0
