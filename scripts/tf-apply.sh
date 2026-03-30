#!/bin/bash
# Terraform Apply Wrapper
# Usage: bash scripts/tf-apply.sh <project-directory>

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "ERROR: Invalid arguments"
  echo "Usage: bash scripts/tf-apply.sh <project-directory>"
  exit 1
fi

PROJECT_DIR="$1"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "ERROR: Project directory does not exist: $PROJECT_DIR"
  exit 1
fi

cd "$PROJECT_DIR" || exit 1

echo "=== Terraform Apply ==="
echo "Project: $PROJECT_DIR"
echo ""

# Run terraform apply with auto-approve
terraform apply -auto-approve

exit $?
