#!/bin/bash
# Validate Project Directory Name
# Ensures project names match safe pattern, rejects anything suspicious
# Exit codes: 0 = valid, 1 = invalid

set -euo pipefail

PROJECT_NAME="${1:-}"

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: validate-project-name.sh <project-name>"
    exit 1
fi

# Must match: lowercase alphanumeric + hyphens, 3-30 chars, starts with alphanumeric
if [[ "$PROJECT_NAME" =~ ^[a-z0-9][a-z0-9-]{2,29}$ ]]; then
    # Additional check: no consecutive hyphens, no trailing hyphen
    if [[ "$PROJECT_NAME" =~ -- ]] || [[ "$PROJECT_NAME" =~ -$ ]]; then
        echo "INVALID: Project name cannot have consecutive or trailing hyphens: $PROJECT_NAME"
        exit 1
    fi

    # Check for shell metacharacters (should never match given regex, but defense in depth)
    if echo "$PROJECT_NAME" | grep -qE '[\$\`\|;&<>(){}!\[\]\\]'; then
        echo "INVALID: Project name contains dangerous characters: $PROJECT_NAME"
        exit 1
    fi

    echo "VALID"
    exit 0
else
    echo "INVALID: Project name must be 3-30 chars, lowercase alphanumeric and hyphens only, start with alphanumeric: $PROJECT_NAME"
    exit 1
fi
