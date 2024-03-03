import byte_util
from window_compressor import WindowCompressor

def test_process_same_bytes():
    n = 1024
    compressor = WindowCompressor(n)
    compressed_bytes = compressor.process(byte_util.same_bytes(n, 13))
    assert compressed_bytes == b'\x80A\xa0,'

def test_process_blocky():
    compressor = WindowCompressor(128)
    input_bytes = (byte_util.same_bytes(32, 13) +
                   byte_util.same_bytes(32, 3) +
                   byte_util.same_bytes(32, 230) +
                   byte_util.same_bytes(32, 107))
    compressed_bytes = compressor.process(input_bytes)
    assert compressed_bytes == b'\x81\x1b \xaa\xb4\x1a\x00\x00\x00\x00\x00\x0c\xb7d\xf9\'\xd8!"\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x082\xdd\x93\xe4\x9f`\x84\x8a'