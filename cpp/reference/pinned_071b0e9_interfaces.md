# Pinned Interface Reference — pvac_hfhe_cpp @ 071b0e9

This file documents the key interfaces from the pinned source commit
used throughout this investigation.

## Source repository

    https://github.com/octra-labs/pvac_hfhe_cpp
    Commit: 071b0e909c119de815e284b347c4bd979cb59ef3
    Date:   2026-07-09
    Message: public matrix sampling

## Key types (include/pvac/core/types.hpp)

```cpp
struct Fp    { __uint128_t val; };           // Field element in Z/(2^127-1)
struct Scalar { uint8_t bytes[32]; };        // Ristretto255 scalar
struct Edge {
    uint64_t idx;   // Column index into H
    uint8_t  sign;  // +1 or -1 (stored as 0x01 / 0xFF)
    Fp       w;     // Edge weight (Fp element)
    uint8_t  ztag; // Zero tag
    uint64_t nonce;// Per-edge nonce
    Scalar   pc;   // Pedersen commitment (32 bytes)
};
struct Layer { std::vector<Edge> edges; };
struct Cipher { std::vector<Layer> layers; };
```

## PRF construction (include/pvac/crypto/lpn.hpp)

```cpp
std::array<uint8_t,32> derive_aes_key(
    const SecKey& prf_k,
    const std::string& canon_tag,
    const std::array<uint8_t,32>& H_digest,
    uint8_t ztag,
    uint64_t nonce_lo, uint64_t nonce_hi,
    const std::string& domain);

Fp prf_R_core(const SecKey& prf_k, uint64_t layer, uint64_t idx,
              const std::string& domain);
```

## Serializer (source/pvac_artifact_serialize.hpp)

Critical: `write_layer` does NOT write R_com.

```cpp
void write_layer(Writer& out, const Layer& layer) {
    write_u64(out, layer.edges.size());
    for (auto& e : layer.edges) {
        write_u64(out, e.idx);
        write_u8(out, e.sign);
        write_u128(out, e.w.val);   // w in plaintext
        write_u8(out, e.ztag);
        write_u64(out, e.nonce);
        write_u32(out, 32);          // PC length
        write_bytes(out, e.pc.bytes, 32);
        // R_com is NOT written here
    }
}
```

## Encryption (include/pvac/ops/encrypt.hpp)

```cpp
// Wrapped construction:
// T_0 = R_0 * (v + m)
// T_1 = -R_1 * m

// Fisher-Yates permutation after merge:
namespace reduction {
    void merge(std::vector<Edge>& edges);
    void permute(std::vector<Edge>& edges);
}
```

## Commitment (include/pvac/crypto/ristretto255.hpp)

```cpp
Scalar sc_from_fp(const Fp& x);  // NO sc_reduce256; p < ell ensures safety
RistrettoPoint pedersen_commit(const Fp& w, const Scalar& rho);
```
