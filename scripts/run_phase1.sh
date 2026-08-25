#!/usr/bin/env bash
# Phase 1: Ciphertext Structure
set -e
ARTIFACTS="${1:-$ARTIFACTS_DIR}"
python analysis/phase1_ciphertext/cross_layer_prf.py --artifacts "$ARTIFACTS"\n