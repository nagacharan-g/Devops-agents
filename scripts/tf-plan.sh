#!/bin/bash
# Terraform Plan Wrapper
# Usage: bash scripts/tf-plan.sh <project-directory>

set -euo pipefail

if [ $# -ne 1 ]; then
  echo "ERROR: Invalid arguments"
  echo "Usage: bash scripts/tf-plan.sh <project-directory>"
  exit 1
fi

PROJECT_DIR="$1"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "ERROR: Project directory does not exist: $PROJECT_DIR"
  exit 1
fi

# STATE CHECK: Validate terraform is initialized (INITIALIZED state)
if [ ! -d "$PROJECT_DIR/.terraform" ]; then
  echo "ERROR: Terraform not initialized in $PROJECT_DIR"
  echo "Current state: CONFIGURED"
  echo "Required state: INITIALIZED"
  echo "Suggestions:"
  echo "  - Run: bash scripts/tf-init.sh $PROJECT_DIR"
  exit 1
fi

cd "$PROJECT_DIR" || exit 1

echo "=== Terraform Plan ==="
echo "Project: $PROJECT_DIR"
echo ""

# Run terraform plan
terraform plan

exit $?
