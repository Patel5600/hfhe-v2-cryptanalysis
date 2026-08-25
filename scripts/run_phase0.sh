#!/usr/bin/env bash
# Phase 0: Artifact verification
# Usage: bash scripts/run_phase0.sh /path/to/artifacts
set -e
ARTIFACTS="${1:-$ARTIFACTS_DIR}"
if [ -z "$ARTIFACTS" ]; then
  echo "Usage: $0 /path/to/artifacts"
  exit 1
fi
python analysis/phase0_artifacts/secret_ct_structure.py --artifacts "$ARTIFACTS"
