#!/bin/bash
# Input Validation Wrapper
# Usage:
#   Field mode: bash scripts/validate-input.sh --field <name> --value <value>
#   Config mode: bash scripts/validate-input.sh --config <path-to-inputs.json>

set -euo pipefail

# Forward all arguments to Python validator
python3 "$(dirname "$0")/validate-config.py" "$@"
exit $?
