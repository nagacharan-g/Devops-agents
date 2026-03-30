# CoE Infrastructure Skills 

---

## 1. What Are "Skills"?

Claude Code (the AI CLI tool) can be extended with **skills** — pre-loaded instruction sets that
give the AI deep, opinionated knowledge about a specific workflow.

Think of a skill like loading a specialist consultant into the AI:

```
Without skill:  Claude knows general Terraform/Ansible concepts
With skill:     Claude knows YOUR project's exact modules, naming conventions,
                security rules, known bugs, and step-by-step workflow
```

You activate a skill with:

```
load coe-infra-deploy-aws skill
load coe-infra-config-aws skill
```

Once loaded, the AI guides you through the entire workflow — asking questions one at a time,
writing files, running commands, and validating output.

---

## 2. The Big Picture

These two skills form a **two-phase pipeline** to go from zero to a fully configured cloud environment:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        YOUR LOCAL MACHINE                               │
│                                                                         │
│  ┌─────────────────────────┐       ┌──────────────────────────────┐    │
│  │   SKILL 1               │       │   SKILL 2                    │    │
│  │   coe-infra-deploy-aws  │──────▶│   coe-infra-config-aws       │    │
│  │                         │       │                              │    │
│  │   TOOL: Terraform        │       │   TOOL: Ansible              │    │
│  │   PURPOSE: Create cloud │       │   PURPOSE: Install software  │    │
│  │   infrastructure        │       │   on the created servers     │    │
│  └────────────┬────────────┘       └──────────────┬───────────────┘    │
│               │                                   │                    │
│               │  handoff.json                     │  outputs-prod.txt  │
│               │  (bridge between skills)          │  handoff-prod.json │
│               ▼                                   ▼                    │
└─────────────────────────────────────────────────────────────────────────┘
                │                                   │
                ▼                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           AWS CLOUD                                      │
│                                                                          │
│   Phase 1 (Deploy): Servers exist, networking set up, databases ready   │
│   Phase 2 (Config): Servers have Docker, Node.js, k3s, Jenkins, etc.   │
└──────────────────────────────────────────────────────────────────────────┘
```

 Skill 1 builds the house. Skill 2 furnishes it.

---

## 3. Skill 1 — coe-infra-deploy-aws (Terraform)

### What it creates

```
                              AWS REGION (e.g. ap-south-1)
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ┌──────────────────── VPC (10.x.0.0/16) ────────────────────┐  │
│  │                                                            │  │
│  │  subnet-1 (AZ-a)      subnet-2 (AZ-b)    subnet-3 (AZ-c) │  │
│  │  ┌──────────┐         ┌──────────┐        ┌──────────┐   │  │
│  │  │ EC2      │         │ EC2      │        │  RDS     │   │  │
│  │  │ Mgmt     │         │ App/k3s  │        │ Postgres │   │  │
│  │  │ t4g.med  │         │ nodes    │        │ (private)│   │  │
│  │  └──────────┘         └──────────┘        └──────────┘   │  │
│  │                                                            │  │
│  │  ┌────────┐  ┌──────────────┐  ┌────────────────────┐    │  │
│  │  │  S3    │  │     ECR      │  │   Lambda (optional) │    │  │
│  │  │ bucket │  │  (prod only) │  │   functions         │    │  │
│  │  └────────┘  └──────────────┘  └────────────────────┘    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

Internet Gateway ──▶ Management Node (public IP, ports 22/10022/80/443)
                     App/k3s Nodes  (VPC-only SSH, public HTTP/HTTPS)
                     RDS            (VPC-only, no public access)
