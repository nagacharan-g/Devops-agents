#!/usr/bin/env python3
"""
Input Validation Script for Terraform Skill
Validates user inputs against defined rules from REFERENCE.md
Prevents invalid configurations from reaching Terraform
"""

import sys
import re
import json
import argparse

# Validation rules (see REFERENCE.md for complete list)
RULES = {
    "environment": r"^(staging|production)$",
    "project_name": r"^[a-z][a-z0-9-]{2,29}$",
    "region": r"^(ap-south-1|ap-northeast-1|ap-southeast-1|us-east-1|us-east-2|us-west-1|us-west-2|eu-west-1|eu-west-2|eu-central-1)$",
    "lambda": r"^(yes|no)$",
    "node_count": r"^([1-9]|10)$",
    "instance_type": r"^(t3|t4g|m5|c5)\.(micro|small|medium|large|xlarge|2xlarge|4xlarge)$",
    "disk_size": r"^(30|50|100|200)$",
    "db_engine": r"^(postgres|mysql)$",
    "db_version": r"^(15|16|17|8\.0|8\.4)$",
    "db_instance": r"^db\.(t3|t4g)\.(micro|small|medium|large)$",
    "db_storage": r"^(20|50|100|200)$",
    "multi_az": r"^(yes|no)$",
    "vpc_cidr": r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$",
    "lambda_runtime": r"^(python3\.(10|11|12)|nodejs(18|20)\.x)$"
}

def validate_field(name, value):
    """Validate a single field against its rule"""
    if name not in RULES:
        return {"valid": True, "message": f"No validation rule for {name}"}

    if not re.match(RULES[name], value, re.IGNORECASE):
        return {
            "valid": False,
            "error": f"Invalid {name}: {value}",
            "suggestion": f"See REFERENCE.md for {name} validation rules"
        }

    return {"valid": True}

def validate_config(config_path):
    """Validate entire configuration file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        errors = []
        for field, value in config.items():
            result = validate_field(field, str(value))
            if not result["valid"]:
                errors.append(result)

        if errors:
            return {"valid": False, "errors": errors}

        return {"valid": True, "message": "All fields valid"}

    except FileNotFoundError:
        return {"valid": False, "error": f"Config file not found: {config_path}"}
    except json.JSONDecodeError as e:
        return {"valid": False, "error": f"Invalid JSON: {str(e)}"}

def main():
    parser = argparse.ArgumentParser(description="Validate Terraform inputs")
    parser.add_argument("--field", help="Field name to validate")
    parser.add_argument("--value", help="Field value to validate")
    parser.add_argument("--config", help="Path to config JSON file")

    args = parser.parse_args()

    if args.field and args.value:
        # Field mode
        result = validate_field(args.field, args.value)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["valid"] else 1)

    elif args.config:
        # Config mode
        result = validate_config(args.config)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["valid"] else 1)

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
