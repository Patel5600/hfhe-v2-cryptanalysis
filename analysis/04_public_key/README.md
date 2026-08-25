# Phase 4 — Public-Key Structure

## Question

Does `pk.bin` contain an exploitable structural weakness that bypasses the intended cryptographic core?

## Wire format

The public key contains:

- `Params`
- `canon_tag`
- `H[0..n_bits-1]`
- `ubk.perm`
- `ubk.inv`
- `H_digest`
- `omega_B`
- `powg_B[0..B-1]`

The pinned serializer validates the H column count, each H bit-vector length, permutation sizes, and `powg_B` count.

## H matrix

Dimensions:

`m_bits = 8192`, `n_bits = 16384`.

Column weight generation uses a deterministic SHA-256-based sampler and a mixed weight of `192` or `193`.

Observed:

- 8190 columns of weight 192
- 8194 columns of weight 193
- full GF(2) rank = 8192
- no duplicate columns in the tested corpus

No useful low-rank or obvious sparse-code shortcut was observed.

## `powg_B`

`B = 337`.

The generated values satisfy:

`powg_B[0] = 1`

`powg_B[i+1] = powg_B[i] * g`

for all 336 transitions, with `g^337 = 1` and `g != 1`.

Because `idx` is already public on every ciphertext edge, recovering the exponent of a public subgroup element does not reveal hidden edge information.

## Cyclotomic relation

The order-337 subgroup satisfies:

`1 + g + ... + g^336 = 0`.

The relation does not by itself reveal a secret coefficient because the published edges already disclose `idx` and `w` and the live layers do not expose an unknown coefficient vector matching the full 337-term relation.

## Verdict

**CLOSED.** No public-key structural shortcut was found.
