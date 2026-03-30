#!/usr/bin/env python3
"""
Secure Handoff Parser for Config Skill
Extracts only known fields from handoff.json, validates formats, detects injection.

Usage: python3 scripts/parse-handoff-for-config.py projects/<project>/handoff.json
Exit codes: 0=success, 1=error, 2=injection detected
"""

import sys
import json
import re

IP_REGEX = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
PRIVATE_IP_REGEX = re.compile(r'^(10\.|172\.(1[6-9]|2\d|3[01])\.|192\.168\.)')
SHELL_METACHAR_REGEX = re.compile(r'[\$`|;&><()\{\}\[\]]')
SAFE_PATH_REGEX = re.compile(r'^[~./][a-zA-Z0-9_./-]+$')

def validate_ip(ip, label):
    """Validate IP format and octet range (0-255)"""
    if not IP_REGEX.match(ip):
        return f"Invalid IP for {label}: {ip}"
    octets = ip.split(".")
    if any(not (0 <= int(o) <= 255) for o in octets):
        return f"IP octet out of range for {label}: {ip}"
    return None

def validate_path(path, label):
    """Validate file path — no shell metacharacters"""
    if SHELL_METACHAR_REGEX.search(path):
        return f"INJECTION DETECTED: {label} contains shell metacharacters: {path}"
    if not SAFE_PATH_REGEX.match(path):
        return f"Invalid path for {label}: {path}"
    return None

def check_injection(value, label):
    """Check if a string value looks like injection"""
    if isinstance(value, str):
        if SHELL_METACHAR_REGEX.search(value):
            return f"Suspicious characters in {label}: {value[:50]}"
        # Check for common injection patterns
        for pattern in ['import ', 'eval(', 'exec(', '__', 'system(', 'subprocess']:
            if pattern in value.lower():
                return f"INJECTION DETECTED in {label}: contains '{pattern}'"
    return None

def parse_handoff(path):
    try:
        with open(path, 'r') as f:
            raw = f.read()
        data = json.loads(raw)
    except FileNotFoundError:
        return {"error": f"File not found: {path}"}, 1
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}, 1

    warnings = []
    errors = []
    result = {
        "nodes": {},
        "ssh_key_paths": {},
        "environment": None,
        "project_name": None,
        "vpc_id": None,
        "subnet_ids": []
    }

    # Extract environment and project
    # Normalise common aliases before validating
    ENV_ALIASES = {"production": "prod", "prod": "prod", "staging": "staging"}
    env_raw = data.get("environment", "")
    env = ENV_ALIASES.get(env_raw, "") if env_raw else ""
    project = data.get("project_name", "")
    if env:
        result["environment"] = env
    elif env_raw:
        errors.append(f"Invalid environment: {env_raw!r} (expected 'prod'/'production' or 'staging')")

    if project:
        inj = check_injection(project, "project_name")
        if inj:
            return {"error": inj}, 2
        result["project_name"] = project

    # Extract VPC info
    vpc_id = data.get("vpc_id", "")
    if vpc_id and isinstance(vpc_id, str):
        result["vpc_id"] = vpc_id

    subnet_ids = data.get("subnet_ids", [])
    if isinstance(subnet_ids, list):
        result["subnet_ids"] = subnet_ids

    # Extract EC2 instances
    ec2 = data.get("ec2_instances", {})
    if isinstance(ec2, dict):
        for name, info in ec2.items():
            if not isinstance(info, dict):
                warnings.append(f"Skipping non-dict instance: {name}")
                continue

            # Validate instance name
            inj = check_injection(name, f"instance_name:{name}")
            if inj:
                return {"error": inj}, 2

            public_ip = info.get("public_ip", "")
            private_ip = info.get("private_ip", "")
            role = info.get("tags", {}).get("Role", "unknown")

            # Validate IPs
            if public_ip:
                err = validate_ip(public_ip, f"{name}.public_ip")
                if err:
                    errors.append(err)
                    continue

            if private_ip:
                err = validate_ip(private_ip, f"{name}.private_ip")
                if err:
                    errors.append(err)
                    continue

            result["nodes"][name] = {
                "public_ip": public_ip,
                "private_ip": private_ip,
                "role": role,
                "instance_type": info.get("instance_type", "")
            }

    # Extract SSH key paths
    ssh_paths = data.get("ssh_key_paths", {})
    if isinstance(ssh_paths, dict):
        for key in ["mgmt_private_key_path", "internal_private_key_path"]:
            path_val = ssh_paths.get(key, "")
            if path_val:
                err = validate_path(path_val, key)
                if err:
                    if "INJECTION" in err:
                        return {"error": err}, 2
                    errors.append(err)
                else:
                    result["ssh_key_paths"][key] = path_val

        for key in ["mgmt_key_name", "internal_key_name"]:
            val = ssh_paths.get(key, "")
            if val:
                inj = check_injection(val, key)
                if inj:
                    return {"error": inj}, 2
                result["ssh_key_paths"][key] = val

    output = {
        "parsed": result,
        "warnings": warnings,
        "errors": errors,
        "injection_detected": False
    }

    print(json.dumps(output, indent=2))
    # Return code 1 if there are hard errors (not just warnings)
    return output, (1 if errors else 0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/parse-handoff-for-config.py <handoff.json>", file=sys.stderr)
        sys.exit(1)

    result, code = parse_handoff(sys.argv[1])
    if code == 2:
        print(json.dumps(result), file=sys.stderr)
        print("INJECTION DETECTED — do NOT use this handoff file", file=sys.stderr)
    sys.exit(code)
