import util

from bitarray import bitarray


def test_num_bits_required_to_represent_0():
    assert util.num_bits_required_to_represent(0) == 1


def test_num_bits_required_to_represent_1():
    assert util.num_bits_required_to_represent(1) == 1


def test_num_bits_required_to_represent_small():
    assert util.num_bits_required_to_represent(101) == 7


def test_num_bits_required_to_represent_medium():
    assert util.num_bits_required_to_represent(58836830) == 26


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
