# Entry 002 \u2014 v2 R_com Removal Confirmed

**Date:** Phase 0
**Status:** CLOSED by source read

## Process

Read `source/pvac_artifact_serialize.hpp` lines 1-503 systematically.
`write_layer` writes: idx, sign, w (u128 plaintext), ztag, nonce, pc_bytes.
R_com is NOT present.

## Consequence

The v1 oracle attack is definitively closed. The wire format contains
no direct randomness seed. Pedersen commitment hiding must be broken
through DLOG, not through R_com recovery.
