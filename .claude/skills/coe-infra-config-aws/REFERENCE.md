# CoE Infrastructure Configuration - Reference Data

## Validation Rules

### IP Address
- IPv4 format only
- Regex: `^(\d{1,3}\.){3}\d{1,3}$`
- Each octet: 0-255
- Management node: Must be a public IP (reachable from control machine)
- Internal nodes: Must be private IPs (10.x.x.x, 172.16-31.x.x, 192.168.x.x)

### SSH Port
- Default: 10022
- Valid range: 1-65535
- Regex: `^([1-9]\d{0,3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$`

### Hostname
- Lowercase alphanumeric + hyphens only
- Must start with letter
- Length: 1-63 characters
- Regex: `^[a-z][a-z0-9-]{0,62}$`
- Examples: `k3s-master`, `web-admin`, `strapi`, `monitoring`

### Node Alias
- Lowercase alphanumeric + hyphens only
- Must start with letter
- Length: 1-30 characters
- Regex: `^[a-z][a-z0-9-]{0,29}$`
- Examples: `web`, `admin`, `strapi`, `k3s-master`, `k3s-worker-1`
- Aliases create: SSH aliases on management node, non-root users on standard nodes

### Node.js Version
- Valid values: "18", "20", "22" (LTS versions)
- Default: "22"
- Regex: `^(18|20|22)$`

### PostgreSQL Client Version
- Valid values: 15, 16, 17
- Default: 17
- Regex: `^(15|16|17)$`

### Redis Password
- Minimum 8 characters
- Recommended: alphanumeric + special characters
- No spaces
- Regex: `^[^\s]{8,}$`

### Redis Port
- Default: 6379
- Valid range: 1024-65535
- Regex: `^(102[4-9]|10[3-9]\d|1[1-9]\d{2}|[2-9]\d{3}|[1-5]\d{4}|6[0-4]\d{3}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$`

### AWS Region
- Valid region codes only
- Common regions: `ap-south-1`, `us-east-1`, `us-west-2`, `eu-west-1`, `eu-central-1`
- Full list: ap-south-1, ap-northeast-1, ap-southeast-1, us-east-1, us-east-2, us-west-1, us-west-2, eu-west-1, eu-west-2, eu-central-1

### AWS ECR Registry URL
- Format: `<account-id>.dkr.ecr.<region>.amazonaws.com`
- Regex: `^\d{12}\.dkr\.ecr\.[a-z]{2}-[a-z]+-\d\.amazonaws\.com$`
- Example: `123456789012.dkr.ecr.ap-south-1.amazonaws.com`

### k3s Namespace
- Kubernetes namespace naming rules
- Lowercase alphanumeric + hyphens
- Must start and end with alphanumeric
- Regex: `^[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$`
- Default: `default`

### k3s Version
- Stored in `k3s_cluster/uneditable.yml`
- Current default: `v1.30.8+k3s1`
- Format: `v<major>.<minor>.<patch>+k3s<build>`
- DO NOT change unless explicitly requested

## Node Types

### Management Node
**Host group:** `management`
**Access:** Public IP, direct SSH with `mgmt.pem`
**Roles applied (in order):**
1. `set_hostname` — Sets hostname to `management-node`
2. `swap` — Configures swap space
3. `nodejs` — Installs Node.js (version from `editable.yml`), yarn, pm2
4. `git` — Installs Git
5. `docker` — Installs Docker + docker-compose, configures daemon
6. `jenkins` — Installs and starts Jenkins CI server
7. `management_node_users` — Creates `custom_users` list, adds to docker group, adds jenkins to docker group
8. `redis` — Installs Redis with password from `editable.yml`
9. `psql-client` — Installs PostgreSQL client (version from `editable.yml`)
10. `jump_access` — Creates `management-user`, copies `internal.pem`, generates SSH aliases from all node aliases
11. `helm` — Installs Helm package manager
12. `cronjobs/refresh_ecr_creds` — Templates ECR refresh script, sets cron at 12AM/12PM
13. `cronjobs/clean_yarn_caches` — Cleans yarn cache periodically
14. `cronjobs/clean_npm_caches` — Cleans npm cache periodically
15. `awscli` — Installs AWS CLI
16. `zip` — Installs zip/unzip utilities

