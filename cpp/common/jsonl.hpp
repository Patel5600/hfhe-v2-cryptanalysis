#pragma once
#include <string>
#include <iostream>
#include <fstream>
#include <sstream>

namespace jsonl {

inline void emit(const std::string& key, double val, bool last = false) {
    std::cout << "\"" << key << "\": " << val << (last ? "" : ", ");
}

inline void emit(const std::string& key, const std::string& val, bool last = false) {
    std::cout << "\"" << key << "\": \"" << val << "\"" << (last ? "" : ", ");
}

inline void emit_line(const std::string& json_str) {
    std::cout << json_str << "\n";
}

} // namespace jsonl\n