```

### Terraform Module Map

```
AWS/modules/aws/
├── vpc/              Creates VPC + subnets + route tables + internet gateway
├── compute/          Creates EC2 instances + security groups + SSH key pairs
├── database/         Creates RDS instance + subnet group + security group
├── object_storage/   Creates S3 bucket + IAM user + access keys
├── container_registry/ Creates ECR repository
├── lambda/           Creates Lambda functions + IAM roles
├── ebs/              (disabled by default) Block storage volumes
└── alb/              (disabled by default) Load balancer
```

### Workflow — Step by Step

```
┌─────────────────────────────────────────────────────────────────────┐
│                  DEPLOY SKILL WORKFLOW                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  STEP 1-6: Q&A Phase (AI asks you questions one at a time)           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  1. Environment?        → staging / production               │   │
│  │  2. Project name?       → e.g. test-coe-gnc                  │   │
│  │  3. AWS region?         → e.g. ap-south-1                    │   │
│  │  4. Lambda needed?      → yes / no                           │   │
│  │  5. App nodes count/type/disk                                │   │
│  │  6. RDS engine/version/size/password                         │   │
│  │  7. VPC CIDR block                                           │   │
│  │  8. (if Lambda) function names/runtimes/handlers             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                         │                                            │
│                         ▼                                            │
│  STEP 8: Create project folder                                       │
│  projects/<project-name>/                                            │
│  ├── main.tf       (which modules to enable)                        │
│  ├── variables.tf  (variable declarations)                          │
│  ├── outputs.tf    (what to output after apply)                     │
│  ├── provider.tf   (AWS provider config)                            │
│  └── .gitignore    (protects secrets)                               │
│                         │                                            │
│                         ▼                                            │
│  STEP 9: SSH Key Setup (TWO separate keys — see Security section)   │
│  → You paste your management public key                             │
│  → You generate an internal key pair on your machine               │
│                         │                                            │
│                         ▼                                            │
│  STEP 9.5: AWS Credentials                                          │
│  → You open terraform.tfvars in your editor, add keys manually      │
│                         │                                            │
│                         ▼                                            │
│  STEP 10: AI enables right modules in main.tf + outputs.tf          │
│                         │                                            │
│                         ▼                                            │
│  STEP 12: Integrity Check → terraform init                          │
│                         │                                            │
│                         ▼                                            │
│  STEP 13: terraform plan  (saved as tfplan.binary)                  │
│           ↓ sanitized output shown in chat                          │
│           ↓ raw output saved to plan-output.log                     │
│                         │                                            │
│                         ▼                                            │
│  STEP 14: Review → YOU confirm (Apply / Cancel / Modify)            │
│                         │                                            │
│                         ▼                                            │
│  STEP 15: terraform apply tfplan.binary                             │
│           ↓ sanitized output in chat                                │
│           ↓ raw output in apply-output.log                          │
│                         │                                            │
│                         ▼                                            │
│  STEP 16: Generate handoff.json + outputs.txt                       │
│           (bridge to config skill)                                  │
│                         │                                            │
│                         ▼                                            │
│  STEP 17: .complete marker created                                  │
│           Offer destroy plan                                        │
└─────────────────────────────────────────────────────────────────────┘
```

### Files Created

```
projects/<project-name>/
├── main.tf              ← Which Terraform modules are active
├── variables.tf         ← Variable type definitions
├── outputs.tf           ← Output values to extract after apply
├── provider.tf          ← AWS provider + region + credentials
├── terraform.tfvars     ← YOUR values (IPs, passwords, keys) ⚠️ gitignored
├── .terraform/          ← Downloaded provider plugins
├── terraform.tfstate    ← Live infrastructure state ⚠️ gitignored
├── tfplan.binary        ← Saved plan file
├── plan-output.log      ← Raw terraform plan output ⚠️ sensitive
├── apply-output.log     ← Raw terraform apply output ⚠️ sensitive
├── outputs.txt          ← All terraform outputs (IPs, keys) ⚠️ sensitive
├── handoff.json         ← Structured data for config skill ⚠️ sensitive
└── .complete            ← Marker: deployment finished
```

### Staging vs Production Differences

| Feature          | Staging                       | Production                       |
| ---------------- | ----------------------------- | -------------------------------- |
| ECR repository   | Not created                   | Created                          |
| RDS Multi-AZ     | Always No                     | You choose                       |
| Node naming      | `<proj>-app-node-N-staging` | `<proj>-k3s-node-N-production` |
| k3s node support | No                            | Yes                              |
| Cost             | Lower                         | Higher                           |

---

## 4. Skill 2 — coe-infra-config-aws (Ansible)

### What it installs on each node type

```
┌─────────────────────────────────────────────────────────────────────┐
│  MANAGEMENT NODE                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Docker · Node.js · Git · Helm · Jenkins · Redis              │  │
│  │  PostgreSQL client · AWS CLI · zip · swap                     │  │
│  │  Custom users + SSH aliases for all app nodes (jump host)     │  │
│  │  Cronjobs: ECR token refresh · cache cleanup                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  K3S MASTER NODE                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  k3s server (Kubernetes distribution)                         │  │
│  │  kubeconfig copied to management node                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  K3S WORKER NODES                                                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  k3s agent (joins master via token)                           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  STANDARD APP NODES                                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Docker · Node.js · Git · custom users                        │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Ansible Role Map

