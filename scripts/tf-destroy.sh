#!/bin/bash
# Terraform Destroy Wrapper
# Usage: bash scripts/tf-destroy.sh <project-directory>

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "ERROR: Invalid arguments"
  echo "Usage: bash scripts/tf-destroy.sh <project-directory>"
  exit 1
fi

PROJECT_DIR="$1"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "ERROR: Project directory does not exist: $PROJECT_DIR"
  exit 1
fi

cd "$PROJECT_DIR" || exit 1

echo "=== Terraform Destroy ==="
echo "Project: $PROJECT_DIR"
echo "WARNING: This will destroy all resources!"
echo ""

# Run terraform destroy with auto-approve
terraform destroy -auto-approve

exit $?
