# Why v2 Removed R_com

In HFHE v2, `write_layer` in `source/pvac_artifact_serialize.hpp` completely omits $R_{com}$.
The wire format contains only:
`idx (u64)`, `sign (u8)`, `w (u128)`, `ztag (u8)`, `nonce (u64)`, `pc (32 bytes)`.
Without $R_{com}$, recovering $\rho$ requires breaking the discrete logarithm on Ristretto255.\n