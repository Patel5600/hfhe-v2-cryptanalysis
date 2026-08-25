# HFHE v2 — Cryptanalytic Investigation

> **Summary:** No practical exploit or private-key recovery was identified across the tested
> attack surface. This is a **negative cryptanalytic result**, not a proof of security.

This repository documents a systematic cryptanalytic investigation of the
[HFHE v2 challenge](https://github.com/octra-labs/hfhe-challenge) published by Octra Labs.
The investigation targets the public artifacts (`secret.ct`, `pk.bin`, and 44 LPN samples)
produced by the `pvac_hfhe_cpp` implementation.

---

## Quick-start

```bash
git clone https://github.com/Patel5600/hfhe-v2-cryptanalysis.git
cd hfhe-v2-cryptanalysis
pip install -r requirements.txt

# Reproduce all experiments (requires artifacts in $ARTIFACTS_DIR)
python experiments/reproduce/run_all.py --artifacts /path/to/challenge/artifacts
```

Each experiment writes machine-readable JSON to `results/` and prints a human-readable
summary. All random seeds are fixed; results should be bit-identical across runs.

---

## System parameters

| Parameter          | Value        |
|--------------------|-------------|
| LPN dimension (n)  | 4 096        |
| LPN samples (m)    | 16 384 / instance |
| LPN instances      | 44           |
| Total LPN samples  | 720 896      |
| Noise rate (tau)   | 1/8          |
| Ciphertext objects | 22           |
| BASE layers        | 44           |
| Edge weight (avg)  | 1 829        |
| Fp field prime     | 2^127 - 1    |
| Group base order   | 337          |

---

## Repository layout

```
hfhe-v2-cryptanalysis/
├── docs/              — Design documents, methodology, attack tree, conclusions
├── analysis/          — Experiment scripts (one directory per attack phase)
├── src/               — Reusable library (artifact parsing, crypto, statistics)
├── experiments/       — Configs, manifests, and end-to-end reproduction drivers
├── results/           — Machine-readable JSON outputs from every experiment
├── figures/           — Publication-quality plots
├── tables/            — CSV summary tables
└── provenance/        — Artifact hashes, source commit pins, environment log
```

See `docs/ATTACK_TREE.md` for the full map of tested hypotheses.

---

## Artifact provenance

| Artifact   | SHA-256                                                            | Size (bytes) |
|------------|--------------------------------------------------------------------|-------------|
| `secret.ct`| `5da7f82724838bf7a8c4fe95fbf6d573b621c04c9b2f7ae849545cf60223fbab` | 1 963 107   |
| `pk.bin`   | `1e788edff9dea19a782defae053f3757ccf5edd41cd3e24ae44e1496045e9410` | 3 042 901   |

Source implementation pinned at commit
`071b0e909c119de815e284b347c4bd979cb59ef3`
of `octra-labs/pvac_hfhe_cpp` (2026-07-09).

---

## High-level findings

| Phase | Area                        | Status   |
|-------|-----------------------------|----------|
| 0     | Artifact verification       | CLOSED   |
| 1     | Ciphertext structure        | CLOSED   |
| 2     | PRF/LPN generation          | CLOSED   |
| 3     | Joint key distinguisher     | CLOSED   |
| 4     | Public key (H matrix)       | CLOSED   |
| 5     | Pedersen commitments        | CLOSED   |
| 6     | Wrapped-mask ratio attacks  | CLOSED   |
| 7     | LPN complexity bounds       | assessed |

The surviving cryptographic object is the core LPN problem instance
(n=4096, m=16384, tau=1/8), for which no sub-exponential practical
attack is currently known.

> **CLOSED** means: the tested hypothesis produced no reproducible exploitable signal.
> It does **not** mean the hypothesis is mathematically impossible.

---

## License

MIT — see `LICENSE`.
