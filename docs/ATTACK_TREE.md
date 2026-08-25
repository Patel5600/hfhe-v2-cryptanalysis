# Attack Tree

```
HFHE v2
│
├── 0. Artifact integrity
│   ├── secret.ct parsing ............... CLOSED (full parse, 22 CT objects confirmed)
│   └── pk.bin parsing .................. CLOSED (H digest byte-for-byte match)
│
├── 1. Ciphertext structure
│   ├── Scalar weight reuse ............. CLOSED (distribution indistinguishable from null)
│   ├── Sign/index correlation .......... CLOSED (no cross-edge bias detected)
│   ├── Cross-layer prf_k distinguisher . CLOSED (KS p=0.523, N=5000)
│   ├── Tuple ordering signal ........... CLOSED (CSPRNG Fisher-Yates permutation; source)
│   ├── Sigma bitvectors ................ CLOSED (csprng_u64, not prf_k-rooted)
│   └── Edge-group reconstruction ....... CLOSED (permutation destroys correspondence)
│
├── 2. PRF/LPN generation
│   ├── Marginal population-A anomaly ... CLOSED (KS p=0.196, N=44)
│   ├── Population-B matched null ....... CLOSED (no deviation from null)
│   ├── Joint key distinguisher ......... CLOSED (preregistered predicates, N=20000)
│   └── Low-weight secret relation ...... CLOSED (no sub-threshold cluster)
│
├── 3. Joint key / metadata
│   ├── T metadata vs nonce correlation . CLOSED (Pearson r=-0.022, p=0.232)
│   ├── Nonce-difference correlation .... CLOSED (no structure)
│   └── Permutation control test ........ CLOSED (permuted null matches real)
│
├── 4. Public key
│   ├── H matrix GF(2) rank ............. CLOSED (8192/8192, full rank)
│   ├── H column weight distribution .... CLOSED (bimodal 192/193, structural)
│   ├── powg_B discrete log ............. CLOSED (B=337 = ord(g), trivial subgroup)
│   └── Cyclotomic subgroup relations ... CLOSED (no secret coefficient constraint)
│
├── 5. Pedersen commitments
│   ├── R_com oracle .................... CLOSED (absent from wire format; source)
│   ├── PC point distribution ........... CLOSED (KS p=0.196, N=44)
│   └── Fp -> Z/ell cross-field inversion CLOSED (0/100000 trials cancel mod ell)
│
├── 6. Wrapped-mask ratio attacks
│   ├── R0/R1 low-dimensional leakage ... CLOSED (Hamming mean=0.500, p>>0.05)
│   ├── Character tests (-T0*T1) ........ CLOSED (Chi2=1.34, p=0.246, N=20000)
│   ├── Parity / sign agreement ......... CLOSED (rate=0.500 exactly, p=0.756)
│   └── Ratio estimators ................ CLOSED (toy world: recovery impossible)
│
└── 7. LPN core — OPEN (no practical attack identified)
    └── LPN(n=4096, m=16384, tau=1/8)
        ├── ISD (BJMM, MMT): super-exponential work factor
        ├── BKW: requires more samples than available
        └── No algorithmic shortcut found
```

## Legend

- **CLOSED** — tested hypothesis produced no reproducible exploitable signal.
  This does NOT mean the hypothesis is mathematically impossible.
- **OPEN** — surviving attack surface; no practical attack found but not
  experimentally falsified.

## Source mapping

| Branch | Script | Results |
|--------|--------|---------|
| Artifact verification | `analysis/00_artifact_verification/` | `results/artifact/` |
| Cross-layer prf_k | `analysis/02_prf_lpn/population_b.py` | `results/prf_lpn/` |
| PC distribution | `analysis/05_commitments/pc_distribution.py` | `results/commitments/` |
| Cross-field inversion | `analysis/05_commitments/cross_field_inversion.py` | `results/commitments/` |
| Character/parity/ratio | `analysis/06_wrapped_ratio/` | `results/wrapped_ratio/` |
| LPN complexity | `analysis/07_lpn_complexity/` | `results/` |