**Required variables:**
- `hostname` (from `uneditable.yml`)
- `nodejs_version` (from `group_vars/all/editable.yml`)
- `git_version` (from `group_vars/all/uneditable.yml`)
- `custom_users` (from `host_vars/management/uneditable.yml`)
- `redis_password`, `redis_port` (from `host_vars/management/editable.yml`)
- `postgresql_client_version` (from `host_vars/management/editable.yml`)
- `aws_access_key_id`, `aws_secret_access_key`, `aws_registry_url`, `aws_region`, `k3s_namespace` (from `host_vars/management/editable.yml`)

### k3s Master Node
**Host group:** `k3s_master` (child of `k3s_cluster`)
**Access:** Private IP, via management proxy with `internal.pem`
**Roles applied (in order):**
1. `set_hostname` — Sets hostname to inventory hostname
2. `swap` — Configures swap space
3. `nodejs` — Installs Node.js, yarn, pm2
4. `git` — Installs Git
5. `k3s/master/install` — Installs k3s server with configured version and args
6. `k3s/master/get-token` — Extracts join token to local `tmp/` for worker setup
7. `helm` — Installs Helm
8. `cronjobs/prune_docker_images` — Prunes unused Docker/containerd images

**Required variables:**
- `k3s_version` (from `k3s_cluster/uneditable.yml`)
- `k3s_install_args` (from `k3s_cluster/uneditable.yml`)
- `k3s_token_file_path`, `k3s_token_dest` (from `k3s_cluster/uneditable.yml`)
- `nodejs_version` (from `group_vars/all/editable.yml`)

### k3s Worker Node
**Host group:** `k3s_worker` (child of `k3s_cluster`)
**Access:** Private IP, via management proxy with `internal.pem`
**Roles applied (in order):**
1. `set_hostname` — Sets hostname to inventory hostname
2. `swap` — Configures swap space
3. `nodejs` — Installs Node.js, yarn, pm2
4. `git` — Installs Git
5. `k3s/worker/setup` — Installs k3s agent, joins cluster using token from master
6. `cronjobs/prune_docker_images` — Prunes unused images

**Required variables:**
- `k3s_version`, `k3s_install_args` (from `k3s_cluster/uneditable.yml`)
- `k3s_server_url` (from `k3s_cluster/uneditable.yml` — computed from master IP)
- `k3s_token_dest` (from `k3s_cluster/uneditable.yml`)
- `nodejs_version` (from `group_vars/all/editable.yml`)

**Dependency:** k3s master must be set up first (token is read from local `tmp/`).

### Standard Node
**Host group:** `std_nodes`
**Access:** Private IP, via management proxy with `internal.pem`
**Roles applied (in order):**
1. `set_hostname` — Sets hostname to inventory hostname
2. `swap` — Configures swap space
3. `nodejs` — Installs Node.js, yarn, pm2
4. `git` — Installs Git
5. `std_node_users` — Creates non-root users from node `alias` list
6. `docker` — Installs Docker + docker-compose
7. `std_node_users_docker_permission` — Grants docker group access to alias users

**Required variables:**
- `alias` (from `hosts.yml` — per-host list of application user names)
- `nodejs_version` (from `group_vars/all/editable.yml`)

## Inventory Structure

### hosts.yml Format
```yaml
all:
  children:
    management:
      hosts:
        management_node:
          ansible_host: <PUBLIC_IP>
          ansible_port: <SSH_PORT>
          alias:
            - management-node
    k3s_cluster:
        children:
          k3s_master:
            hosts:
              k3s-master:
                ansible_host: <PRIVATE_IP>
                alias:
                  - k3s-master
          k3s_worker:
            hosts:
              k3s-worker-1:
                ansible_host: <PRIVATE_IP>
                alias:
                  - k3s-worker-1
              # Add more workers as needed
    std_nodes:
      hosts:
        web-admin:
          ansible_host: <PRIVATE_IP>
          alias:
            - web
            - admin
        strapi:
          ansible_host: <PRIVATE_IP>
          alias:
            - strapi
```

**Rules:**
- Management group is always required and uncommented
- k3s_cluster and std_nodes should be commented out if not used
- Worker nodes can be commented individually within k3s_worker
- Each host MUST have an `alias` list
- Hostnames in inventory become the actual hostname on the node

