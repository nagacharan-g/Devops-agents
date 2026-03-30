#!/bin/bash
# AWS Credentials Setup Script
# This script securely prompts for credentials and writes to terraform.tfvars

set -euo pipefail

TFVARS_FILE="$1"

if [ -z "$TFVARS_FILE" ]; then
  echo "Usage: $0 <path-to-terraform.tfvars>"
  exit 1
fi

if [ ! -f "$TFVARS_FILE" ]; then
  echo "ERROR: terraform.tfvars not found: $TFVARS_FILE"
  echo "Suggestions:"
  echo "  - Ensure terraform.tfvars was created first"
  echo "  - Check the file path"
  exit 1
fi

echo "=== AWS Credentials Setup ==="
echo "This script will prompt for your AWS credentials."
echo "Credentials will be written to: $TFVARS_FILE"
echo ""

# Prompt for AWS Access Key ID
read -p "AWS Access Key ID: " aws_access_key
if [ -z "$aws_access_key" ]; then
  echo "ERROR: AWS Access Key ID cannot be empty"
  exit 1
fi

# Prompt for AWS Secret Access Key (hidden input)
read -s -p "AWS Secret Access Key: " aws_secret_key
echo ""
if [ -z "$aws_secret_key" ]; then
  echo "ERROR: AWS Secret Access Key cannot be empty"
  exit 1
fi

# Append credentials to terraform.tfvars
cat >> "$TFVARS_FILE" << EOF

# AWS Credentials (added by setup-credentials.sh)
aws_access_key_id     = "$aws_access_key"
aws_secret_access_key = "$aws_secret_key"
EOF

echo ""
echo "✓ Credentials written to $TFVARS_FILE"
echo "⚠️  This file is in .gitignore and will not be committed"
echo ""
