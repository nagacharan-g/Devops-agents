#!/bin/bash
# Check Current Terraform State
# Detects the current state of a terraform project based on file presence

set -euo pipefail

PROJECT_DIR="${1:-.}"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "ERROR: Project directory does not exist: $PROJECT_DIR"
  exit 1
fi

# State detection logic based on file presence
detect_state() {
  local dir="$1"

  # Check for completion marker
  if [ -f "$dir/.complete" ]; then
    echo "COMPLETE"
    return
  fi

  # Check for terraform state (APPLIED)
  if [ -f "$dir/terraform.tfstate" ] && [ -s "$dir/terraform.tfstate" ]; then
    # Check if outputs exist (FINALIZED)
    if [ -f "$dir/outputs.txt" ] && [ -f "$dir/handoff.json" ]; then
      echo "FINALIZED"
    else
      echo "APPLIED"
    fi
    return
  fi

  # Check for plan file (PLANNED)
  if [ -f "$dir/tfplan.binary" ]; then
    echo "PLANNED"
    return
  fi

  # Check if terraform is initialized (INITIALIZED)
  if [ -d "$dir/.terraform" ]; then
    echo "INITIALIZED"
    return
  fi

  # Check for configuration (CONFIGURED)
  if [ -f "$dir/terraform.tfvars" ]; then
    echo "CONFIGURED"
    return
  fi

  # Check for terraform templates (VALIDATED)
  if [ -f "$dir/main.tf" ] && [ -f "$dir/provider.tf" ]; then
    echo "VALIDATED"
    return
  fi

  # Check if project directory exists (INIT)
  echo "INIT"
}

# Detect and display current state
CURRENT_STATE=$(detect_state "$PROJECT_DIR")

echo "Current State: $CURRENT_STATE"
echo ""
echo "Valid transitions from $CURRENT_STATE:"

case "$CURRENT_STATE" in
  INIT)
    echo "  → VALIDATED (create terraform templates)"
    ;;
  VALIDATED)
    echo "  → CONFIGURED (create terraform.tfvars, configure credentials)"
    ;;
  CONFIGURED)
    echo "  → INITIALIZED (run terraform init)"
    ;;
  INITIALIZED)
    echo "  → PLANNED (run terraform plan)"
    ;;
  PLANNED)
    echo "  → APPLIED (run terraform apply)"
    ;;
  APPLIED)
    echo "  → FINALIZED (generate outputs.txt and handoff.json)"
    ;;
  FINALIZED)
    echo "  → COMPLETE (mark deployment complete)"
    ;;
  COMPLETE)
    echo "  No further transitions (deployment complete)"
    ;;
esac

exit 0
