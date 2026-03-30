#!/usr/bin/env python3
"""
Secure tfvars Parser for Session Resume
Parses terraform.tfvars and extracts ONLY valid HCL variable assignments.
Ignores comments (potential injection vectors) and validates values.
Returns clean JSON with recovered configuration.
"""

import sys
import re
import json
from pathlib import Path


# Allowed variable names that we expect in tfvars
ALLOWED_VARIABLES = {
    "aws_region", "aws_access_key", "aws_secret_key", "project_name",
    "vpc_name", "cidr_block", "subnets", "database", "ssh_keys",
    "compute", "object_storage", "container_registry",
}

# Validation rules for simple string values
VALIDATION_RULES = {
    "aws_region": r'^[a-z]{2}-[a-z]+-\d$',
    "project_name": r'^[a-z0-9][a-z0-9-]{2,29}$',
    "vpc_name": r'^[a-z0-9][a-z0-9-]{2,60}$',
    "cidr_block": r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$',
}

# Shell metacharacters that should NEVER appear in simple string values
DANGEROUS_CHARS = re.compile(r'[`$|;&<>]|\$\(|\$\{')

# Prompt injection patterns
INJECTION_PATTERNS = [
    r'ignore\s+(all\s+)?previous\s+instructions',
    r'ignore\s+(all\s+)?above',
    r'system\s*:\s*',
    r'assistant\s*:\s*',
    r'human\s*:\s*',
    r'you\s+are\s+now',
    r'new\s+instructions?\s*:',
    r'forget\s+(all|everything|your)',
    r'disregard\s+(all|previous|above)',
]


def check_injection(text):
    """Check if text contains prompt injection patterns."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def validate_simple_value(key, value):
    """Validate a simple string value against known rules."""
    if key in VALIDATION_RULES:
        if not re.match(VALIDATION_RULES[key], value):
            return False, f"Value for '{key}' fails validation: '{value}'"

    # Check for dangerous characters in simple values
    if DANGEROUS_CHARS.search(value):
        return False, f"Dangerous characters in value for '{key}'"

    # Check for injection in value
    if check_injection(value):
        return False, f"Potential injection detected in value for '{key}'"

    return True, None


def parse_tfvars(filepath):
    """
    Parse tfvars file extracting only valid variable assignments.
    Returns dict of recovered values and list of warnings.
    """
    result = {
        "recovered": {},
        "warnings": [],
        "injection_detected": False,
        "has_aws_access_key": False,
        "has_aws_secret_key": False,
    }

    try:
        content = Path(filepath).read_text()
    except FileNotFoundError:
        result["warnings"].append(f"File not found: {filepath}")
        return result

    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            i += 1
            continue

        # Skip ALL comments — these are injection vectors
        if stripped.startswith('#') or stripped.startswith('//'):
            if check_injection(stripped):
                result["injection_detected"] = True
                result["warnings"].append(f"Line {i+1}: Injection attempt detected in comment, IGNORED")
            i += 1
            continue

        # Match simple variable assignment: key = "value"
        simple_match = re.match(r'^(\w+)\s*=\s*"([^"]*)"', stripped)
        if simple_match:
            key, value = simple_match.group(1), simple_match.group(2)

            if key not in ALLOWED_VARIABLES:
                result["warnings"].append(f"Line {i+1}: Unknown variable '{key}', skipped")
                i += 1
                continue

            # Check for credential presence (don't extract values)
            if key == "aws_access_key":
                result["has_aws_access_key"] = True
                i += 1
                continue
            if key == "aws_secret_key":
                result["has_aws_secret_key"] = True
                i += 1
                continue

            valid, error = validate_simple_value(key, value)
            if valid:
                result["recovered"][key] = value
            else:
                result["warnings"].append(f"Line {i+1}: {error}")

            i += 1
            continue

        # Match start of complex block: key = [ or key = {
        block_match = re.match(r'^(\w+)\s*=\s*[\[\{]', stripped)
        if block_match:
            key = block_match.group(1)
            if key in ALLOWED_VARIABLES:
                # We note the variable exists but don't try to parse complex blocks
                # (they are used as-is by terraform, not displayed in chat)
                result["recovered"][f"_has_{key}"] = True
            i += 1
            continue

        i += 1

    return result


def main():
    if len(sys.argv) != 2:
        print("Usage: parse-tfvars.py <path/to/terraform.tfvars>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    result = parse_tfvars(filepath)

    print(json.dumps(result, indent=2))

    if result["injection_detected"]:
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
