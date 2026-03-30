#!/bin/bash
# Check Ansible Configuration State
# Usage: bash scripts/check-config-state.sh <env> <infra-config-dir>
# Example: bash scripts/check-config-state.sh staging infra-configuration/AWS
#
# States (linear progression):
#   UNCONFIGURED  → no inventory edits (hosts.yml has default IPs)
#   INVENTORIED   → hosts.yml has been edited with real IPs
#   CONFIGURED    → editable.yml files have been customized
#   KEYS_READY    → keys/<env>/*.pem exist and are valid
#   MGMT_DONE     → management playbook completed (.mgmt-complete-<env> marker)
#   STD_DONE      → std_nodes playbook completed (.std-complete-<env> marker)
#   K3S_DONE      → k3s playbooks completed (.k3s-complete-<env> marker)
#   COMPLETE      → outputs + handoff exist (.config-complete-<env> marker)

set -euo pipefail

if [ $# -ne 2 ]; then
    echo "Usage: bash scripts/check-config-state.sh <env> <infra-config-dir>"
    exit 1
fi

ENV="$1"
DIR="$2"

if [[ ! "$ENV" =~ ^(staging|prod)$ ]]; then
    echo "ERROR: Environment must be 'staging' or 'prod'"
    exit 1
fi

if [ ! -d "$DIR" ]; then
    echo "ERROR: Directory not found: $DIR"
    exit 1
fi

# Check states in reverse order (most advanced first)
if [ -f "$DIR/.config-complete-$ENV" ]; then
    echo "Current State: COMPLETE"
    echo "Environment: $ENV"
    echo "All configuration is done."
    exit 0
fi

if [ -f "$DIR/.k3s-complete-$ENV" ]; then
    echo "Current State: K3S_DONE"
    echo "Environment: $ENV"
    echo "Resume at: Step 8 (Verify & Generate Outputs)"
    exit 0
fi

if [ -f "$DIR/.std-complete-$ENV" ]; then
    echo "Current State: STD_DONE"
    echo "Environment: $ENV"
    echo "Resume at: Step 7e (k3s access) or Step 8 (if no k3s)"
    exit 0
fi

if [ -f "$DIR/.mgmt-complete-$ENV" ]; then
    echo "Current State: MGMT_DONE"
    echo "Environment: $ENV"
    echo "Resume at: Step 7b (k3s) or Step 7d (std nodes)"
    exit 0
fi

# Check keys
KEYS_VALID=true
if [ -f "$DIR/keys/$ENV/mgmt.pem" ] && [ -f "$DIR/keys/$ENV/internal.pem" ]; then
    ssh-keygen -l -f "$DIR/keys/$ENV/mgmt.pem" > /dev/null 2>&1 || KEYS_VALID=false
    ssh-keygen -l -f "$DIR/keys/$ENV/internal.pem" > /dev/null 2>&1 || KEYS_VALID=false
    if [ "$KEYS_VALID" = true ]; then
        echo "Current State: KEYS_READY"
        echo "Environment: $ENV"
        echo "Resume at: Step 5d (Test connectivity) or Step 6 (Review)"
        exit 0
    fi
fi

# Check if editable.yml has been customized (not default values)
EDITABLE="$DIR/inventories/$ENV/host_vars/management/editable.yml"
if [ -f "$EDITABLE" ]; then
    # Check if AWS credentials are set (not defaults)
    if grep -q "YOUR_AWS_ACCESS_KEY_ID\|YOUR_AWS_SECRET_ACCESS_KEY" "$EDITABLE" 2>/dev/null; then
        # Still has defaults — check if other values were changed
        :
    else
        AWS_COUNT=$(grep -c "aws_access_key_id\|aws_secret_access_key" "$EDITABLE" 2>/dev/null || echo 0)
        if [ "$AWS_COUNT" -ge 2 ]; then
            echo "Current State: CONFIGURED"
            echo "Environment: $ENV"
            echo "Resume at: Step 5 (SSH Key Setup)"
            exit 0
        fi
    fi
fi

# Check if inventory has been edited
HOSTS="$DIR/inventories/$ENV/hosts.yml"
if [ -f "$HOSTS" ]; then
    # Check if management IP is not the default
    DEFAULT_IP=$(grep "ansible_host:" "$HOSTS" 2>/dev/null | head -1 | awk '{print $2}')
    if [ -n "$DEFAULT_IP" ] && [ "$DEFAULT_IP" != "13.201.76.158" ]; then
        echo "Current State: INVENTORIED"
        echo "Environment: $ENV"
        echo "Resume at: Step 4 (Configure Variables)"
        exit 0
    fi
fi

echo "Current State: UNCONFIGURED"
echo "Environment: $ENV"
echo "Resume at: Step 1 (fresh start)"
exit 0
