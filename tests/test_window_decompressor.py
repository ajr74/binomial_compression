import byte_util
import util
from window_decompressor import WindowDecompressor


def test_process_same_bytes():
    compressed_bytes = b'\x80A\xa0,'
    decompressor = WindowDecompressor(1024)
    existence_bitarray = util.empty_bitarray(256)
    decompressed_bytes = decompressor.process(compressed_bytes, existence_bitarray)
    assert decompressed_bytes == byte_util.same_bytes(1024, 13)


def test_process_blocky():
    compressed_bytes = b'\x81\x1b \xaa\xb4\x1a\x00\x00\x00\x00\x00\x0c\xb7d\xf9\'\xd8!"\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x082\xdd\x93\xe4\x9f`\x84\x8a'
    decompressor = WindowDecompressor(128)
    existence_bitarray = util.empty_bitarray(256)
    decompressed_bytes = decompressor.process(compressed_bytes, existence_bitarray)
    assert decompressed_bytes == (byte_util.same_bytes(32, 13) +
                                  byte_util.same_bytes(32, 3) +
                                  byte_util.same_bytes(32, 230) +
                                  byte_util.same_bytes(32, 107))
