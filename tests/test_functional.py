import random

import util
from binomial import Binomial
from compressor import Compressor
from decompressor import Decompressor


def random_sparse_bytes(n: int) -> bytearray:
    result = bytearray(n)
    for i in range(0, n):
        if random.randint(1, 10) > 7:
            result[i] = random.randint(0, 255)
    return result


def test_roundtrips():
    cache = Binomial(1001)
    for i in range(0, 10):
        n = random.randint(500, 1000)
        m = util.num_bits_required_to_represent(n)
        random_bytes = random_sparse_bytes(n)
        compressor = Compressor(binomial_coefficient_cache=cache)
        compressed_bytes = compressor.compress(random_bytes, m)
        decompressor = Decompressor(binomial_coefficient_cache=cache)
        decompressed_bytes = decompressor.decompress(compressed_bytes, m)
        assert decompressed_bytes == random_bytes
