# Executive Summary

## Investigation: HFHE v2 Cryptanalytic Challenge

**Date:** 2026-08-25
**Investigator:** Irshad Patel
**Target:** octra-labs/hfhe-challenge (public artifacts: secret.ct, pk.bin, 44 LPN samples)
**Source pin:** pvac_hfhe_cpp @ 071b0e9

---

## Finding

> No practical exploit or private-key/plaintext recovery was identified across the
> tested attack surface.

This is a **negative cryptanalytic result**. The investigation was exhaustive across
the tested dimensions but cannot rule out undiscovered attacks.

---

## What was tested

Eight attack phases, each decomposed into independently testable hypotheses:

| Phase | Area | Branches tested | Result |
|-------|------|-----------------|--------|
| 0 | Artifact verification | 2 | CLOSED |
| 1 | Ciphertext structure | 6 | CLOSED |
| 2 | PRF/LPN generation | 4 | CLOSED |
| 3 | Joint key distinguisher | 3 | CLOSED |
| 4 | Public key / H matrix | 4 | CLOSED |
| 5 | Pedersen commitments | 3 | CLOSED |
| 6 | Wrapped-mask ratio attacks | 4 | CLOSED |
| 7 | LPN complexity assessment | — | assessed |

**Total independently falsified branches: 26**

---

## Surviving cryptographic object

The residual security rests on the hardness of:

    LPN(n=4096, m=16384, tau=1/8)

No sub-exponential practical algorithm is currently known for this parameter regime.
The investigation did not find a shortcut; generic ISD and BKW families were assessed
in Phase 7 but produce no practical attack at these parameters.

---

## What this does NOT establish

- Computational security of the complete construction
- Impossibility of an undiscovered cryptanalytic attack
- Security against future LPN algorithms
- Security of components not exercised by the experiments
- Equivalence between experimental estimates and formal reductions

See `docs/LIMITATIONS.md` for the full list.