```
roles/setup/
├── set_hostname/            Sets server hostname
├── swap/                    Configures swap space
├── docker/                  Installs Docker CE
├── nodejs/                  Installs Node.js (via nvm)
├── git/                     Installs Git
├── helm/                    Installs Helm (k8s package manager)
├── jenkins/                 Installs Jenkins CI/CD
├── redis/                   Installs + configures Redis
├── psql-client/             Installs PostgreSQL client tools
├── awscli/                  Installs AWS CLI + ECR login cronjob
├── zip/                     Installs zip/unzip
├── management_node_users/   Creates users + SSH aliases (mgmt node)
├── std_node_users/          Creates users on standard nodes
├── std_node_users_docker_permission/ Adds users to docker group
├── jump_access/             Sets up SSH proxy from mgmt → app nodes
├── cronjobs/                Schedules recurring tasks
└── k3s/
    ├── master/setup/        Installs k3s server
    └── worker/setup/        Installs k3s agent + joins cluster
```

### Workflow — Step by Step

```
┌─────────────────────────────────────────────────────────────────────┐
│                  CONFIG SKILL WORKFLOW                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  STEP 1: Environment (staging / production)                          │
│          Pre-flight: check Ansible, check state, fix key paths       │
│                         │                                            │
│                         ▼                                            │
│  STEP 2: Gather node info                                           │
│          → Auto: parse handoff.json from deploy skill               │
│          → Manual: enter IPs + aliases one by one                   │
│                         │                                            │
│                         ▼                                            │
│  STEP 3: Configure inventories/<env>/hosts.yml                      │
│          → Set management IP/port                                   │
│          → Uncomment k3s_cluster section (if needed)               │
│          → Uncomment std_nodes section (if needed)                  │
│          → Validate with validate-inventory.py                      │
│                         │                                            │
│                         ▼                                            │
│  STEP 4: Configure variables (one question at a time)               │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  group_vars/all/editable.yml     → nodejs_version            │   │
│  │  host_vars/management/editable.yml → postgresql_version,     │   │
│  │                                      redis_password/port,    │   │
│  │                                      ECR URL, AWS region,    │   │
│  │                                      k3s namespace,          │   │
│  │                                      AWS credentials         │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                         │                                            │
│                         ▼                                            │
│  STEP 5: SSH Key Setup                                              │
│          bash scripts/setup-ssh-keys.sh <env> <mgmt-key> <int-key>  │
│          Test: ansible ping management node                          │
│                         │                                            │
│                         ▼                                            │
│  STEP 6: Review & Confirm                                           │
│                         │                                            │
│                         ▼                                            │
│  STEP 7: Run Playbooks (MUST be in this order)                      │
│                                                                      │
│   7a ──▶ setup-management.yml         (always first — jump host)    │
│   7b ──▶ setup-k3s-master.yml         (if k3s)                     │
│   7c ──▶ setup-k3s-worker.yml         (if k3s, after 7b)           │
│   7d ──▶ setup-std-node.yml           (if std nodes)               │
│   7e ──▶ setup-management-k3s-access.yml  (if k3s, after 7a+7b)   │
│                         │                                            │
│                         ▼                                            │
│  STEP 8: Verify + Generate outputs-<env>.txt + handoff-<env>.json   │
│          .config-complete-<env> marker created                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Playbook Execution Order — Why It Matters

```
setup-management.yml
      │
      │  Management node becomes the JUMP HOST
      │  (SSH proxy to all internal nodes)
      │
      ▼
setup-k3s-master.yml
      │
      │  Master generates a JOIN TOKEN
      │  Token is saved locally for worker to use
      │
      ▼
setup-k3s-worker.yml          setup-std-node.yml
      │                               │
      │  Worker reads token           │  Independent of k3s
      │  and joins cluster            │
      ▼                               ▼
