# Entry 003 — 22 Ciphertext Objects

**Date:** Phase 0  
**Status:** Structural finding

## Finding

Parsing secret.ct revealed 22 ciphertext objects (not 44 as initially assumed).
Each object contains 1829 edges.

## Implication

With 22 ciphertext objects x 1829 edges each = 40,238 edges total.
The 44 LPN files are SEPARATE from these -- they are domain pvac.prf.r.1 samples,
not the 22 ciphertext objects.

## What this meant for our attack surface

- Population A: pairs from the same ciphertext object (1829 x 1829/2 ~= 1.6M pairs possible)
- Population B: pairs across different ciphertext objects (22 objects = 22 x 21 / 2 = 231 cross-pairs per edge)
- Our experiments sampled 5,000 pairs from each population
