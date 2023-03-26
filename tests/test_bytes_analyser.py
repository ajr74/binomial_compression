import math
import random

from bytes_analyser import BytesAnalyser


def test_compute_md5_hex_empty():
    analyser = BytesAnalyser()
    analyser.update(b'')
    assert analyser.compute_md5_hex() == 'd41d8cd98f00b204e9800998ecf8427e'


def test_compute_md5_hex():
    analyser = BytesAnalyser()
    analyser.update(b'The quick brown fox jumps over the lazy dog')
    assert analyser.compute_md5_hex() == '9e107d9d372bb6826bd81d3542a419d6'


def test_compute_shannon_entropy_completely_uniform():
    analyser = BytesAnalyser()
    analyser.update(b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    assert math.isclose(analyser.compute_shannon_entropy(), 0.0)


def test_compute_shannon_entropy_completely_mixed():
    analyser = BytesAnalyser()
    vals = []
    for i in range(0, 256):
        vals.append(i)
    random.shuffle(vals)
    analyser.update(bytes(vals))
    assert math.isclose(analyser.compute_shannon_entropy(), 8.0)


def test_compute_shannon_entropy_low():
    analyser = BytesAnalyser()
    vals = []
    for i in range(0, 100):
        vals.append(5)
    for i in range(100, 200):
        vals.append(117)
    for i in range(200, 300):
        vals.append(201)
    random.shuffle(vals)
    analyser.update(bytes(vals))
    assert math.isclose(analyser.compute_shannon_entropy(), 1.584962500721156)
