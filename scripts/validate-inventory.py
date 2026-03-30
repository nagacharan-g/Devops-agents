#!/usr/bin/env python3
"""
Validate Ansible Inventory (hosts.yml)
Checks structure, IP formats, alias names, and detects injection.

Usage: python3 scripts/validate-inventory.py inventories/<env>/hosts.yml
Exit codes: 0=valid, 1=invalid, 2=injection detected
"""

import sys
import re
import yaml

IP_REGEX = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
PRIVATE_IP_REGEX = re.compile(r'^(10\.|172\.(1[6-9]|2\d|3[01])\.|192\.168\.)')
HOSTNAME_REGEX = re.compile(r'^[a-z][a-z0-9-]{0,62}$')
ALIAS_REGEX = re.compile(r'^[a-z][a-z0-9-]{0,29}$')
SHELL_METACHAR_REGEX = re.compile(r'[\$`|;&><()\{\}\[\]]')

def validate(path):
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        return {"valid": False, "errors": [f"File not found: {path}"]}, 1
    except yaml.YAMLError as e:
        return {"valid": False, "errors": [f"Invalid YAML: {e}"]}, 1

    errors = []
    warnings = []

    if not isinstance(data, dict) or 'all' not in data:
        errors.append("Missing top-level 'all' key")
        return {"valid": False, "errors": errors}, 1

    children = data.get('all', {}).get('children', {})
    if not isinstance(children, dict):
        errors.append("Missing 'all.children' section")
        return {"valid": False, "errors": errors}, 1

    # Validate management group
    mgmt = children.get('management', {})
    if not mgmt:
        errors.append("Missing 'management' group")
    else:
        hosts = mgmt.get('hosts', {})
        if not hosts or 'management_node' not in hosts:
            errors.append("Missing 'management_node' host in management group")
        else:
            node = hosts['management_node']
            if not isinstance(node, dict):
                errors.append("management_node has no configuration")
            else:
                ip = str(node.get('ansible_host', ''))
                if not IP_REGEX.match(ip):
                    errors.append(f"management_node: invalid IP '{ip}'")
                if SHELL_METACHAR_REGEX.search(ip):
                    return {"valid": False, "errors": ["INJECTION: shell metacharacters in management IP"]}, 2

                port = node.get('ansible_port', 10022)
                if not isinstance(port, int) or port < 1 or port > 65535:
                    errors.append(f"management_node: invalid port '{port}'")

                aliases = node.get('alias', [])
                if not aliases:
                    errors.append("management_node: missing 'alias' list")
                else:
                    for a in aliases:
                        if not ALIAS_REGEX.match(str(a)):
                            errors.append(f"management_node: invalid alias '{a}'")

    # Validate std_nodes (if present and not commented)
    std = children.get('std_nodes', {})
    if std and isinstance(std, dict):
        hosts = std.get('hosts', {})
        if isinstance(hosts, dict):
            for hostname, config in hosts.items():
                # Validate hostname
                if SHELL_METACHAR_REGEX.search(str(hostname)):
                    return {"valid": False, "errors": [f"INJECTION: shell metacharacters in hostname '{hostname}'"]}, 2

                if not isinstance(config, dict):
                    errors.append(f"{hostname}: no configuration")
                    continue

                ip = str(config.get('ansible_host', ''))
                if not IP_REGEX.match(ip):
                    errors.append(f"{hostname}: invalid IP '{ip}'")
                elif not PRIVATE_IP_REGEX.match(ip):
                    warnings.append(f"{hostname}: IP '{ip}' is not in private range")

                if SHELL_METACHAR_REGEX.search(ip):
                    return {"valid": False, "errors": [f"INJECTION: shell metacharacters in {hostname} IP"]}, 2

                aliases = config.get('alias', [])
                if not aliases:
                    errors.append(f"{hostname}: missing 'alias' list (required for user creation)")
                else:
                    for a in aliases:
                        a_str = str(a)
                        if not ALIAS_REGEX.match(a_str):
                            errors.append(f"{hostname}: invalid alias '{a_str}'")
                        if SHELL_METACHAR_REGEX.search(a_str):
                            return {"valid": False, "errors": [f"INJECTION: shell metacharacters in alias '{a_str}'"]}, 2

    # Validate k3s_cluster (if present and not commented)
    k3s = children.get('k3s_cluster', {})
    if k3s and isinstance(k3s, dict):
        k3s_children = k3s.get('children', {})
        if isinstance(k3s_children, dict):
            for group_name in ['k3s_master', 'k3s_worker']:
                group = k3s_children.get(group_name, {})
                if group and isinstance(group, dict):
                    hosts = group.get('hosts', {})
                    if isinstance(hosts, dict):
                        for hostname, config in hosts.items():
                            if SHELL_METACHAR_REGEX.search(str(hostname)):
                                return {"valid": False, "errors": [f"INJECTION in k3s hostname '{hostname}'"]}, 2
                            if isinstance(config, dict):
                                ip = str(config.get('ansible_host', ''))
                                if not IP_REGEX.match(ip):
                                    errors.append(f"{hostname}: invalid IP '{ip}'")
                                if SHELL_METACHAR_REGEX.search(ip):
                                    return {"valid": False, "errors": [f"INJECTION in {hostname} IP"]}, 2

    result = {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

    import json
    print(json.dumps(result, indent=2))
    return result, 0 if result["valid"] else 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate-inventory.py <hosts.yml>", file=sys.stderr)
        sys.exit(1)
    _, code = validate(sys.argv[1])
    sys.exit(code)
