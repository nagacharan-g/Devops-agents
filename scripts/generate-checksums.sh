#!/bin/bash
# Generate Integrity Checksums
# Creates SHA256 checksums for all scripts and module files
# Run this ONCE after initial setup or after authorized changes
# Output: .integrity/checksums.sha256

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHECKSUM_DIR="$REPO_ROOT/.integrity"
CHECKSUM_FILE="$CHECKSUM_DIR/checksums.sha256"

mkdir -p "$CHECKSUM_DIR"

echo "Generating checksums for scripts and modules..."

# Clear existing checksums
> "$CHECKSUM_FILE"

# Checksum all scripts (excluding __pycache__)
find "$REPO_ROOT/scripts" -type f \( -name "*.sh" -o -name "*.py" \) ! -path "*__pycache__*" | sort | while read -r file; do
    rel_path="${file#$REPO_ROOT/}"
    shasum -a 256 "$file" | awk -v rp="$rel_path" '{print $1 "  " rp}' >> "$CHECKSUM_FILE"
done

# Checksum all module files
find "$REPO_ROOT/AWS/modules" -type f -name "*.tf" | sort | while read -r file; do
    rel_path="${file#$REPO_ROOT/}"
    shasum -a 256 "$file" | awk -v rp="$rel_path" '{print $1 "  " rp}' >> "$CHECKSUM_FILE"
done

# Checksum core terraform files
for tf_file in "$REPO_ROOT/AWS/main.tf" "$REPO_ROOT/AWS/provider.tf" "$REPO_ROOT/AWS/variables.tf" "$REPO_ROOT/AWS/outputs.tf"; do
    if [ -f "$tf_file" ]; then
        rel_path="${tf_file#$REPO_ROOT/}"
        shasum -a 256 "$tf_file" | awk -v rp="$rel_path" '{print $1 "  " rp}' >> "$CHECKSUM_FILE"
    fi
done

total=$(wc -l < "$CHECKSUM_FILE" | tr -d ' ')
echo "Checksums generated: $total files"
echo "Saved to: $CHECKSUM_FILE"
echo ""
echo "IMPORTANT: Commit .integrity/checksums.sha256 to version control."
echo "Re-run this script after any authorized changes to scripts or modules."
