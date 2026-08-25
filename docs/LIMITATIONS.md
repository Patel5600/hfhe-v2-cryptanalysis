# Limitations

## What this investigation does NOT establish

This work does **not** establish:

1. **Computational security** of the complete HFHE v2 construction.
   A negative experimental result does not imply formal security.

2. **Impossibility** of an undiscovered cryptanalytic attack.
   The tested attack surface is large but finite; novel mathematical
   techniques may succeed where our experiments failed.

3. **Security against future LPN algorithms.**
   LPN cryptanalysis is an active research area. Parameter margins
   that appear adequate today may erode with algorithmic advances.

4. **Security against implementation bugs** not exercised by the
   experiments. The investigation analysed the serialized wire format
   and public source; it did not audit the full implementation for
   memory-safety, side-channel, or fault-injection vulnerabilities.

5. **Security of unavailable/private components.**
   The investigation is limited to the public artifacts and pinned source.
   Private server-side components, key derivation infrastructure, or
   deployment-specific code are out of scope.

6. **Equivalence between experimental estimates and formal reductions.**
   Statistical tests provide empirical evidence, not mathematical proofs.
   Failure to detect a distinguisher does not bound the distinguishing
   advantage below any specific epsilon.

## Scope limitations

- All 44 LPN samples are domain `pvac.prf.r.1` (R1 derivation seed only).
  The noise/R2/R3 domains were not available for analysis.

- The investigation does not cover chosen-ciphertext or adaptive attacks.

- Quantum algorithms (Grover speedup on LPN, Regev's quantum-classical
  hybrid) are noted but not implemented or estimated.

## Terminology

**CLOSED** = the tested hypothesis produced no reproducible exploitable signal.
This does NOT mean the hypothesis is mathematically impossible or that
the construction is secure against that class of attack.
