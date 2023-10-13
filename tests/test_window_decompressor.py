import byte_util
from window_decompressor import WindowDecompressor

def test_process_same_bytes():
    compressed_bytes = b'\x80\x00\x10h\x0b'
    decompressor = WindowDecompressor(1024)
    decompressed_bytes = decompressor.process(compressed_bytes)
    assert decompressed_bytes == byte_util.same_bytes(1024, 13)

def test_process_blocky():
    compressed_bytes = b"\x80\x026AUh4\x00\x00\x00\x00\x00\x19n\xc9\xf2O\xb0BE\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10e\xbb'\xc9>\xc1\t\x14"
    decompressor = WindowDecompressor(128)
    decompressed_bytes = decompressor.process(compressed_bytes)
    assert decompressed_bytes == (byte_util.same_bytes(32, 13) +
                   byte_util.same_bytes(32, 3) +
                   byte_util.same_bytes(32, 230) +
                   byte_util.same_bytes(32, 107))

