import argparse
import os
import sys
import time

from alive_progress import alive_bar

import util
from binomial import Binomial
from stats_calculator import StatsCalculator
from window_compressor import WindowCompressor
from window_decompressor import WindowDecompressor

MAGIC_BYTES = b'ajr74z'
COMPRESSED_EXT = '.ajz'
DEFAULT_WINDOW_SIZE = 1024
MAX_WINDOW_SIZE = 4096
MD5_DIGEST_SIZE = 16

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Compress/decompress a file')
    parser.add_argument('file', help='the file to process')
    parser.add_argument('-d', '--decompress', action='store_true', help='run in decompression mode')
    parser.add_argument('-k', '--keep', action='store_true', help='retain files')
    parser.add_argument('-s', '--size', help=f'number of bytes per processing window (max {MAX_WINDOW_SIZE})',
                        default=DEFAULT_WINDOW_SIZE)
    parser.add_argument('-v', '--verbose', action='store_true', help='run verbosely')
    args = parser.parse_args()

    if not os.path.exists(args.file) or not os.path.isfile(args.file):
        raise FileNotFoundError(f'{args.file} does not exist or is not a regular file')

    if args.decompress:
        d_input_path = args.file
        d_output_path = d_input_path.removesuffix(COMPRESSED_EXT)
        file_size = os.stat(d_input_path).st_size
        with alive_bar(file_size, title='Decompressed', enrich_print=False, max_cols=220, force_tty=True,
                       bar='circles', unit='b', disable=not args.verbose) as bar,\
                open(d_input_path, 'rb') as d_input_file:
            d_in_stats = StatsCalculator()
            magic = util.read_bytes(d_input_file, d_in_stats, len(MAGIC_BYTES))
            bar(len(magic))
            if magic == MAGIC_BYTES:
                bytes_per_window = util.read_val(d_input_file, d_in_stats)
                bar(util.NUM_BYTES_FOR_PERSISTED_PARAMETERS)
                cache_tic = time.perf_counter()
                cache = Binomial(bytes_per_window + 1)
                cache_toc = time.perf_counter()
                if args.verbose:
                    print(f'Precomputed binomial coefficients in {cache_toc - cache_tic:0.3f}s')
                decompressor = WindowDecompressor(cache, bytes_per_window)
                d_out_stats = StatsCalculator()
                with open(d_output_path, 'wb') as d_output_file:
                    size = util.read_val(d_input_file, d_in_stats)
                    while size:
                        bar(util.NUM_BYTES_FOR_PERSISTED_PARAMETERS)
                        payload_bytes = util.read_bytes(d_input_file, d_in_stats, size)
                        bar(len(payload_bytes))
                        decompressed_bytes = decompressor.process(payload_bytes)
                        util.write_bytes(d_output_file, d_out_stats, decompressed_bytes)
                        if d_in_stats.num_bytes == file_size - MD5_DIGEST_SIZE:
                            published_digest_bytes = util.read_bytes(d_input_file, d_in_stats, MD5_DIGEST_SIZE)
                            bar(len(published_digest_bytes))
                        size = util.read_val(d_input_file, d_in_stats)
                    computed_digest_bytes = d_out_stats.compute_md5_bytes()
                assert computed_digest_bytes == published_digest_bytes

            else:
                print(f'Incorrect compression format!')
                sys.exit(1)

        if args.verbose:
            print(f'Input:: MD5: {d_in_stats.compute_md5_hex()}; Shannon entropy: {d_in_stats.compute_shannon_entropy():0.6f}')
            print(f'Output:: MD5: {d_out_stats.compute_md5_hex()}; Shannon entropy: {d_out_stats.compute_shannon_entropy():0.6f}')
        if not args.keep:
            os.remove(d_input_path)

    else:
        bytes_per_window = args.size if 0 < args.size < DEFAULT_WINDOW_SIZE else DEFAULT_WINDOW_SIZE
        num_bits_for_bytes_per_window = util.num_bits_required_to_represent(bytes_per_window)
        cache_tic = time.perf_counter()
        cache = Binomial(bytes_per_window + 1)
        cache_toc = time.perf_counter()
        if args.verbose:
            print(f"Precomputed binomial coefficients in {cache_toc - cache_tic:0.3f}s")

        c_input_path = args.file
        file_size = os.stat(c_input_path).st_size
        c_output_path = c_input_path + COMPRESSED_EXT
        c_in_stats = StatsCalculator()
        c_out_stats = StatsCalculator()
        compressor = WindowCompressor(cache, bytes_per_window)

        with alive_bar(file_size, title='Compressed', enrich_print=False, max_cols=220, bar='circles',
                       force_tty=True, unit='b', disable=not args.verbose) as bar,\
                open(c_input_path, 'rb') as c_input_file, open(c_output_path, 'wb') as c_output_file:
            util.write_bytes(c_output_file, c_out_stats, MAGIC_BYTES)
            util.write_val(c_output_file, c_out_stats, bytes_per_window)
            in_buffer_bytes = util.read_bytes(c_input_file, c_in_stats, bytes_per_window)
            while in_buffer_bytes:
                bar(len(in_buffer_bytes))
                compressed_bytes = compressor.process(in_buffer_bytes)
                util.write_val(c_output_file, c_out_stats, len(compressed_bytes))
                util.write_bytes(c_output_file, c_out_stats, compressed_bytes)
                in_buffer_bytes = util.read_bytes(c_input_file, c_in_stats, bytes_per_window)
            util.write_bytes(c_output_file, c_out_stats, c_in_stats.compute_md5_bytes())

        if args.verbose:
            print(f'Input:: MD5: {c_in_stats.compute_md5_hex()}; Shannon entropy: {c_in_stats.compute_shannon_entropy():0.6f}')
            print(f'Output:: MD5: {c_out_stats.compute_md5_hex()}; Shannon entropy: {c_out_stats.compute_shannon_entropy():0.6f}')
            print(f'Space saving: {100 * (1 - c_out_stats.num_bytes / c_in_stats.num_bytes):0.2f}%')

        if not args.keep:
            os.remove(c_input_path)
