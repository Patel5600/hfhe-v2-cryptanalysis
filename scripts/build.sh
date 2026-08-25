#!/usr/bin/env bash
# Build all C++ experiment binaries
# Requires: g++, zlib-dev
# Usage: bash scripts/build.sh

set -e
BASE="$(cd "$(dirname "$0")/.."; pwd)"
CPP="$BASE/cpp"
BIN="$BASE/bin"
mkdir -p "$BIN"

echo "=== Building C++ experiment binaries ==="

g++ -O2 -std=c++17 \
    -I"$CPP/common" \
    "$CPP/artifact/secret_ct_parser.cpp" \
    "$CPP/common/field.cpp" \
    -lz -o "$BIN/secret_ct_parser"
echo "  [OK] secret_ct_parser"

g++ -O2 -std=c++17 \
    "$CPP/experiments/cross_field_test.cpp" \
    -o "$BIN/cross_field_test"
echo "  [OK] cross_field_test"

echo "=== Build complete ==="
echo "Binaries in: $BIN"
