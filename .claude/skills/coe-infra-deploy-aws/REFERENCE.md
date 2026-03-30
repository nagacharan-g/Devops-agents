# CoE Infrastructure Deployment - Reference Data

## Validation Rules

### Environment
- Valid values: "Staging" or "Production" (case-insensitive)
- Regex: `^(staging|production)$/i`

### Project Name
- Lowercase alphanumeric + hyphens only
- Must start with letter
- Length: 3-30 characters
- Regex: `^[a-z][a-z0-9-]{2,29}$`
- Examples: `coe-api`, `payment-service`, `user-mgmt`

### AWS Region
- Valid region codes only
- Common regions: `ap-south-1`, `us-east-1`, `us-west-2`, `eu-west-1`, `eu-central-1`
- Full list: ap-south-1, ap-northeast-1, ap-southeast-1, us-east-1, us-east-2, us-west-1, us-west-2, eu-west-1, eu-west-2, eu-central-1

### Lambda Required
- Valid values: "Yes" or "No" (case-insensitive)
- Regex: `^(yes|no)$/i`

### App Node Count
- Integer between 1 and 10
- Regex: `^([1-9]|10)$`

### EC2 Instance Types
<!-- FIX #2: Compute module (AWS/modules/aws/compute/main.tf) fetches ARM64 Ubuntu AMI only. x86_64 types (t3, m5, c5) will fail to boot due to architecture mismatch. Restricting to t4g (ARM64) only. -->
<!-- Old valid types (x86_64 - incompatible with ARM64 AMI): -->
<!-- - Valid types: t3.micro, t3.small, t3.medium, t3.large, t3.xlarge, t3.2xlarge -->
<!-- - Valid types: m5.large, m5.xlarge, m5.2xlarge, m5.4xlarge -->
<!-- - Valid types: c5.large, c5.xlarge, c5.2xlarge, c5.4xlarge -->
- Valid types (ARM64 only): t4g.micro, t4g.small, t4g.medium, t4g.large, t4g.xlarge, t4g.2xlarge
- Regex: `^t4g\.(micro|small|medium|large|xlarge|2xlarge)$`

### Root Disk Size
- Valid values: 30, 50, 100, 200 (GB)
- Regex: `^(30|50|100|200)$`

### Database Engine
- Valid values: "Postgres" or "MySQL" (case-insensitive)
- Regex: `^(postgres|mysql)$/i`

### Database Version
- Postgres: 15, 16, 17 (recommend 17)
- MySQL: 8.0, 8.4 (recommend 8.4)
- Regex: `^(15|16|17|8\.0|8\.4)$`

### Database Instance Class
- Valid classes: db.t3.micro, db.t3.small, db.t3.medium, db.t3.large
- Valid classes: db.t4g.micro, db.t4g.small, db.t4g.medium, db.t4g.large
- Regex: `^db\.(t3|t4g)\.(micro|small|medium|large)$`

### Database Storage
- Valid values: 20, 50, 100, 200 (GB)
- Regex: `^(20|50|100|200)$`

