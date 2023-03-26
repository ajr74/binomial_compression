import random

from binomial import Binomial
from window_compressor import WindowCompressor
from window_decompressor import WindowDecompressor


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
        random_bytes = random_sparse_bytes(n)
        compressor = WindowCompressor(cache, n)
        compressed_bytes = compressor.process(random_bytes)
        decompressor = WindowDecompressor(cache, n)
        decompressed_bytes = decompressor.process(compressed_bytes)
        assert decompressed_bytes == random_bytes
