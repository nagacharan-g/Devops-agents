#!/usr/bin/env python3
"""
Generate Handoff File from Terraform Outputs
Extracts outputs and creates structured handoff.json for downstream agents
"""

import sys
import json
import subprocess
import os
from pathlib import Path

def get_terraform_outputs(project_dir):
    """Run terraform output and parse JSON"""
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to get terraform outputs: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON from terraform output: {str(e)}", file=sys.stderr)
        sys.exit(1)

def generate_handoff(project_dir):
    """Generate handoff.json from terraform outputs"""
    outputs = get_terraform_outputs(project_dir)

    # Extract values from terraform output format
    handoff = {}
    for key, value_obj in outputs.items():
        if isinstance(value_obj, dict) and "value" in value_obj:
            handoff[key] = value_obj["value"]
        else:
            handoff[key] = value_obj

    # Write to handoff.json
    handoff_path = Path(project_dir) / "handoff.json"
    try:
        with open(handoff_path, 'w') as f:
            json.dump(handoff, f, indent=2)
        print(f"✓ Handoff file created: {handoff_path}")
        return handoff
    except IOError as e:
        print(f"ERROR: Failed to write handoff file: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: generate-handoff.py <project-directory>", file=sys.stderr)
        sys.exit(1)

    project_dir = sys.argv[1]

    if not os.path.isdir(project_dir):
        print(f"ERROR: Project directory does not exist: {project_dir}", file=sys.stderr)
        sys.exit(1)

    handoff = generate_handoff(project_dir)

    # Print SAFE summary only — never print full handoff (contains IPs, keys, credentials)
    SENSITIVE_KEYS = {
        "s3_user_access_key", "s3_user_secret_key",
        "ec2_instances", "security_groups", "security_group_id",
        "primary_rds_instance_ids", "rds_security_group_ids",
        "ecr_repository_urls", "vpc_id", "subnet_ids",
        "ec2_key_pairs",
    }
    safe_summary = {k: v for k, v in handoff.items() if k not in SENSITIVE_KEYS}

    print("\n=== Handoff Summary (sanitized — sensitive fields written to file only) ===")
    print(json.dumps(safe_summary, indent=2))
    print("\n[REDACTED] Fields written to handoff.json but not shown: " +
          ", ".join(k for k in handoff if k in SENSITIVE_KEYS))

if __name__ == "__main__":
    main()