setup-management-k3s-access.yml
      │
      │  Copies kubeconfig from master → management node
      │  Tests: kubectl get nodes (needs port 6443 open)
      ▼
      DONE
```

---

## 5. SSH Architecture — The Two-Key Model

This is critical to understand. The deploy skill enforces **strict key separation**:

```
╔══════════════════════════════════════════════════════════════════════╗
║                     SSH ACCESS ARCHITECTURE                          ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  YOUR LAPTOP                                                         ║
║  ┌──────────────────────────────────┐                               ║
║  │  ~/.ssh/test-coe-charan          │  ← mgmt.pem (YOUR key)        ║
║  │  ~/.ssh/test-coe-gnc-internal-*  │  ← internal.pem (generated)   ║
║  └──────────────────────────────────┘                               ║
║         │                    │                                       ║
║         │ mgmt key           │ (never used directly from laptop)     ║
║         ▼                    │                                       ║
║  ┌──────────────────┐        │                                       ║
║  │  MANAGEMENT NODE │        │                                       ║
║  │  (public IP)     │        │                                       ║
║  │  port 10022      │        │                                       ║
║  └────────┬─────────┘        │                                       ║
║           │                  │                                       ║
║           │ internal key ◀───┘ (copied here by config skill)        ║
║           │ (VPC-internal only)                                      ║
║           ▼                                                          ║
║  ┌────────────────────────────────────────────────────────────────┐ ║
║  │  PRIVATE NODES (k3s-node-1, k3s-node-2, app-node-3)           │ ║
║  │  No public SSH access — reachable ONLY via management node     │ ║
║  └────────────────────────────────────────────────────────────────┘ ║
║                                                                      ║
║  Why two keys?                                                       ║
║  • Mgmt key compromise → only management node at risk               ║
║  • Internal key never leaves the management node after setup        ║
║  • App nodes have zero direct internet exposure                     ║
╚══════════════════════════════════════════════════════════════════════╝
```

### SSH Port Change (Important!)

The compute module's `user_data` script changes SSH from **port 22 → port 10022** on boot.
This is why ALL security groups must have **both** ports open:

```
Port 22    → Initial connection before user_data runs
Port 10022 → All connections after first boot
```

---

## 6. The Handoff.json Bridge

`handoff.json` is the **data contract** between the two skills:

```
DEPLOY SKILL produces:                  CONFIG SKILL consumes:
┌─────────────────────────────┐         ┌──────────────────────────────┐
│ handoff.json                │         │ parse-handoff-for-config.py  │
│ ─────────────────────────── │  ──────▶│ (secure parser)              │
│ ec2_instances:              │         │ extracts:                    │
│   mgmt-node: {IP, type}     │         │  • node IPs → hosts.yml      │
│   k3s-node-1: {IP, type}    │         │  • SSH key paths → Step 5    │
│   k3s-node-2: {IP, type}    │         │  • project/env metadata      │
│   app-node-3: {IP, type}    │         └──────────────────────────────┘
│ ssh_key_paths:              │
│   mgmt_private_key_path     │         NEVER read directly with cat/Read
│   internal_private_key_path │         Always use parse-handoff-for-config.py
│ vpc_id, subnet_ids          │         (injection protection)
│ s3 keys, ECR URLs, RDS IDs  │
└─────────────────────────────┘
```

---

## 7. Security Model

### Layered Defences

```
Layer 1 — Input Validation
  • All project names validated: ^[a-z0-9][a-z0-9-]{2,29}$
  • All IPs validated: ^(\d{1,3}\.){3}\d{1,3}$ + octet range 0-255
  • Shell metacharacters rejected in all user inputs
  • Separate validators for inventory, handoff.json, project names

Layer 2 — Output Sanitization
  • sanitize-tf-output.py  → strips IPs/ARNs/credentials from Terraform output
  • sanitize-ansible-output.py → strips hostnames from Ansible PLAY RECAP
  • generate-handoff.py → prints only non-sensitive fields to chat

Layer 3 — File Integrity
  • verify-integrity.sh checks SHA256 hashes of all scripts + modules
  • Must pass before every terraform init/plan/apply
  • generate-checksums.sh regenerates after authorized changes

Layer 4 — Credential Isolation
  • AWS credentials: user types in their own editor, never in chat
  • SSH private keys: user generates with ! prefix (runs locally)
  • State files: gitignored, never committed
  • outputs.txt / handoff.json: gitignored, contain live secrets

