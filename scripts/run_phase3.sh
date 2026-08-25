#!/usr/bin/env bash
# Phase 3: Joint Key Distinguisher
set -e
ARTIFACTS="${1:-$ARTIFACTS_DIR}"
python analysis/phase3_joint_key/public_T_distinguisher.py --artifacts "$ARTIFACTS"\n