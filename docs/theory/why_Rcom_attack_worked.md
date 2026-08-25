# Why the v1 R_com Attack Worked

In HFHE v1, $R_{com}$ (the commitment randomness seed) was explicitly serialized inside `write_layer`.
An attacker could:
1. Parse $R_{com}$ directly from the wire.
2. Recompute $\rho = PRF(R_{com})$.
3. Subtract $\rho \cdot H$ from $PC$ to isolate $w \cdot G$.
4. Reconstruct the full $R_0, R_1$ mask matrices.\n