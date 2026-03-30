## Folder structure

```
coe-agents/
│
├── .claude/
│   ├── skills/
│   │   ├── infra-boot/
│   │   │   └── skill.md
│   │   ├── infra-config/
│   │   │   └── skill.md
│   │   ├── init-deploy/
│   │   │   └── skill.md
│   │   ├── cicd-setup/
│   │   │   └── skill.md
│   │   ├── monitoring-logging/
│   │   │   └── skill.md
│   │   ├── documentation/
│   │   │   └── skill.md
│   │   ├── rules-evaluator/
│   │   │   └── skill.md
│   │   └── report-generator/
│   │       └── skill.md
│   │
│   └── commands/
│       ├── deploy.md
│       └── audit.md
│
├── agents/
│   ├── infra-boot/
│   │   ├── README.md
│   │   ├── reference.md
│   │   ├── input.schema.json
│   │   ├── output.schema.json
│   │   ├── examples/
│   │   │   ├── sample-input.json
│   │   │   └── sample-output.json
│   │   ├── templates/
│   │   │   ├── tfvars.template
│   │   │   └── backend.hcl
│   │   ├── terraform/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   └── modules/
│   │   ├── scripts/
│   │   │   ├── validate_inputs.py
│   │   │   ├── render_tfvars.py
│   │   │   └── collect_outputs.py
│   │   ├── handoff/
│   │   │   └── handoff.example.json
│   │   └── tests/
│   │       └── test_validate_inputs.py
│   │
│   ├── infra-config/
│   │   ├── README.md
│   │   ├── reference.md
│   │   ├── input.schema.json
│   │   ├── output.schema.json
│   │   ├── ansible/
│   │   │   ├── inventory/
│   │   │   ├── playbooks/
│   │   │   ├── roles/
│   │   │   └── group_vars/
│   │   ├── scripts/
│   │   │   ├── generate_inventory.py
│   │   │   └── summarize_run.py
│   │   ├── handoff/
│   │   │   └── handoff.example.json
│   │   └── tests/
│   │
│   ├── init-deploy/
│   ├── cicd-setup/
│   ├── monitoring-logging/
│   ├── documentation/
│   ├── rules-evaluator/
│   └── report-generator/
│
├── orchestration/
│   ├── orchestrator-plan.md
│   ├── state-schema.md
│   ├── control-rules.md
│   ├── runbook.md
│   └── contracts/
│       ├── deployment-state.schema.json
│       └── audit-state.schema.json
│
├── shared/
│   ├── schemas/
│   │   ├── common-status.schema.json
│   │   ├── environment.schema.json
│   │   └── project.schema.json
│   ├── scripts/
│   │   ├── json_logger.py
│   │   ├── file_utils.py
│   │   └── retry.py
│   ├── templates/
│   └── utils/
│
├── runtime/                  # only later, when orchestration starts
│   ├── graph.py
│   ├── state.py
│   ├── agents/
│   │   ├── infra_boot.py
│   │   ├── infra_config.py
│   │   └── ...
│   └── main.py
│
├── runs/                     # generated artifacts, optional
│   ├── deployment/
│   └── audit/
│
├── docs/
│   ├── architecture.md
│   ├── agent-interactions.md
│   └── onboarding.md
│
└── README.md
```
