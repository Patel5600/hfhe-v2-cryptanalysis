// secret_ct_parser.cpp
// Parse and dump structure of secret.ct from HFHE v2 challenge.
// Compile: g++ -O2 -o secret_ct_parser secret_ct_parser.cpp -lz
// Usage:   ./secret_ct_parser secret.ct

#include <zlib.h>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <vector>
#include <string>
#include <stdexcept>

static const char MAGIC[] = "OCTRA-HFHE-BTY02";
static const int  MAGIC_LEN = 16;

static uint8_t  u8 (const uint8_t* p) { return *p; }
static uint32_t u32(const uint8_t* p) {
    uint32_t v; memcpy(&v, p, 4); return v;
}
static uint64_t u64(const uint8_t* p) {
    uint64_t v; memcpy(&v, p, 8); return v;
}

std::vector<uint8_t> decompress(const std::vector<uint8_t>& in) {
    std::vector<uint8_t> out(in.size() * 10);
    uLongf out_len = out.size();
    int rc;
    while ((rc = uncompress(out.data(), &out_len,
                             in.data(), in.size())) == Z_BUF_ERROR) {
        out.resize(out.size() * 2);
        out_len = out.size();
    }
    if (rc != Z_OK) throw std::runtime_error("zlib decompress failed");
    out.resize(out_len);
    return out;
}

int main(int argc, char** argv) {
    if (argc < 2) { fprintf(stderr, "Usage: %s secret.ct\n", argv[0]); return 1; }

    FILE* f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 1; }
    fseek(f, 0, SEEK_END);
    size_t sz = ftell(f);
    rewind(f);
    std::vector<uint8_t> raw(sz);
    fread(raw.data(), 1, sz, f);
    fclose(f);

    if (memcmp(raw.data(), MAGIC, MAGIC_LEN) != 0) {
        fprintf(stderr, "Bad magic\n"); return 1;
    }
    printf("Magic: OK\n");
    printf("Compressed size: %zu bytes\n", sz);

    std::vector<uint8_t> data(raw.begin() + MAGIC_LEN, raw.end());
    auto body = decompress(data);
    printf("Decompressed: %zu bytes\n", body.size());

    size_t off = 0;
    int n_cipher = 0, n_pubkey = 0, n_seckey = 0;
    while (off < body.size()) {
        uint8_t tag = u8(body.data() + off);  off += 1;
        uint64_t bsz = u64(body.data() + off); off += 8;
        if (tag == 0) {
            n_cipher++;
            // Parse edge count
            uint64_t n_edges = u64(body.data() + off);
            printf("  CT object %d: %llu edges\n",
                   n_cipher, (unsigned long long)n_edges);
        } else if (tag == 1) {
            n_pubkey++;
        } else if (tag == 2) {
            n_seckey++;
        }
        off += bsz;
    }
    printf("Total: %d cipher, %d pubkey, %d seckey objects\n",
           n_cipher, n_pubkey, n_seckey);
    return 0;
}
