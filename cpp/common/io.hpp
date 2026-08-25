#pragma once
// Minimal I/O helpers for reading HFHE v2 binary artifacts
#include <cstdint>
#include <cstring>
#include <vector>
#include <fstream>
#include <stdexcept>
#include <string>

inline std::vector<uint8_t> read_file(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) throw std::runtime_error("Cannot open: " + path);
    return std::vector<uint8_t>(
        std::istreambuf_iterator<char>(f),
        std::istreambuf_iterator<char>());
}

inline uint8_t  read_u8 (const uint8_t* p) { return *p; }
inline uint32_t read_u32(const uint8_t* p) {
    uint32_t v; std::memcpy(&v, p, 4); return v;
}
inline uint64_t read_u64(const uint8_t* p) {
    uint64_t v; std::memcpy(&v, p, 8); return v;
}

// Write JSONL line
#include <iostream>
inline void jsonl_line(const std::string& s) {
    std::cout << s << "\n";
}
