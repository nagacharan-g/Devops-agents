#!/bin/bash
# Verify Integrity of Scripts and Modules
# Compares current file hashes against stored checksums
# Exit codes: 0 = all good, 1 = tampering detected, 2 = no checksums found

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHECKSUM_FILE="$REPO_ROOT/.integrity/checksums.sha256"

if [ ! -f "$CHECKSUM_FILE" ]; then
    echo "WARNING: No checksum file found at $CHECKSUM_FILE"
    echo "Run 'bash scripts/generate-checksums.sh' to create initial checksums."
    exit 2
fi

FAILED=0
PASSED=0
MISSING=0

echo "=== Integrity Verification ==="
echo ""

while IFS='  ' read -r expected_hash rel_path; do
    # Skip empty lines
    [ -z "$expected_hash" ] && continue
    [ -z "$rel_path" ] && continue

    full_path="$REPO_ROOT/$rel_path"

    if [ ! -f "$full_path" ]; then
        echo "MISSING: $rel_path"
        MISSING=$((MISSING + 1))
        continue
    fi

    actual_hash=$(shasum -a 256 "$full_path" | awk '{print $1}')

    if [ "$expected_hash" = "$actual_hash" ]; then
        PASSED=$((PASSED + 1))
    else
        echo "TAMPERED: $rel_path"
        echo "  Expected: $expected_hash"
        echo "  Actual:   $actual_hash"
        FAILED=$((FAILED + 1))
    fi
done < "$CHECKSUM_FILE"

echo ""
echo "Results: $PASSED passed, $FAILED tampered, $MISSING missing"

if [ $FAILED -gt 0 ] || [ $MISSING -gt 0 ]; then
    echo ""
    echo "[SECURITY ALERT] File integrity check failed!"
    echo "Do NOT proceed with deployment until tampering is investigated."
    echo ""
    echo "If changes were authorized, re-run: bash scripts/generate-checksums.sh"
    exit 1
fi

echo "All files verified successfully."
exit 0
