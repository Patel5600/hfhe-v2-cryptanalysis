#include <pvac/pvac.hpp>
#include <pvac/utils/text.hpp>
#include "../source/pvac_artifact_serialize.hpp"

#include <iostream>
#include <vector>
#include <fstream>
#include <map>

using namespace pvac;

std::vector<uint8_t> load_file(const std::string& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("cannot open " + path);
    in.seekg(0, std::ios::end);
    size_t sz = in.tellg();
    in.seekg(0, std::ios::beg);
    std::vector<uint8_t> d(sz);
    in.read((char*)d.data(), sz);
    return d;
}

std::vector<Cipher> load_bundle(const std::string& path) {
    auto data = load_file(path);
    size_t pos = 16; // magic
    uint64_t count = 0;
    for (int i = 0; i < 8; ++i) count |= (uint64_t)data[pos++] << (8 * i);
    std::vector<Cipher> cts;
    for (uint64_t i = 0; i < count; ++i) {
        uint64_t len = 0;
        for (int j = 0; j < 8; ++j) len |= (uint64_t)data[pos++] << (8 * j);
        cts.push_back(pvac_ser::deserialize_cipher(data.data() + pos, len));
        pos += len;
    }
    return cts;
}

Fp calc_public_T(const PubKey& pk, const Cipher& c, uint32_t layer_id) {
    Fp acc = layer_id == 0 && !c.c0.empty() ? c.c0[0] : fp_from_u64(0);
    for (const auto& e : c.E) {
        if (e.layer_id != layer_id) continue;
        Fp term = fp_mul(e.w[0], pk.powg_B[e.idx]);
        acc = sgn_val(e.ch) > 0 ? fp_add(acc, term) : fp_sub(acc, term);
    }
    return acc;
}

int main() {
    std::cout << "=== Comprehensive Historical Attack Suite on secret.ct ===\n\n";

    auto pk_bytes = load_file("C:/Dev/octra/pk.bin");
    auto pk = pvac_ser::deserialize_pubkey(pk_bytes.data(), pk_bytes.size());
    std::cout << "Loaded pk.bin: B = " << pk.prm.B << ", powg_B count = " << pk.powg_B.size() << "\n";

    auto ciphers = load_bundle("C:/Dev/octra/secret.ct");
    std::cout << "Loaded secret.ct: " << ciphers.size() << " ciphers.\n\n";

    // ── ATTACK 1: Historical R^2 Attack Sweep ──
    std::cout << "--- [1] Testing Historical R^2 Attack on all edge pairs ---\n";
    int total_pairs_tested = 0;
    int r2_candidates = 0;

    for (size_t ci = 0; ci < ciphers.size(); ++ci) {
        const auto& ct = ciphers[ci];
        for (uint32_t lid = 0; lid < ct.L.size(); ++lid) {
            if (ct.L[lid].rule != RRule::BASE) continue;

            Fp T_l = calc_public_T(pk, ct, lid);
            std::vector<size_t> pos_edges, neg_edges;
            for (size_t e_i = 0; e_i < ct.E.size(); ++e_i) {
                if (ct.E[e_i].layer_id != lid) continue;
                if (ct.E[e_i].ch == SGN_P) pos_edges.push_back(e_i);
                else neg_edges.push_back(e_i);
            }

            for (size_t pi : pos_edges) {
                Fp t_p = fp_mul(ct.E[pi].w[0], pk.powg_B[ct.E[pi].idx]);
                for (size_t ni : neg_edges) {
                    Fp t_n = fp_mul(ct.E[ni].w[0], pk.powg_B[ct.E[ni].idx]);
                    Fp cand = fp_sub(t_p, t_n);
                    ++total_pairs_tested;

                    // Compute sqrt(cand) mod p where p = 2^127 - 1
                    Fp cand_qr = fp_pow_u128(cand, ((u128)1 << 125));
                    Fp sq = fp_mul(cand_qr, cand_qr);
                    if (sq.lo == cand.lo && sq.hi == cand.hi) {
                        if (cand_qr.lo != 0 || cand_qr.hi != 0) {
                            Fp v_cand = fp_mul(T_l, fp_inv(cand_qr));
                            if (v_cand.hi < (1ull << 56)) {
                                uint8_t buf[15];
                                unpack_fp_to_15_bytes(v_cand, buf);
                                int printable = 0;
                                for (int b = 0; b < 15; ++b) {
                                    if (buf[b] >= 32 && buf[b] < 127) ++printable;
                                }
                                if (printable >= 13) {
                                    ++r2_candidates;
                                    std::cout << "  [!] R^2 MATCH in CT" << ci << " Layer" << lid
                                              << ": \"" << std::string((char*)buf, 15) << "\"\n";
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    std::cout << "  Total edge pairs tested: " << total_pairs_tested << "\n";
    std::cout << "  R^2 printable candidates found: " << r2_candidates << "\n\n";

    // ── ATTACK 2: Two-Ciphertext Division / Cross-Ratio Lineage ──
    std::cout << "--- [2] Testing Two-Ciphertext Cross-Layer Combinations ---\n";
    int cross_cipher_matches = 0;
    for (size_t i = 0; i < ciphers.size(); ++i) {
        for (size_t j = i + 1; j < ciphers.size(); ++j) {
            Fp Ti0 = calc_public_T(pk, ciphers[i], 0);
            Fp Tj0 = calc_public_T(pk, ciphers[j], 0);
            Fp ratio = fp_mul(Ti0, fp_inv(Tj0));
            if (ratio.lo < 1000 && ratio.hi == 0) {
                std::cout << "  Small integer ratio between CT" << i << " and CT" << j << ": " << ratio.lo << "\n";
                ++cross_cipher_matches;
            }
        }
    }
    std::cout << "  Cross-ciphertext small ratio matches: " << cross_cipher_matches << "\n\n";

    std::cout << "============================================================\n";
    std::cout << "  HISTORICAL REGRESSION ATTACK SUITE: VERDICT\n";
    std::cout << "============================================================\n";
    std::cout << "  R^2 Attack in 071b0e9 secret.ct:     " << (r2_candidates > 0 ? "EXPLOIT FOUND" : "CLOSED (Patched in 071b0e9)") << "\n";
    std::cout << "  Two-Cipher Division Ratio:          " << (cross_cipher_matches > 0 ? "SIGNAL FOUND" : "CLOSED (No Small Ratio)") << "\n";
    std::cout << "============================================================\n";

    return 0;
}
