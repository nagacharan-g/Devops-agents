# Claude Code Skills for Terraform IAC

This directory contains Claude Code skills for managing infrastructure as code with Terraform.

## Available Skills

### 🧪 skill-tester
**Location:** `.claude/skills/skill-tester/`

Testing framework for Claude Code skills with strict context isolation.

**Features:**
- Isolated skill execution (prevents context bleeding)
- Multiple exit commands (`:exit`, `:back`, `:claude`)
- Session recording and replay
- Debug mode to see skill state
- Iterative development workflow

**Quick Start:**
```
Test my skill
```

Or:
```
Test coe-infra-deploy-aws skill with debug mode
```

**Documentation:**
- [README](skills/skill-tester/README.md) - Usage guide and examples
- [Skill Definition](skills/skill-tester/skill.md) - Technical implementation

---

### 🚀 coe-infra-deploy-aws
**Location:** `.claude/skills/coe-infra-deploy-aws/`

Specialized skill for deploying CoE Staging and Production environments on AWS using Terraform.

**Features:**
- Opinionated CoE infrastructure patterns
- Auto-configured management nodes (t4g.medium)
- Supports k3s node identification for production
- Interactive deployment workflow
- Plan review before applying changes
- Enforced naming conventions
- Error handling and troubleshooting

**Quick Start:**
```
Deploy CoE infrastructure to AWS
```

Or:
```
I want to deploy CoE production environment
```

**Documentation:**
- [Skill Definition](skills/coe-infra-deploy-aws/skill.md) - Technical implementation

## Using Skills

### Invoking Skills

Skills can be invoked in multiple ways:

1. **Slash command:** `/skill-name`
2. **Natural language:** Claude detects when to use skills based on context
3. **Explicit request:** "Use the infra-deploy skill to..."

### Listing Skills

To see all available skills:
```
list my skills
```

## Directory Structure

```
.claude/
├── README.md                           # This file
└── skills/
    └── coe-infra-deploy-aws/
        └── skill.md                    # Skill implementation
```

## Creating New Skills

To create a new skill:

1. Create a directory: `.claude/skills/your-skill-name/`
2. Add `skill.md` with the skill logic
3. Add `README.md` with user documentation
4. Optionally add `metadata.json` for metadata

### Skill Template

```markdown
# Your Skill Name

## Description
Brief description of what this skill does

## Workflow
Step-by-step workflow of how the skill operates

## Example Interactions
Show example conversations

## Files to Work With
List relevant files

## Success Criteria
Define when the skill task is complete
```

## Best Practices

### For Skill Development
- ✅ Write clear, step-by-step workflows
- ✅ Include error handling and recovery steps
- ✅ Provide example interactions
- ✅ Document prerequisites and dependencies
- ✅ Add troubleshooting sections
- ✅ **Test with skill-tester** before using in production

### For Skill Testing
- ✅ Use `skill-tester` to test skills in isolation
- ✅ Exit test sessions with `:exit` before modifying skills
- ✅ Enable debug mode to see skill state
- ✅ Save and review test sessions
- ✅ Iterate: test → modify → retest

### For Skill Usage
- ✅ Read the skill documentation before first use
- ✅ Ensure prerequisites are met
- ✅ Review plans/changes before confirming
- ✅ Keep credentials secure
- ✅ Back up important state files

## Contributing

To improve or add skills:

1. Create or modify skill in `.claude/skills/`
2. Test the skill thoroughly
3. Update documentation
4. Add examples
5. Commit changes

## Support

For help with:
- **Claude Code**: Use `/help` or visit [Claude Code docs](https://claude.com/claude-code)
- **Skills**: Check individual skill README files
- **Terraform**: https://www.terraform.io/docs
- **Cloud Providers**: AWS/DigitalOcean documentation

## Version History

- **v2.0.0** (2025-03-19): Updated to `coe-infra-deploy-aws` - CoE-specific AWS deployment skill
- **v1.0.0** (2025-03-19): Initial release with `infra-deploy` skill (deprecated)