Layer 5 — Injection Detection
  • All parsers detect: "ignore previous instructions", "system:", etc.
  • Exit code 2 on detection → workflow stops
  • Covers: tfvars, handoff.json, Terraform output, Ansible output
```

### What Goes Where

```
SAFE to show in chat:        NEVER shown in chat:
─────────────────────        ────────────────────────────────────
Resource counts              IP addresses
Module names                 AWS credentials (access/secret keys)
File paths                   SSH private key content
Task counts (ok/changed)     RDS passwords
Playbook names               S3 secret access keys
Node roles                   ECR URLs with account IDs
                             Instance IDs, SG IDs, VPC IDs
                             outputs.txt content
                             terraform.tfstate content
```

---

## 8. Staging vs Production — Config Skill

| Aspect                      | Staging                             | Production              |
| --------------------------- | ----------------------------------- | ----------------------- |
| Inventory path              | `inventories/staging/`            | `inventories/prod/`   |
| SSH keys                    | `keys/staging/`                   | `keys/prod/`          |
| Key paths in uneditable.yml | `keys/staging/`                   | `keys/prod/`          |
| Playbooks                   | Copies with `-staging.yml` suffix | Default playbooks       |
| State markers               | `.mgmt-complete-staging`          | `.mgmt-complete-prod` |
| ECR config                  | Optional (skip if no ECR)           | Required                |
| k3s support                 | Not typical                         | Yes                     |

**Note for freshers:** When you copy staging inventory from prod, the skill auto-fixes
all hardcoded `keys/prod/` paths to `keys/staging/` (Step 1d).

---

## 9. Trade-offs

### Deploy Skill (Terraform)

| Trade-off                              | Description                                                                                                                                        |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Local state**                  | `terraform.tfstate` lives on your machine. If lost, you lose track of what Terraform manages. Use remote state (S3 backend) for teams.           |
| **No drift detection on resume** | Resuming from PLANNED state uses a saved plan. If AWS resources changed since the plan, the apply may conflict. The skill warns about stale plans. |
| **Lambda requires local zips**   | `filebase64sha256()` reads the zip at plan time. Zips must exist locally before planning. CI/CD workflows need to build them first.              |
| **Single-region**                | One region per project. Multi-region requires separate projects.                                                                                   |
| **Hardcoded ARM64 AMI**          | Compute module uses ARM64 AMI — only `t4g` family instances work. Using `t3`/`m5`/`c5` will fail to boot silently.                        |
| **Credentials in tfvars**        | Simpler than IAM roles but less secure than instance profiles. Rotate keys after deployment.                                                       |

### Config Skill (Ansible)

| Trade-off                             | Description                                                                                                                                            |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Playbook order is mandatory** | Management must run first (it's the jump host). k3s master before worker (join token dependency). Wrong order = connection failures.                   |
| **Idempotency not guaranteed**  | Most roles are idempotent (safe to re-run), but some (k3s install, Jenkins GPG) may behave differently on re-run.                                      |
| **Ansible version sensitivity** | `warn: false` removed in Ansible 2.14+. Other deprecations may appear in future versions. Pin Ansible version in CI.                                 |
| **uneditable.yml files**        | Jump access and SSH key paths are in `uneditable.yml`. Changing them requires understanding the role internals. Wrongly edited = SSH lockout.        |
| **Port 6443 cross-skill gap**   | k3s access requires port 6443 open in the k3s master SG — but the deploy skill doesn't know this. Must be added manually to tfvars and re-applied.    |
| **Jenkins GPG key expiry**      | Jenkins repo key may expire. When it does, the Jenkins role fails. Workaround: dearmor the key manually.                                               |
| **No rollback**                 | Ansible doesn't have a rollback mechanism. If a role fails mid-way, the node may be in a partial state. Re-running is usually safe but not guaranteed. |

### Both Skills

| Trade-off                          | Description                                                                                                          |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Sequential questions**     | The AI asks one question at a time — intentional (anti-injection) but slower than a config file.                    |
| **No parallel environments** | Skills maintain one active session. Don't run staging and production simultaneously in the same Claude Code session. |
| **Handoff.json coupling**    | Skills are designed to chain via handoff.json. Using them independently requires manual IP entry.                    |
| **Context window**           | Very long sessions (many playbooks) may approach context limits. The skill's session resume covers this.             |

---

## 10. Session Resume

Both skills support **resuming interrupted sessions**:

```
DEPLOY SKILL states:
INIT → VALIDATED → CONFIGURED → INITIALIZED → PLANNED → APPLIED → FINALIZED → COMPLETE

