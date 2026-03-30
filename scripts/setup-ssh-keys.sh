#!/bin/bash
# Secure SSH Key Setup Script
# Copies, validates, and verifies SSH keys for the config skill.
#
# Usage: bash scripts/setup-ssh-keys.sh <env> <mgmt-key-source> <internal-key-source> [<expected-mgmt-fingerprint>]
#
# Security:
#   - NEVER outputs key content
#   - Validates file paths (no shell metacharacters)
#   - Validates key format with ssh-keygen
#   - Optionally verifies fingerprint matches deployed key
#   - Sets 400 permissions atomically with copy
#
# Example:
#   bash scripts/setup-ssh-keys.sh staging ~/.ssh/test-coe-charan ~/.ssh/internal_test-coe-naga_staging
#   bash scripts/setup-ssh-keys.sh staging ~/.ssh/test-coe-charan ~/.ssh/internal_test-coe-naga_staging "SHA256:abc..."

set -euo pipefail

# --- Input validation ---

if [ $# -lt 3 ] || [ $# -gt 4 ]; then
    echo "ERROR: Invalid arguments"
    echo "Usage: bash scripts/setup-ssh-keys.sh <env> <mgmt-key-source> <internal-key-source> [<expected-mgmt-fingerprint>]"
    exit 1
fi

ENV="$1"
MGMT_SRC="$2"
INTERNAL_SRC="$3"
EXPECTED_FP="${4:-}"

# Validate environment
if [[ ! "$ENV" =~ ^(staging|prod)$ ]]; then
    echo "ERROR: Environment must be 'staging' or 'prod', got: '$ENV'"
    exit 1
fi

# Validate paths — reject shell metacharacters (anti-injection)
validate_path() {
    local path="$1"
    local label="$2"
    if [[ "$path" =~ [\$\`\|\;\&\>\<\(\)\{\}\[\]] ]]; then
        echo "ERROR: $label path contains invalid characters: '$path'"
        echo "ERROR: Shell metacharacters are not allowed in key paths"
        exit 2
    fi
    if [ ! -f "$path" ]; then
        echo "ERROR: $label file does not exist: '$path'"
        exit 1
    fi
}

validate_path "$MGMT_SRC" "Management key"
validate_path "$INTERNAL_SRC" "Internal key"

# --- Setup destination ---

DEST_DIR="infra-configuration/AWS/keys/$ENV"

if [ ! -d "infra-configuration/AWS" ]; then
    echo "ERROR: infra-configuration/AWS/ directory not found. Run from repo root."
    exit 1
fi

mkdir -p "$DEST_DIR"

# --- Copy and validate management key ---

echo "=== SSH Key Setup for '$ENV' ==="
echo ""

echo "[1/4] Copying management key..."
# Use install to copy + set permissions atomically (avoids chmod race)
install -m 400 "$MGMT_SRC" "$DEST_DIR/mgmt.pem"

echo "[2/4] Validating management key..."
MGMT_FP=$(ssh-keygen -l -f "$DEST_DIR/mgmt.pem" 2>&1) || {
    echo "ERROR: Management key is INVALID after copy."
    echo "ERROR: ssh-keygen output: $MGMT_FP"
    echo ""
    echo "Common causes:"
    echo "  - Source file is not a valid SSH private key"
    echo "  - File was modified by an IDE (trailing newline stripped)"
    echo "  - File encoding is wrong (must be UTF-8, LF line endings)"
    rm -f "$DEST_DIR/mgmt.pem"
    exit 1
}

# Extract just the fingerprint hash (e.g., SHA256:abc...) for comparison
MGMT_FP_HASH=$(echo "$MGMT_FP" | awk '{print $2}')
echo "  Fingerprint: $MGMT_FP_HASH"
echo "  Status: VALID"

# Verify fingerprint if expected value provided
if [ -n "$EXPECTED_FP" ]; then
    if [ "$MGMT_FP_HASH" = "$EXPECTED_FP" ]; then
        echo "  Fingerprint match: YES"
    else
        echo "  WARNING: Fingerprint does NOT match expected value!"
        echo "  Expected: $EXPECTED_FP"
        echo "  Got:      $MGMT_FP_HASH"
        echo "  This key may not match the public key deployed to AWS."
        echo ""
        read -p "  Continue anyway? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Aborted. Remove incorrect key."
            rm -f "$DEST_DIR/mgmt.pem"
            exit 1
        fi
    fi
fi

# --- Copy and validate internal key ---

echo ""
echo "[3/4] Copying internal key..."
install -m 400 "$INTERNAL_SRC" "$DEST_DIR/internal.pem"

echo "[4/4] Validating internal key..."
INTERNAL_FP=$(ssh-keygen -l -f "$DEST_DIR/internal.pem" 2>&1) || {
    echo "ERROR: Internal key is INVALID after copy."
    echo "ERROR: ssh-keygen output: $INTERNAL_FP"
    echo ""
    echo "Common causes:"
    echo "  - Source file is not a valid SSH private key"
    echo "  - File was modified by an IDE (trailing newline stripped)"
    echo "  - File encoding is wrong (must be UTF-8, LF line endings)"
    rm -f "$DEST_DIR/internal.pem"
    exit 1
}

INTERNAL_FP_HASH=$(echo "$INTERNAL_FP" | awk '{print $2}')
echo "  Fingerprint: $INTERNAL_FP_HASH"
echo "  Status: VALID"

# --- Final verification ---

echo ""
echo "=== Verification ==="
echo ""

# Verify files exist with correct permissions
MGMT_PERMS=$(stat -f "%Lp" "$DEST_DIR/mgmt.pem" 2>/dev/null || stat -c "%a" "$DEST_DIR/mgmt.pem" 2>/dev/null)
INTERNAL_PERMS=$(stat -f "%Lp" "$DEST_DIR/internal.pem" 2>/dev/null || stat -c "%a" "$DEST_DIR/internal.pem" 2>/dev/null)

MGMT_SIZE=$(wc -c < "$DEST_DIR/mgmt.pem" | tr -d ' ')
INTERNAL_SIZE=$(wc -c < "$DEST_DIR/internal.pem" | tr -d ' ')

echo "  mgmt.pem:     ${MGMT_SIZE} bytes, permissions ${MGMT_PERMS}, VALID"
echo "  internal.pem: ${INTERNAL_SIZE} bytes, permissions ${INTERNAL_PERMS}, VALID"

# Check for potential issues
ISSUES=0

if [ "$MGMT_PERMS" != "400" ]; then
    echo "  WARNING: mgmt.pem permissions are $MGMT_PERMS, should be 400"
    ISSUES=$((ISSUES + 1))
fi

if [ "$INTERNAL_PERMS" != "400" ]; then
    echo "  WARNING: internal.pem permissions are $INTERNAL_PERMS, should be 400"
    ISSUES=$((ISSUES + 1))
fi

# Verify keys are different files (mgmt ≠ internal)
if [ "$MGMT_FP_HASH" = "$INTERNAL_FP_HASH" ]; then
    echo "  ERROR: Management and internal keys have the SAME fingerprint!"
    echo "  ERROR: These must be DIFFERENT key pairs for security isolation."
    exit 1
fi

echo ""
if [ $ISSUES -eq 0 ]; then
    echo "=== SUCCESS: All keys validated and installed ==="
else
    echo "=== PARTIAL: Keys installed with $ISSUES warning(s) ==="
fi
echo ""
echo "Keys installed to: $DEST_DIR/"
echo "  mgmt.pem     → SSH to management node"
echo "  internal.pem  → SSH to app/k3s nodes (via mgmt jump)"
