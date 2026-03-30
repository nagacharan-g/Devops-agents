#!/usr/bin/env python3
"""
Sanitize Terraform Output for Chat Display
Filters terraform plan/apply output to show ONLY resource counts and status.
Strips IPs, ARNs, credentials, endpoints, and any raw resource details.
Prevents prompt injection via terraform output content.
"""

import sys
import re


# Patterns that indicate sensitive data - never display lines matching these
SENSITIVE_PATTERNS = [
    r'(?:public_ip|private_ip|endpoint|address)\s*=',
    r'(?:access_key|secret_key|password|token)\s*=',
    r'arn:aws:',
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP addresses
    r'ami-[a-z0-9]+',
    r'sg-[a-z0-9]+',
    r'subnet-[a-z0-9]+',
    r'vpc-[a-z0-9]+',
    r'igw-[a-z0-9]+',
    r'rtb-[a-z0-9]+',
    r'i-[a-z0-9]{8,}',  # Instance IDs
    r'db-[A-Z0-9]+',  # RDS instance IDs
    r'AKIA[A-Z0-9]{16}',  # AWS access key IDs
]

# Patterns that are safe to display
SAFE_PATTERNS = [
    r'Plan:\s+\d+\s+to add',
    r'Apply complete!.*Resources:',
    r'\d+ to add, \d+ to change, \d+ to destroy',
    r'No changes\.',
    r'Terraform has been successfully initialized',
    r'Initializing',
    r'Creating\.\.\.',
    r'Creation complete',
    r'Still creating',
    r'Destroying\.\.\.',
    r'Destruction complete',
    r'Error:',
    r'Warning:',
    r'Planning failed',
    r'Apply failed',
    r'module\.\w+\.\w+\.\w+\[',  # Resource addresses (without values)
]

# Patterns that look like prompt injection attempts
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


def is_sensitive(line):
    """Check if a line contains sensitive data."""
    stripped = line.strip()
    # Skip ANSI color code stripping for matching
    clean = re.sub(r'\x1b\[[0-9;]*m', '', stripped)
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, clean, re.IGNORECASE):
            return True
    return False


def is_safe(line):
    """Check if a line is safe to display."""
    stripped = line.strip()
    clean = re.sub(r'\x1b\[[0-9;]*m', '', stripped)
    for pattern in SAFE_PATTERNS:
        if re.search(pattern, clean, re.IGNORECASE):
            return True
    return False


def has_injection(line):
    """Check if a line looks like a prompt injection attempt."""
    clean = re.sub(r'\x1b\[[0-9;]*m', '', line)
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, clean, re.IGNORECASE):
            return True
    return False


def extract_summary(lines):
    """Extract a safe summary from terraform output."""
    summary = {
        "resources_add": 0,
        "resources_change": 0,
        "resources_destroy": 0,
        "status": "unknown",
        "creating": [],
        "errors": [],
        "injection_detected": False,
    }

    for line in lines:
        clean = re.sub(r'\x1b\[[0-9;]*m', '', line).strip()

        # Check for injection attempts
        if has_injection(clean):
            summary["injection_detected"] = True
            continue

        # Extract plan counts
        plan_match = re.search(r'(\d+) to add, (\d+) to change, (\d+) to destroy', clean)
        if plan_match:
            summary["resources_add"] = int(plan_match.group(1))
            summary["resources_change"] = int(plan_match.group(2))
            summary["resources_destroy"] = int(plan_match.group(3))

        # Extract status
        if 'Apply complete' in clean:
            res_match = re.search(r'Resources:\s*(\d+) added, (\d+) changed, (\d+) destroyed', clean)
            if res_match:
                summary["resources_add"] = int(res_match.group(1))
                summary["resources_change"] = int(res_match.group(2))
                summary["resources_destroy"] = int(res_match.group(3))
            summary["status"] = "applied"

        if 'successfully initialized' in clean:
            summary["status"] = "initialized"

        if 'Planning failed' in clean or 'Apply failed' in clean:
            summary["status"] = "failed"

        # Track resource creation (address only, no values)
        create_match = re.search(r'(module\.\w+\.\w+\.\w+(?:\[.*?\])?):?\s*(?:Creating|Creation complete|Still creating)', clean)
        if create_match:
            resource = create_match.group(1)
            if resource not in summary["creating"]:
                summary["creating"].append(resource)

        # Capture errors (but sanitize them)
        if re.match(r'\s*Error:', clean):
            # Only keep the error type, strip specific values
            error_clean = re.sub(r'(?:password|key|secret|token|credential)\s*[=:]\s*\S+', '[REDACTED]', clean, flags=re.IGNORECASE)
            error_clean = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '[IP]', error_clean)
            summary["errors"].append(error_clean)

    return summary


def format_summary(summary):
    """Format the summary for safe chat display."""
    output = []

    if summary["injection_detected"]:
        output.append("[SECURITY WARNING] Potential prompt injection detected in terraform output. Review raw logs manually.")
        output.append("")

    if summary["status"] == "applied":
        output.append(f"Apply complete! {summary['resources_add']} added, {summary['resources_change']} changed, {summary['resources_destroy']} destroyed.")
    elif summary["status"] == "initialized":
        output.append("Terraform initialized successfully.")
    elif summary["status"] == "failed":
        output.append("Terraform operation failed.")
        for err in summary["errors"]:
            output.append(f"  {err}")
    else:
        if summary["resources_add"] or summary["resources_change"] or summary["resources_destroy"]:
            output.append(f"Plan: {summary['resources_add']} to add, {summary['resources_change']} to change, {summary['resources_destroy']} to destroy.")

    if summary["creating"]:
        output.append(f"Resources processed: {len(summary['creating'])}")

    return "\n".join(output)


def main():
    """Read terraform output from stdin or file and output sanitized version."""
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)
    else:
        lines = sys.stdin.readlines()

    summary = extract_summary(lines)
    print(format_summary(summary))

    if summary["injection_detected"]:
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
