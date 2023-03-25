# Compression
Compression based on binomials and byte-space reduction

# Background
Digital photos, word-processing documents, and database tables are stored with just 1s and 0s. All data is binary, and in the internet age, there's a _lot_ of it. But, despite the availability of low-cost / high-capacity storage, it makes compelling sense to be able to compress data prior persisting it to disk or transmitting it over a network. 

Here we propose a new compression algorithm based on some aspects of combinatorial number systems.

Consider a bitset $b$ containing $N$ bits and having a population count of $k$. Bitset $b$ is one of many possible bitsets associated with the tuple $(N,k)$, or $b\in{B_{N,k}}=\{b_0, b_1, ...\}$. The cardinality of $B_{N,k}$ is given by the usual binomial coefficient

$$|B_{N,k}|=\binom{N}{k}=\frac{N!}{k!(N-k)!}$$.

We seek a function to uniquely index each window $b$ in $B_{N,k}$. Using co-lexicographic ordering, there is a ranking function to obtain the index value:

$$r(b)=\sum^{k}_{i=1}\binom{p(b,i)}{i}$$

where $p(b,i)\in{[0,N-1]}$ gives the $i^{th}$ index of $1$ within $b$.
We can recover $b$ from $r(b)$ by successively applying an unranking function

$$p(b,i)=\max_j\binom{j}{i}, \text{s.t.}\binom{j}{i}\leqslant r(b)-\sum^{k}_{\ell=i+1}p(b,\ell)$$

where $i=k,...,1$.
