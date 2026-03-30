#!/usr/bin/env python3
"""
Sanitize Ansible Playbook Output for Chat Display
Extracts ONLY PLAY RECAP task counts. Strips IPs, hostnames, and all
role/task detail lines. Prevents prompt injection via Ansible output.

Usage:
    ansible-playbook ... 2>&1 | tee /tmp/playbook.log | python3 scripts/sanitize-ansible-output.py
    python3 scripts/sanitize-ansible-output.py /tmp/playbook.log

Exit codes: 0=success, 1=failures detected, 2=injection detected
"""

import sys
import re

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')

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

IP_PATTERN = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
HOSTNAME_PATTERN = re.compile(r'\b[a-z][a-z0-9-]{2,62}\b')

# PLAY RECAP line format:
# <hostname> : ok=N changed=N unreachable=N failed=N skipped=N rescued=N ignored=N
RECAP_LINE = re.compile(
    r'^(.+?)\s*:\s*ok=(\d+)\s+changed=(\d+)\s+unreachable=(\d+)\s+failed=(\d+)'
    r'(?:\s+skipped=(\d+))?(?:\s+rescued=(\d+))?(?:\s+ignored=(\d+))?'
)


def clean(line):
    return ANSI_ESCAPE.sub('', line).strip()


def has_injection(line):
    text = clean(line).lower()
    for p in INJECTION_PATTERNS:
        if re.search(p, text):
            return True
    return False


def parse_recap(lines):
    in_recap = False
    recap_entries = []
    injection_detected = False
    fatal_lines = []

    for raw in lines:
        line = clean(raw)

        if has_injection(line):
            injection_detected = True
            continue

        if line.startswith('PLAY RECAP'):
            in_recap = True
            continue

        if in_recap:
            m = RECAP_LINE.match(line)
            if m:
                recap_entries.append({
                    "ok":          int(m.group(2)),
                    "changed":     int(m.group(3)),
                    "unreachable": int(m.group(4)),
                    "failed":      int(m.group(5)),
                    "skipped":     int(m.group(6) or 0),
                    "rescued":     int(m.group(7) or 0),
                    "ignored":     int(m.group(8) or 0),
                })
            elif line:
                in_recap = False  # End of recap block

        # Capture fatal errors (host and detail redacted)
        if line.startswith('fatal:') or 'FAILED!' in line:
            # Strip IP addresses and long strings, keep error type only
            redacted = IP_PATTERN.sub('[IP]', line)
            redacted = re.sub(r'"msg":\s*"[^"]{0,120}"', '"msg": "[REDACTED]"', redacted)
            fatal_lines.append(redacted[:200])

    return recap_entries, fatal_lines, injection_detected


def format_output(recap_entries, fatal_lines, injection_detected):
    out = []

    if injection_detected:
        out.append("[SECURITY WARNING] Potential prompt injection detected in Ansible output. Review raw logs manually.")
        out.append("")

    if not recap_entries:
        out.append("No PLAY RECAP found in output.")
        return "\n".join(out), 1

    total_ok = total_changed = total_failed = total_unreachable = 0
    for e in recap_entries:
        total_ok          += e["ok"]
        total_changed     += e["changed"]
        total_failed      += e["failed"]
        total_unreachable += e["unreachable"]

    node_count = len(recap_entries)
    out.append(f"PLAY RECAP — {node_count} host(s)")
    out.append(f"  ok={total_ok}  changed={total_changed}  "
               f"unreachable={total_unreachable}  failed={total_failed}")

    if total_failed > 0 or total_unreachable > 0:
        out.append(f"\n[WARN] {total_failed} task(s) failed, {total_unreachable} host(s) unreachable.")
        for fl in fatal_lines[:5]:  # Show up to 5 fatal lines (redacted)
            out.append(f"  {fl}")

    return "\n".join(out), (1 if (total_failed > 0 or total_unreachable > 0) else 0)


def main():
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r', errors='replace') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)
    else:
        lines = sys.stdin.readlines()

    recap_entries, fatal_lines, injection_detected = parse_recap(lines)
    output, exit_code = format_output(recap_entries, fatal_lines, injection_detected)
    print(output)

    if injection_detected:
        sys.exit(2)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
