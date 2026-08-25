# HFHE v2 — Cryptanalytic Investigation

> **Summary:** No practical exploit or private-key recovery was identified across the tested attack surface. This is a **negative cryptanalytic result**, not a proof of security.

This repository documents a systematic cryptanalytic investigation of the public HFHE v2 challenge artifacts: `secret.ct`, `pk.bin`, and the 44 published LPN sample files, against the pinned `pvac_hfhe_cpp` implementation.

---

## What was actually tested

The investigation is not just a summary of “looks random.” It contains explicit hypotheses and quantitative tests for:

- ciphertext serialization and object/layer structure;
- weight reuse and cross-layer intersections;
- sign/index structure and group-level relations;
- tuple ordering and hidden tuple grouping;
- the removed v1 `R_com` oracle;
- PRF/LPN marginal statistics and matched-null methodology;
- joint `prf_k` / `public_T` dependency;
- public H matrix rank and weight structure;
- `powg_B` subgroup/DLP structure;
- Pedersen commitment serialization and distribution;
- Fp versus Ristretto scalar-field inversion;
- wrapped-layer `R0/R1` ratio recovery;
- Legendre, parity, LSB and subgroup-character predicates;
- generic ISD/BKW complexity estimates.

See [`docs/DETAILED_EXPERIMENT_CATALOG.md`](docs/DETAILED_EXPERIMENT_CATALOG.md) for the complete experiment-by-experiment record.

---

## Core mathematics

The wrapped pair is:

```text
T0 = R0 (v + m) mod p
T1 = -R1 m mod p
```

with `p = 2^127 - 1`.

Let:

```text
lambda = R0 / R1 mod p
```

Then:

```text
T0 + lambda*T1 = R0*v mod p
```

so recovering `lambda` would remove the fresh wrapper mask `m`.

The investigation therefore explicitly targeted `lambda`, rather than merely checking whether individual ciphertext values looked random.

The LPN core is:

```text
y_i = <A_i, S> XOR e_i
```

with:

```text
n    = 4096
m    = 16384 samples / instance
tau  = 1/8
files = 44
M    = 720896 total equations
```

The complete derivations and caveats are in [`docs/MATHEMATICS.md`](docs/MATHEMATICS.md).

---

## System parameters

| Parameter | Value |
|---|---:|
| LPN dimension | 4,096 |
| LPN samples / instance | 16,384 |
| LPN instances | 44 |
| Total equations | 720,896 |
| Noise rate | 1/8 |
| Ciphertext objects | 22 |
| BASE layers | 44 |
| Total serialized edge weights | 1,829 |
| Fp prime | 2^127 - 1 |
| `powg_B` entries | 337 |

---

## Repository layout

```text
hfhe-v2-cryptanalysis/
├── docs/              # mathematics, threat model, methodology, attack tree, results
├── analysis/          # phase-by-phase experiment code and experiment READMEs
├── src/               # reusable parsers, field/group helpers, statistical utilities
├── experiments/       # configs, manifests, and reproduction drivers
├── results/           # machine-readable experiment outputs
├── figures/           # generated visualizations
├── tables/            # summary CSVs
└── provenance/        # artifact hashes, source pin, environment, experiment log
```

### Phase map

```text
Phase 0  Artifact verification              CLOSED
Phase 1  Ciphertext structure                CLOSED
Phase 2  PRF/LPN statistics                 CLOSED
Phase 3  Joint-key / public_T correlation   CLOSED
Phase 4  Public-key structure               CLOSED
Phase 5  Pedersen commitments               CLOSED
Phase 6  Wrapped-mask ratio attacks         CLOSED
Phase 7  Generic LPN complexity             ASSESSED
```

---

## Important terminology

**CLOSED** means the *specific tested hypothesis* produced no reproducible exploitable signal.

It does **not** mean:

- mathematically impossible;
- formally secure;
- immune to future cryptanalysis;
- that every implementation path has been exhausted.

Phase 7 is deliberately marked **ASSESSED**, not CLOSED, because complexity estimates do not constitute a formal lower bound against every possible LPN algorithm.

---

## Artifact provenance

| Artifact | SHA-256 | Size |
|---|---|---:|
| `secret.ct` | `5da7f82724838bf7a8c4fe95fbf6d573b621c04c9b2f7ae849545cf60223fbab` | 1,963,107 |
| `pk.bin` | `1e788edff9dea19a782defae053f3757ccf5edd41cd3e24ae44e1496045e9410` | 3,042,901 |

Pinned implementation:

`octra-labs/pvac_hfhe_cpp@071b0e909c119de815e284b347c4bd979cb59ef3`

---

## Final result

The evidence supports the following statement:

> **No practical exploit or private-key recovery route was identified among the tested hypotheses. The tested peripheral attack surface was clean, leaving the cryptographic core as the remaining unbroken path.**

This repository deliberately does **not** claim a formal security proof or a universal multi-thousand-bit security bound.

---

## Reproduction

The end-to-end reproducer expects the public challenge artifacts to be supplied separately:

```bash
pip install -r requirements.txt
python experiments/reproduce/run_all.py --artifacts /path/to/challenge/artifacts
```

The experiment manifests record the expected inputs, sample sizes, null models, and statistical procedures.

---

## License

MIT — see [`LICENSE`](LICENSE).
