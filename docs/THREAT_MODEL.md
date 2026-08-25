# Threat Model

## Attacker

**Goal:** Recover the plaintext message or the private key from the public artifacts.

**Capabilities:**
- Full access to `secret.ct` (ciphertext, 1,963,107 bytes compressed)
- Full access to `pk.bin` (public key, 3,042,901 bytes compressed)
- Full access to 44 LPN samples (`pvac.prf.r.1.*`)
- Unlimited offline computation
- Knowledge of the full source code (`pvac_hfhe_cpp @ 071b0e9`)
- Knowledge of all parameter values

**Not modelled:**
- Chosen-ciphertext oracle
- Timing/side-channel access
- Access to private components not released with the challenge

## Attack surfaces (scoped)

1. **Ciphertext structure** — scalar weights, signs, indices, cross-layer relations
2. **PRF/LPN generation** — prf_k-rooted derivation of R seeds; LPN samples
3. **Public key** — H matrix rank and weight distribution; powg_B discrete log
4. **Pedersen commitments** — PC point distribution; R_com oracle (absent from wire)
5. **Wrapped mask** — T0 = R0(v+m), T1 = -R1·m; ratio/character/parity attacks
6. **LPN core** — Direct ISD/BKW attack on (n=4096, m=16384, tau=1/8)

## Out of scope

- Attacks requiring chosen-ciphertext queries
- Side-channel / timing attacks
- Quantum algorithms (Grover, Regev variants) — noted but not implemented
- Fault injection
