#!/usr/bin/env python3
"""
Validate Handoff File Schema
Ensures handoff.json contains required fields for downstream agents
"""

import sys
import json
import argparse
from pathlib import Path

# Required fields in handoff.json
REQUIRED_FIELDS = [
    "vpc_id",
    "subnet_ids",
    "security_group_id"
]

# Conditional required fields
CONDITIONAL_FIELDS = {
    "rds_enabled": ["db_endpoint", "db_name"],
    "lambda_enabled": ["lambda_function_name", "lambda_role_arn"]
}

def validate_handoff(handoff_path):
    """Validate handoff.json schema and required fields"""
    try:
        with open(handoff_path, 'r') as f:
            handoff = json.load(f)
    except FileNotFoundError:
        return {"valid": False, "error": f"Handoff file not found: {handoff_path}"}
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"Invalid JSON in handoff file: {str(e)}"}

    errors = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in handoff:
            errors.append(f"Missing required field: {field}")
        elif not handoff[field]:
            errors.append(f"Empty value for required field: {field}")

    # Check conditional fields
    for condition, fields in CONDITIONAL_FIELDS.items():
        if handoff.get(condition):
            for field in fields:
                if field not in handoff:
                    errors.append(f"Missing conditional field: {field} (required when {condition}=true)")
                elif not handoff[field]:
                    errors.append(f"Empty value for conditional field: {field}")

    if errors:
        return {"valid": False, "errors": errors}

    return {"valid": True, "message": "Handoff file is valid"}

def main():
    parser = argparse.ArgumentParser(description="Validate handoff.json schema")
    parser.add_argument("handoff_path", help="Path to handoff.json file")

    args = parser.parse_args()

    result = validate_handoff(args.handoff_path)
    print(json.dumps(result, indent=2))

    sys.exit(0 if result["valid"] else 1)

if __name__ == "__main__":
    main()
