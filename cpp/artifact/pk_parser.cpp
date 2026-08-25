// pk_parser.cpp
// Decompresses and validates pk.bin from HFHE v2 challenge.
#include <zlib.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <stdexcept>

int main(int argc, char** argv) {
    const char* path = (argc > 1) ? argv[1] : "pk.bin";
    FILE* f = fopen(path, "rb");
    if (!f) { perror(path); return 1; }
    fseek(f, 0, SEEK_END);
    size_t sz = ftell(f);
    rewind(f);
    std::vector<uint8_t> compressed(sz);
    fread(compressed.data(), 1, sz, f);
    fclose(f);

    std::vector<uint8_t> raw(sz * 8);
    uLongf dest_len = raw.size();
    while (uncompress(raw.data(), &dest_len, compressed.data(), sz) == Z_BUF_ERROR) {
        raw.resize(raw.size() * 2);
        dest_len = raw.size();
    }
    raw.resize(dest_len);

    printf("pk.bin decompressed: %zu bytes\n", raw.size());
    uint32_t B, m_bits, n_bits, h_col_wt, x_col_wt, err_wt, lpn_n, lpn_t, tau_num, tau_den;
    memcpy(&B, raw.data(), 4);
    memcpy(&m_bits, raw.data() + 4, 4);
    memcpy(&n_bits, raw.data() + 8, 4);
    memcpy(&h_col_wt, raw.data() + 12, 4);
    memcpy(&lpn_n, raw.data() + 24, 4);
    memcpy(&lpn_t, raw.data() + 28, 4);
    memcpy(&tau_num, raw.data() + 32, 4);
    memcpy(&tau_den, raw.data() + 36, 4);

    printf("  B: %u, m_bits: %u, n_bits: %u, h_col_wt: %u, lpn_n: %u, lpn_t: %u, tau: %u/%u\n",
           B, m_bits, n_bits, h_col_wt, lpn_n, lpn_t, tau_num, tau_den);
    return 0;
}\n