CONFIG SKILL states:
UNCONFIGURED → INVENTORIED → CONFIGURED → KEYS_READY → MGMT_DONE → STD_DONE → K3S_DONE → COMPLETE
```

When you load a skill, it automatically detects where you left off and resumes from that point.
**You never need to start from scratch** after a crash or disconnection.

---

## 11. Quick Reference

### Deploy Skill Commands (internal)

```bash
# Integrity check (mandatory before init)
bash scripts/verify-integrity.sh

# Terraform init
bash scripts/tf-init.sh projects/<project-name>

# Plan (saves plan file)
cd projects/<project-name> && terraform plan -out=tfplan.binary \
  > plan-output.log 2>&1

# Apply (from saved plan)
cd projects/<project-name> && terraform apply tfplan.binary \
  > apply-output.log 2>&1

# Sanitize output for chat
python3 scripts/sanitize-tf-output.py < plan-output.log

# Generate handoff
python3 scripts/generate-handoff.py projects/<project-name>
```

### Config Skill Commands (internal)

```bash
# SSH key setup
bash scripts/setup-ssh-keys.sh <env> ~/.ssh/<mgmt-key> ~/.ssh/<internal-key>

# Test connectivity
cd infra-configuration/AWS && \
  ansible -i inventories/<env>/hosts.yml management -m ping \
  --private-key keys/<env>/mgmt.pem

# Run a playbook
cd infra-configuration/AWS && \
  ansible-playbook -i inventories/<env>/hosts.yml setup-management.yml \
  2>&1 | tee /tmp/mgmt.log | python3 ../../scripts/sanitize-ansible-output.py

# Validate inventory
python3 scripts/validate-inventory.py infra-configuration/AWS/inventories/<env>/hosts.yml

# Parse handoff securely
python3 scripts/parse-handoff-for-config.py projects/<project>/handoff.json
```

### Checklist Before Starting

```
Deploy Skill:
  □ AWS credentials ready (access key + secret key)
  □ SSH key pair exists on your machine (~/.ssh/your-key)
  □ AWS region decided
  □ Instance types chosen (t4g family only)
  □ RDS password prepared (16+ chars, alphanumeric only)
  □ Lambda zip files ready IF using Lambda

Config Skill:
  □ Deploy skill completed (.complete marker exists)
  □ handoff.json exists in projects/<name>/
  □ Internal key pair generated (~/.ssh/<project>-internal-<env>)
  □ AWS credentials ready for Ansible (for ECR access)
  □ Redis password decided
  □ k3s namespace name decided
```

---

## 12. Common Errors & Fixes

| Error                                   | Cause                                                  | Fix                                                                   |
| --------------------------------------- | ------------------------------------------------------ | --------------------------------------------------------------------- |
| `filebase64sha256: open lambda/*.zip` | Lambda zip doesn't exist at plan time                  | Comment out Lambda module, deploy rest first                          |
| `Cannot apply incomplete plan`        | Plan had errors, binary is incomplete                  | Delete tfplan.binary, fix errors, re-plan                             |
| `Unsupported parameters: warn`        | Ansible 2.14+ removed `warn:` from command module    | Remove `warn: false` from role task                                 |
| `dial tcp x.x.x.x:6443: i/o timeout`  | Port 6443 not in k3s master security group             | Add port 6443 ingress to tfvars, re-apply                             |
| `Permission denied (publickey)`       | Wrong key for the node                                 | Check key_name in tfvars matches the node                             |
| SSH works on 22, fails on 10022         | user_data hasn't run yet OR port 10022 missing from SG | Wait for boot to complete; verify SG has port 10022                   |
| `variable not declared` in Terraform  | Using wrong credential variable names                  | Must use `aws_access_key` / `aws_secret_key` (not `_id` suffix) |
| Duplicate security group names          | Two compute entries share same `security_group_name` | Each node must have a unique `security_group_name`                  |
