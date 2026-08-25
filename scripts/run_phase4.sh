#!/usr/bin/env bash
# Phase 4: Public Key Structure
set -e
ARTIFACTS="${1:-$ARTIFACTS_DIR}"
python analysis/phase4_public_key/powg_analysis.py --artifacts "$ARTIFACTS"\n