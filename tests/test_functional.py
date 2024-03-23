import random

import byte_util
import main
import util
from window_compressor import WindowCompressor
from window_decompressor import WindowDecompressor


def test_roundtrips():
    existence_index_set = set()
    existence_bitarray = util.empty_bitarray(256)
    for i in range(25):
        n = random.randint(main.DEFAULT_WINDOW_SIZE, main.MAX_WINDOW_SIZE)
        input_bytes = byte_util.random_sparse_bytes(n)
        compressor = WindowCompressor(n)
        compressed_bytes = compressor.process(input_bytes, existence_index_set)
        decompressor = WindowDecompressor(n)
        decompressed_bytes = decompressor.process(compressed_bytes, existence_bitarray)
        assert decompressed_bytes == input_bytes