## SSH Proxy Architecture

### Connection Flow
```
Control Machine → (mgmt.pem, port 10022) → Management Node → (internal.pem, port 10022) → Internal Nodes
```

### Proxy Configuration (from uneditable.yml)
```yaml
# k3s_cluster and std_nodes groups:
ansible_ssh_common_args: >
  -o ProxyCommand="ssh -o IdentitiesOnly=yes -i {{ playbook_dir }}/keys/prod/mgmt.pem -p 10022 -o StrictHostKeyChecking=no -W %h:%p ubuntu@{{ hostvars['management_node'].ansible_host }}"
  -o IdentitiesOnly=yes
  -o StrictHostKeyChecking=no
ansible_ssh_private_key_file: "{{ playbook_dir }}/keys/prod/internal.pem"

# Management node:
ansible_ssh_common_args: ""  # No proxy for self
ansible_ssh_private_key_file: "{{ playbook_dir }}/keys/prod/mgmt.pem"
```

## Variable Files Reference

### Editable Files (safe to modify)
| File | Variables | Purpose |
|------|-----------|---------|
| `group_vars/all/editable.yml` | `nodejs_version` | Global Node.js version |
| `host_vars/management/editable.yml` | `postgresql_client_version`, `redis_password`, `redis_port`, `aws_access_key_id`, `aws_secret_access_key`, `aws_registry_url`, `aws_region`, `k3s_namespace` | Management node services config |

### Uneditable Files (do NOT modify)
| File | Variables | Purpose |
|------|-----------|---------|
| `group_vars/all/uneditable.yml` | `git_version` | Global defaults |
| `group_vars/k3s_cluster/uneditable.yml` | `ansible_user`, `ansible_port`, `ansible_ssh_common_args`, `ansible_ssh_private_key_file`, `hostname`, `k3s_*` vars | k3s SSH proxy + cluster config |
| `group_vars/std_nodes/uneditable.yml` | `ansible_user`, `ansible_port`, `ansible_ssh_common_args`, `ansible_ssh_private_key_file`, `hostname` | Standard nodes SSH proxy config |
| `host_vars/management/uneditable.yml` | `ansible_ssh_common_args`, `ansible_ssh_private_key_file`, `hostname`, `custom_users` | Management SSH config + users |

## Playbook Execution Order

```
1. setup-management.yml          [REQUIRED] [FIRST]
   ↓
2. setup-k3s-master.yml          [IF k3s] [AFTER 1]
   ↓
3. setup-k3s-worker.yml          [IF k3s] [AFTER 2]
   ↓
4. setup-std-node.yml            [IF std_nodes] [AFTER 1]
   ↓
5. setup-management-k3s-access.yml [IF k3s] [AFTER 1+2]
```

