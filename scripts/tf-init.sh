#!/bin/bash
# Terraform Init Wrapper
# Usage: bash scripts/tf-init.sh <project-directory>

set -euo pipefail

# Strict parameter validation
if [ $# -ne 1 ]; then
  echo "ERROR: Invalid arguments"
  echo "Usage: bash scripts/tf-init.sh <project-directory>"
  exit 1
fi

PROJECT_DIR="$1"

# Validate project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
  echo "ERROR: Project directory does not exist: $PROJECT_DIR"
  echo "Suggestions:"
  echo "  - Verify project directory path"
  echo "  - Ensure project structure was created"
  exit 1
fi

# Validate terraform files exist
if [ ! -f "$PROJECT_DIR/main.tf" ]; then
  echo "ERROR: main.tf not found in $PROJECT_DIR"
  echo "Suggestions:"
  echo "  - Ensure templates were extracted correctly"
  echo "  - Check project structure creation step"
  exit 1
fi

# STATE CHECK: Validate terraform.tfvars exists (CONFIGURED state)
if [ ! -f "$PROJECT_DIR/terraform.tfvars" ]; then
  echo "ERROR: terraform.tfvars not found in $PROJECT_DIR"
  echo "Current state: VALIDATED"
  echo "Required state: CONFIGURED"
  echo "Suggestions:"
  echo "  - Complete Step 9: Generate terraform.tfvars"
  echo "  - Complete Step 9.5: Configure AWS credentials"
  exit 1
fi

# Change to project directory
cd "$PROJECT_DIR" || exit 1

echo "=== Terraform Init ==="
echo "Project: $PROJECT_DIR"
echo ""

# Run terraform init
terraform init

exit $?
