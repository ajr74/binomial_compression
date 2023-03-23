import os
import time

import util
from binomial import Binomial
from compressor import Compressor
from decompressor import Decompressor
from stats_calculator import StatsCalculator

COMPRESS = True
DECOMPRESS = True


if __name__ == '__main__':

    # TODO get params from command-line args.
    bytes_per_window = 1024
    num_bits_for_bytes_per_window = util.num_bits_required_to_represent(bytes_per_window)
    input_path = 'data/bible.txt'
    output_path = 'data/result.bin'
    reassemble_path = 'data/reassemble.bin'

    cache_builder_tic = time.perf_counter()
    cache = Binomial(bytes_per_window + 1)
    cache_builder_toc = time.perf_counter()
    print(f"Setting up binomial coefficient cache took {cache_builder_toc - cache_builder_tic:0.4f} seconds")

    if COMPRESS:
        compression_tic = time.perf_counter()
        total_bytes_read = 0
        total_compressed_bytes = 0
        num_bytes_for_writing_num_window_bytes = 2
        in_stats = StatsCalculator()
        out_stats = StatsCalculator()

        compressor = Compressor(binomial_coefficient_cache=cache)
        with open(input_path, 'rb') as input_file, open(output_path, 'wb') as output_file:
            in_buffer_bytes = input_file.read(bytes_per_window)
            in_stats.update(in_buffer_bytes)
            while in_buffer_bytes:
                total_bytes_read += len(in_buffer_bytes)
                compressed_bytes = compressor.compress(in_buffer_bytes, num_bits_for_bytes_per_window)
                num_compressed_bytes = len(compressed_bytes)
                total_compressed_bytes += num_bytes_for_writing_num_window_bytes + num_compressed_bytes
                num_compressed_bytes_as_bytes = num_compressed_bytes.to_bytes(num_bytes_for_writing_num_window_bytes, 'big')
                output_file.write(num_compressed_bytes_as_bytes)
                out_stats.update(num_compressed_bytes_as_bytes)
                output_file.write(compressed_bytes)
                out_stats.update(compressed_bytes)
                in_buffer_bytes = input_file.read(bytes_per_window)
                in_stats.update(in_buffer_bytes)
            original_md5_bytes = in_stats.compute_md5_bytes()
            output_file.write(original_md5_bytes)  # append the original 16-byte MD5 to the very end of the file.
            out_stats.update(original_md5_bytes)
            total_compressed_bytes += 16

        print(f'Input MD5: {in_stats.compute_md5_hex()}')
        print(f'Input Shannon entropy: {in_stats.compute_shannon_entropy():0.6f}')
        print(f'Output MD5: {out_stats.compute_md5_hex()}')
        print(f'Output Shannon entropy: {out_stats.compute_shannon_entropy():0.6f}')

        compression_toc = time.perf_counter()
        print(f"Compressing took {compression_toc - compression_tic:0.4f} seconds")

        print(f'total bytes (raw): {total_bytes_read}')
        print(f'total bytes (compressed): {total_compressed_bytes}')
        print(f'space saving: {100 * (1 - total_compressed_bytes / total_bytes_read):0.2f}%')

    # Try reading back

    if DECOMPRESS:
        num_bytes_read = 0
        decompression_tic = time.perf_counter()
        file_size = os.stat(output_path).st_size
        rehydrate_stats = StatsCalculator()
        decompressor = Decompressor(binomial_coefficient_cache=cache)
        with open(output_path, 'rb') as output_file, open(reassemble_path, 'wb') as reassemble_file:
            size_bytes = output_file.read(2)  # TODO remove hard-coded stuff
            while size_bytes:
                size = int.from_bytes(size_bytes, 'big')
                payload_bytes = output_file.read(size)
                num_bytes_read += 2 + len(payload_bytes)  # TODO remove hard-coded stuff
                decompressed_bytes = decompressor.decompress(payload_bytes, num_bits_for_bytes_per_window)
                rehydrate_stats.update(decompressed_bytes)
                reassemble_file.write(decompressed_bytes)
                if num_bytes_read == file_size - 16:
                    published_digest_bytes = output_file.read(16)
                    num_bytes_read += 16
                size_bytes = output_file.read(2)  # TODO remove hard-coded stuff
            computed_digest_bytes = rehydrate_stats.compute_md5_bytes()

        assert computed_digest_bytes == published_digest_bytes
        decompression_toc = time.perf_counter()
        print(f'Decompressing took {decompression_toc - decompression_tic:0.4f} seconds')
        print(f'Reconstituted MD5: {rehydrate_stats.compute_md5_hex()}')

        print(f"Num compressed bytes read back in: {num_bytes_read}")