**Dependencies:**
- All playbooks depend on management (it's the jump host)
- k3s workers depend on k3s master (need join token)
- k3s access playbook depends on both management and k3s master
- Standard nodes only depend on management (for proxy access)

## Troubleshooting

### Common Issues

**"Permission denied (publickey)" on management:**
- Check: `mgmt.pem` exists in `keys/prod/` with 400 permissions
- Check: Correct public IP in `hosts.yml`
- Check: Security group allows SSH on port 10022

**"Permission denied" on internal nodes:**
- Check: `internal.pem` exists in `keys/prod/` with 400 permissions
- Check: Management node is reachable first
- Check: Internal node private IPs are correct
- Check: Proxy config in `k3s_cluster/uneditable.yml` or `std_nodes/uneditable.yml` is intact

**k3s worker fails to join:**
- Verify k3s master setup completed successfully
- Check token file exists: `ls AWS/tmp/k3s_node_token`
- Verify `k3s_server_url` resolves to master's private IP
- Check master is healthy: `ansible k3s_master -m shell -a "k3s kubectl get nodes"`

**"No hosts matched" error:**
- Section is commented out in `hosts.yml` — uncomment the needed group
- Typo in group name — verify against playbook `hosts:` field

**Redis connection refused:**
- Check `redis_password` and `redis_port` in `editable.yml`
- Verify Redis service: `ansible management -m shell -a "systemctl status redis-server"`

**Jenkins not accessible:**
- Default port: 8080
- Check security group allows port 8080
- Get initial admin password: `ansible management -m shell -a "cat /var/lib/jenkins/secrets/initialAdminPassword"`

## Handoff Input (from Deploy Skill)

The `coe-infra-deploy-aws` skill generates `handoff.json` in the Terraform project directory (`projects/<project-name>/handoff.json`). If available, read it to auto-populate inventory.

**Expected fields from deploy handoff:**
- `vpc_id`, `subnet_ids`, `security_group_id` — network context
- EC2 instance outputs — management node public IP, app/k3s node private IPs, instance names, roles

**How to consume:**
1. Ask user for the handoff.json path (e.g., `../../projects/<project-name>/handoff.json`)
2. Read and parse the JSON
3. Extract management public IP, internal node private IPs, node names
4. Map k3s-named nodes to `k3s_cluster` group, others to `std_nodes`
5. Ask user to confirm extracted values and provide aliases

## Output Files

### outputs.txt
**Location:** `AWS/outputs.txt`
**Generated in:** Step 8b
**Contents:** Verification results from all configured nodes — hostnames, service versions (Docker, Node.js, Redis, Helm), k3s cluster node list, Jenkins status. Timestamped.
**Security:** May contain IPs and hostnames. Do NOT display in chat. Inform user to review the file.

### handoff.json
**Location:** `AWS/handoff.json`
**Generated in:** Step 8c
**Purpose:** Structured post-configuration state for downstream consumers (monitoring, CI/CD, documentation).

**Schema:**
```json
{
  "version": "1.0",
  "type": "ansible-config",
  "timestamp": "2026-03-25T10:00:00Z",
  "project": {
    "cloud": "aws",
    "environment": "production",
    "region": "<aws-region>"
  },
  "nodes": {
    "management": {
      "hostname": "management-node",
      "public_ip": "<ip>",
      "ssh_port": 10022,
      "ssh_user": "ubuntu",
      "services": ["docker", "jenkins", "redis", "nodejs", "helm", "awscli"],
      "custom_users": ["management-user"],
      "cronjobs": ["refresh_ecr_creds", "clean_yarn_caches", "clean_npm_caches"]
    },
    "k3s_master": {
      "hostname": "<hostname>",
      "private_ip": "<ip>",
      "services": ["k3s-server", "nodejs", "helm"],
      "k3s_version": "<version>"
    },
    "k3s_workers": [
      {
        "hostname": "<hostname>",
        "private_ip": "<ip>",
        "services": ["k3s-agent", "nodejs"]
      }
    ],
    "std_nodes": [
      {
        "hostname": "<hostname>",
        "private_ip": "<ip>",
        "aliases": ["<alias1>", "<alias2>"],
        "services": ["docker", "nodejs"]
      }
    ]
  },
  "access": {
    "management_ssh": "ssh -i keys/prod/mgmt.pem -p 10022 ubuntu@<mgmt-ip>",
    "internal_proxy": "via management node",
    "kubectl": "available as management-user on management node"
  },
  "status": "complete"
}
```

**Rules:**
- Omit `k3s_master`, `k3s_workers` if k3s was not configured
- Omit `std_nodes` if no standard nodes were configured
- NEVER include passwords, AWS credentials, or SSH key contents
- Include only IPs, hostnames, service names, and access commands

## Post-Configuration Verification Commands

**Management node services:**
```bash
cd AWS && ansible management -m shell -a "docker --version && node --version && systemctl status jenkins --no-pager -l"
```

**k3s cluster health:**
```bash
cd AWS && ansible k3s_master -m shell -a "k3s kubectl get nodes"
```

**Standard node users:**
```bash
cd AWS && ansible std_nodes -m shell -a "cat /etc/passwd | tail -5"
```

## Ansible Configuration Defaults

From `ansible.cfg`:
```ini
[defaults]
inventory = inventories/prod/hosts.yml
remote_user = ubuntu
host_key_checking = False
retry_files_enabled = False
interpreter_python = auto
```

- All nodes use `ubuntu` as remote user
- Host key checking is disabled (expected for cloud instances)
- Python interpreter is auto-detected