### Database Password
- Minimum 16 characters
- Alphanumeric only (uppercase, lowercase, numbers)
- NO special characters (@, $, #, !, etc.) — they cause connection issues in some clients and require escaping in tfvars
- Regex: `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{16,}$`

<!-- FIX #15: Previously required special characters, but Step 4 in SKILL.md said to avoid them. RDS master passwords with special chars cause issues with psql connection strings and some ORMs. Aligned to alphanumeric-only. -->

### Multi-AZ
- Valid values: "Yes" or "No" (case-insensitive)
- Production only
- Regex: `^(yes|no)$/i`

### VPC CIDR Block
- Valid CIDR notation (RFC 1918 private ranges recommended)
- Common options: 10.0.0.0/16, 172.16.0.0/16, 192.168.0.0/16
- Default: 10.0.0.0/16
- Regex: `^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$`
- Must be large enough for 3 subnets

### Lambda Runtime
- Valid runtimes: python3.10, python3.11, python3.12, nodejs18.x, nodejs20.x
- Regex: `^(python3\.(10|11|12)|nodejs(18|20)\.x)$`

### Lambda Handler
- Format: `filename.function_name`
- Examples: `app.handler`, `index.handler`, `main.lambda_handler`
- Regex: `^[a-zA-Z0-9_-]+\.[a-zA-Z0-9_]+$`

## Naming Conventions

All resources follow pattern: `<project>-<type>-<env>`

### Management Node
- Pattern: `<project>-mgmt-node-<env>`
- Example: `coe-api-mgmt-node-staging`

### App Nodes (Staging)
- Pattern: `<project>-app-node-<number>-<env>`
- Example: `coe-api-app-node-1-staging`

### K3s Nodes (Production)
- Pattern: `<project>-k3s-node-<number>-<env>`
- Example: `coe-api-k3s-node-1-production`

### App Nodes (Production, non-k3s)
- Pattern: `<project>-app-node-<number>-<env>`
- Example: `coe-api-app-node-3-production`

### RDS Database
- Pattern: `<project>-db-<env>`
- Example: `coe-api-db-production`
- Default DB name: `<project>db` (remove hyphens)

### VPC
- Pattern: `<project>-vpc-<env>`
- Example: `coe-api-vpc-staging`

### S3 Bucket
- Pattern: `<project>-storage-<env>`
- Example: `coe-api-storage-production`

### ECR Repository
- Pattern: `<project>-ecr-<env>`
- Example: `coe-api-ecr-production`
- Production only

### Lambda Functions
- Pattern: `<project>-<function-name>-<env>`
- Example: `coe-api-user-service-staging`

## Auto-Configured Resources

### Management Node (Always Fixed)
- Instance Type: `t4g.medium`
- vCPU: 2
- Memory: 4 GB
- Root Disk: 30 GB gp3 (encrypted)
- Security Groups: SSH (22), SSH-custom (10022), HTTP (80), HTTPS (443)
- **CRITICAL:** Port 10022 MUST be included — the compute module's user_data changes SSH to 10022 and reboots. Without it, the node is unreachable after first boot. `<!-- FIX #12 -->`

### Security Group Naming (CRITICAL)
- Each compute node MUST have a **unique** `security_group_name`
- Pattern: `<project>-<role>-sg-<N>-<env>` (e.g., `myapp-app-sg-1-staging`)
- Management: `<project>-mgmt-sg-<env>` (always unique, only one mgmt node)
- The compute module creates one AWS SG per `security_group_name`. Duplicate names cause `InvalidGroup.Duplicate` errors and **partial apply failures** that are masked by the sanitizer `<!-- FIX #9 -->`

### VPC Configuration
- CIDR Block: User-configurable (default: `10.0.0.0/16`)
- Subnet 1 (EC2): First /24 subnet from CIDR
- Subnet 2 (RDS): Second /24 subnet from CIDR
- Subnet 3 (RDS): Third /24 subnet from CIDR

### RDS Configuration (Auto)
- Encrypted: `true`
- Publicly Accessible: `false`
- Security Group: Allow from VPC CIDR only
- Default Username: `dbadmin`
- Backup Retention: 7 days (production), 1 day (staging)

## Infrastructure Patterns

### Staging/Non-Production Pattern
Required resources:
1. 1 Management Node (t4g.medium)
2. x App Nodes (user-defined count/type)
3. 1 RDS Database (t-class)
4. 1 S3 Bucket
5. Optional: Lambda functions

### Production Pattern
Required resources:
1. 1 Management Node (t4g.medium)
2. x App Nodes (mix of k3s and regular)
3. 1 RDS Database (t-class, Multi-AZ option)
4. 1 S3 Bucket
5. 1 ECR Repository
6. Optional: Lambda functions

## Handoff File Schema (C6, C7, C13)

**Location:** `projects/<project-name>/handoff.json` (in .gitignore)

**Schema note:** `generate-handoff.py` dumps raw `terraform output -json` as flat key-value pairs (not a nested structure). The actual handoff.json content depends on which outputs are uncommented in `outputs.tf`. Ensure Step 10 uncomments all required outputs (VPC, EC2, RDS, S3, and conditionally ECR) so the handoff contains the fields `validate-handoff.py` expects: `vpc_id`, `subnet_ids`, `security_group_id`, and conditionally `db_endpoint`, `db_name`, `lambda_function_name`, `lambda_role_arn`.

**Inter-Agent Contract:** Terraform→Ansible handoff. Scope: Infrastructure only (IPs, nodes). Excludes database/S3. Security: No sensitive data. Validation: `validate-handoff.py`. Downstream: Ansible generates inventory via coe-infra-config-aws skill.

## State Machine (C12)

**Linear Progression:** INIT → VALIDATED → CONFIGURED → INITIALIZED → PLANNED → APPLIED → FINALIZED → COMPLETE

**State Indicators:**
- INIT: `projects/<name>/` exists
- VALIDATED: `main.tf`, `provider.tf` exist
- CONFIGURED: `terraform.tfvars` exists
- INITIALIZED: `.terraform/` exists
- PLANNED: `tfplan.binary` exists
- APPLIED: `terraform.tfstate` exists (non-empty)
- FINALIZED: `outputs.txt` and `handoff.json` exist
- COMPLETE: `.complete` marker

**Transitions:** Each state→next only. Scripts check prerequisites. Use `bash scripts/check-state.sh projects/<name>` to detect current state.

**Known limitation:** `check-state.sh` uses `-s terraform.tfstate` (non-empty file) to detect APPLIED state. After `terraform destroy`, the state file still exists with `{"resources": []}` — non-empty but no resources. The script will report APPLIED for a destroyed project. Workaround: check `terraform.tfstate` content for empty `"resources": []` to distinguish destroyed from active.

## Future Enhancements

### Remote Backend (C8 - DEFERRED)
**Status**: Not in v1.0. Uses local state (terraform.tfstate).
**Limitation**: Not for production team collaboration.
**Why**: Bootstrap complexity, S3+DynamoDB prerequisite.
**Workaround**: Backup state regularly, don't commit (.gitignore protects).

**Production Migration**: Create S3 bucket + DynamoDB table, add backend.tf with S3 config (bucket, key, region, dynamodb_table, encrypt=true), run `terraform init -migrate-state`.
