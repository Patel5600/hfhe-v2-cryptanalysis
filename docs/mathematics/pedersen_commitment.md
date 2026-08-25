# Pedersen Commitment Construction

## Definition

For edge weight w ∈ Fp and blinding scalar ρ ∈ Z/ℓZ:

    PC = w*G + ρ*H   ∈ Ristretto255

where G, H are independent public generators of Ristretto255.

## Binding and hiding

- **Binding:** Computational binding under discrete log hardness.
  An adversary cannot find (w', ρ') ≠ (w, ρ) with PC(w,ρ) = PC(w',ρ').
- **Hiding:** PC is perfectly hiding — for any w, the distribution
  over ρ ∈_R Z/ℓZ makes PC uniformly distributed on the curve.

## R_com is NOT in the wire format

v1 of HFHE serialized R_com (the commitment randomness seed) inside the
ciphertext, enabling a direct oracle attack. v2 removes this:

Source `source/pvac_artifact_serialize.hpp`, function `write_layer`:
```cpp
// R_com is NOT written. Only edges (idx, sign, w, ztag, nonce, PC) are.
for (auto& edge : layer.edges) {
    write_u64(out, edge.idx);
    write_u8(out, edge.sign);
    // ... w, ztag, nonce, pc bytes
}
```

## Why PC does not leak w

Given PC = w*G + ρ*H, recovering w requires either:
1. Solving DLOG on Ristretto255 (infeasible)
2. Knowing ρ (hidden by CSPRNG blinding, not in wire format)

## PC distribution experiment

The 44 PC values (one per LPN sample) were tested for distribution anomalies:
- KS(REAL vs permuted-null): p = 0.196
- Interpretation: No distinguishable structure. CLOSED.
