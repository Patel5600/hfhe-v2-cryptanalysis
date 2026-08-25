# Entry 001 — The v1 R_com Oracle Attack

**Date:** Phase 0  
**Status:** CLOSED by source (v1 vulnerability confirmed; v2 fix confirmed)

## Discovery

Reading `source/pvac_artifact_serialize.hpp`, function `write_layer`:
v1 serialized R_com (the randomness seed for Pedersen commitments) into
the ciphertext wire format.

## Why this was fatal in v1

R_com -> rho (Pedersen blinding scalar) -> PC - rho*H = w*G -> w.
With w known and R_com known, the full mask matrix R could be reconstructed,
collapsing IND-CPA security.

## v2 fix

The v2 `write_layer` does NOT write R_com. Verified by reading lines 1-503
of `pvac_artifact_serialize.hpp` and finding no R_com write.

## Lesson

This is a clean example of a design-level fix. The mathematical construction
was sound; the implementation serialization was the vulnerability.
v2 correctly removes the oracle.
