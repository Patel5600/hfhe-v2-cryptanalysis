# 00 Project Overview — HFHE v2 Cryptanalytic Investigation

This repository records the exhaustive cryptanalytic investigation of the **Octra Labs HFHE v2 Challenge** (`octra-labs/hfhe-challenge`), pinned against `octra-labs/pvac_hfhe_cpp` commit `071b0e909c119de815e284b347c4bd979cb59ef3`.

## The Challenge
The challenge provides:
1. `secret.ct` (1,963,107 bytes): 22 ciphertext objects under unknown key $prf_k$.
2. `pk.bin` (3,042,901 bytes): Public key defining the parity-check matrix $H \in \mathbb{F}_2^{8192 \times 16384}$, cyclic group parameter $B=337$, and LPN parameters $(n=4096, m=16384, \tau=1/8)$.
3. 44 LPN sample instances (`pvac.prf.r.1.*`): 16,384 samples each over dimension 4096 with noise rate $\tau = 1/8$.

## Core Finding
> **Negative Cryptanalytic Result:** No practical exploit, plaintext recovery, or private key recovery was identified across the tested attack surface. The construction's residual security rests on the hard core problem: **$\text{LPN}(n=4096, m=16384, \tau=1/8)$**.

This is not a mathematical proof of security, but an empirical and structural falsification of 26 attack hypotheses.\n