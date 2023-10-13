import random

import byte_util
import main
from window_compressor import WindowCompressor
from window_decompressor import WindowDecompressor

def test_roundtrips():
    for i in range(25):
        n = random.randint(main.DEFAULT_WINDOW_SIZE, main.MAX_WINDOW_SIZE)
        input_bytes = byte_util.random_sparse_bytes(n)
        compressor = WindowCompressor(n)
        compressed_bytes = compressor.process(input_bytes)
        decompressor = WindowDecompressor(n)
        decompressed_bytes = decompressor.process(compressed_bytes)
        assert decompressed_bytes == input_bytes
