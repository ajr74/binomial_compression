import byte_util
from window_compressor import WindowCompressor

def test_process_same_bytes():
    n = 1024
    compressor = WindowCompressor(n)
    compressed_bytes = compressor.process(byte_util.same_bytes(n, 13))
    assert compressed_bytes == b'\x80\x00\x10h\x0b'

def test_process_blocky():
    compressor = WindowCompressor(128)
    input_bytes = (byte_util.same_bytes(32, 13) +
                   byte_util.same_bytes(32, 3) +
                   byte_util.same_bytes(32, 230) +
                   byte_util.same_bytes(32, 107))
    compressed_bytes = compressor.process(input_bytes)
    assert compressed_bytes == b"\x80\x026AUh4\x00\x00\x00\x00\x00\x19n\xc9\xf2O\xb0BE\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10e\xbb'\xc9>\xc1\t\x14"