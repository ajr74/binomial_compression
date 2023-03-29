# Binomial compression
We propose a method for lossless compression based on a two-fold strategy: (i) decomposition of a window of arbitray bytes to a series of reduced bitsets; (ii) compression of bitsets using colexicographic ranking.

The algorithm is presently incapable of outperforming standard compression utilities like _gzip_ and _xz_. However, it works. We see it therefore, as _only_ a proof of concept - a starting point for bigger things.

## Window decomposition
Consider, in a universe of size 3, a window of five elements, say $[y, y, x, z, z]$. We can project this window on to three bitsets (in ascending order): $[00100]\_{x}$, $[11000]\_{y}$, and $[00011]\_{z}$. Rather than use these bitsets of equal length as input to a bitset compressor, we can fist perform a reduction. A simple scheme involves removing bitset positions from previous bitsets: $[00100]\_{\bar{x}}$, $[1100]\_{\bar{y}}$, and $[11]\_{\bar{z}}$. Such a scheme is reversible.

In practice, we deal with byte windows which have a universe size of 256, but the methodology is similar to the synthetic example above. If each byte present in a byte window can be representled by a sparse (and diminishing) bitset, then these bitsets can be compressed and stored as a concatentation, potentially with fewer bytes than the original byte window.

## Bitset ranking
One way to compress a bitset is to consider its length, $N$ say, and its population count, $k$ say. With $N$ and $k$ we can compute a _rank_ for this bitset from the positions of the bitset's populated bits. If this computed rank (and any info required to support it, _e.g._, $k$) can be stored with fewer bits than the original bitset, then we have compression.

Bitset $b$ is one of many possible bitsets associated with the tuple $(N,k)$, or $b\in{B_{N,k}}=\{b_0, b_1, ...\}$. The number of elements in $B_{N,k}$ is given by the usual binomial coefficient:

$$|B_{N,k}|=\binom{N}{k}=\frac{N!}{k!(N-k)!}.$$

We seek a function to uniquely index each $b$ in $B_{N,k}$. Using co-lexicographic ordering, there is a ranking function to obtain the index value:

$$r(b)=\sum^{k}_{i=1}\binom{p(b,i)}{i}$$

where $p(b,i)\in{[0,N-1]}$ gives the $i^{th}$ index of $1$ within $b$.

We can recover $b$ from $r(b)$ by successively applying an unranking function:

$$p(b,i)=\max_j\binom{j}{i}, \text{s.t.}\binom{j}{i}\leqslant r(b)-\sum^{k}_{\ell=i+1}p(b,\ell)$$

where $i=k,...,1$.

## Compressed file spec
The file format is fairly rudimentary. The beginning of the file contains magic bytes and the number of uncompressed bytes for each window. Then a succession of compressed windows. The end of the file contains the MD5 digest of the original.

## Usage
    usage: main.py [-h] [-d] [-k] [-s SIZE] [-v] file
    
    Compress/decompress a file
    
    positional arguments:
      file                  the file to process
    
    optional arguments:
      -h, --help            show this help message and exit
      -d, --decompress      run in decompression mode
      -k, --keep            retain files
      -s SIZE, --size SIZE  number of bytes per processing window (default 1024, max 4096)
      -v, --verbose         run verbosely

## Future directions
- Variable/optimal length byte windows
- Port from Python to C++
- Parallelisation

## References

1. [Ranking and Unranking of Combinations and Permutations](https://computationalcombinatorics.wordpress.com/2012/09/10/ranking-and-unranking-of-combinations-and-permutations/), Derrick Stolee (2012).
2. [Binary Image Compression Based on Binomial Numbers](https://scholar.google.com/scholar_lookup?title=Binary+Image+Compression+Based+on+Binomial+Numbers&author=Borysenko,+O.&author=Kulyk,+I.&author=Kostel,+S.&author=Skordina,+O.&publication_year=2010&journal=Bull.+PG+Univ.+Ploiesti+Ser.+Math.+Inform.+Phys.+Ploiesti&volume=62&pages=1–12,), O. Borysenko, I. Kulyk, S. Kostel, O. Skordina (2010).
