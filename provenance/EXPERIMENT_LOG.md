# Experiment Log

Chronological record of all experiments performed during this investigation.

---

## 2026-08-XX — Phase 0: Artifact verification

### secret.ct structure
- **Script:** `analysis/00_artifact_verification/secret_ct_structure.py`
- **Finding:** 22 ciphertext objects parsed successfully; H digest matches byte-for-byte
- **Status:** CLOSED

### pk.bin structure
- **Script:** `analysis/00_artifact_verification/pk_bin_structure.py`
- **Finding:** pk decompresses to 17,110,454 bytes; B=337, m_bits=8192, n_bits=16384
- **Status:** CLOSED

---

## Phase 1: Ciphertext structure

### Cross-layer prf_k distinguisher
- **Script:** `analysis/02_prf_lpn/population_b.py`
- **N:** 5,000 pairs
- **Result:** KS(REAL vs NULL_B): stat=0.0263, p=0.523
- **Status:** CLOSED

### Tuple ordering
- **Evidence:** Source read — `reduction::permute` applies CSPRNG Fisher-Yates shuffle
- **Status:** CLOSED (source)

### R_com oracle
- **Evidence:** Source read — `write_layer` does not serialize R_com
- **Status:** CLOSED (source)

---

## Phase 4: Public key

### H matrix GF(2) rank
- **Finding:** 8192 pivot rows / 8192 total → full rank
- **H weight distribution:** 8190 cols of wt 192, 8194 cols of wt 193
- **Status:** CLOSED

### powg_B DLP
- **Finding:** B=337 = ord(g), so g^B = g^337 = identity; idx is public
- **Status:** CLOSED

---

## Phase 5: Pedersen commitments

### PC distribution
- **Script:** `analysis/05_commitments/pc_distribution.py`
- **N:** 44 PC values
- **Result:** KS(REAL vs NULL_B): p=0.196
- **Status:** CLOSED

### Cross-field Fp/Z-ell inversion
- **Script:** `analysis/05_commitments/cross_field_inversion.py`
- **N:** 100,000 trials
- **Result:** 0/100,000 trials: R * R_inv_p ≡ 1 mod ell
- **Status:** CLOSED

---

## Phase 6: Wrapped-mask ratio attacks

### Character test — Legendre(-T0·T1)
- **Script:** `analysis/06_wrapped_ratio/character_tests.py`
- **N:** 20,000 samples (IDEAL/TOY/REAL comparison)
- **Result:** Chi²=1.3448, p=0.246
- **Status:** CLOSED

### Sign agreement
- **Result:** Rate=0.500 exactly, p=0.756 (N=20,000)
- **Status:** CLOSED

### Toy ratio experiment
- **Script:** `analysis/06_wrapped_ratio/toy_ratio_experiment.py`
- **Finding:** Known-key toy world: ratio recovery impossible after permutation
- **Status:** CLOSED

---

## Phase 7: LPN complexity

### ISD/BKW work factor assessment
- **Script:** `analysis/07_lpn_complexity/work_factor.py`
- **Finding:** No practical attack at n=4096, m=16384, tau=1/8 with available resources
- **Note:** Formal concrete security level NOT established by this investigation
