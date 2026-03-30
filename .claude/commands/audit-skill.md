# Audit Skill - Full Compliance Check

Run a comprehensive compliance audit against COMPLIANCE-RULES.md.

## What This Command Does

Checks the Terraform skill against all compliance rules:
1. DRY principle (no duplication)
2. File size limits (~150 lines, max 180)
3. Main skill structure (conversation flow only)
4. REFERENCE.md structure (reference data only)
5. Script embedding (all 11 templates present)
6. Security fixes (C2-C13 implementation)
7. No inline terraform commands
8. State machine enforcement
9. Handoff file schema compliance

## Usage

```bash
/audit-skill
```

Optional: Check security only
```bash
/audit-skill --security-only
```

## When to Use

- ✅ Before starting any phase
- ✅ After completing any phase
- ✅ Frequently during implementation
- ✅ Before committing changes
- ✅ When unsure if changes broke compliance

## What It Checks

### 1. DRY Compliance
```bash
# Search for duplicated patterns across files
grep -n "Pattern.*project.*name" terraform-skill.md terraform-skill-REFERENCE.md

# Check validation rules appear only in REFERENCE.md
grep -n "^[a-z][a-z0-9-]{2,29}\$" terraform-skill.md
# Should be 0 results (only in REFERENCE.md)
```

Expected: Each instruction appears once only.

### 2. File Size Limits
```bash
wc -l terraform-skill.md
wc -l terraform-skill-REFERENCE.md
```

Expected:
- terraform-skill.md: ~150 lines (max 180)
- terraform-skill-REFERENCE.md: ~150 lines (max 180)

### 3. Template Count
```bash
grep -c "### File:" terraform-skill.md
```

Expected: 11 templates embedded

Templates required:
1. `.gitignore`
2. `scripts/validate-input.sh`
3. `scripts/validate-config.py`
4. `scripts/setup-credentials.sh`
5. `scripts/tf-init.sh`
6. `scripts/tf-plan.sh`
7. `scripts/tf-apply.sh`
8. `scripts/tf-destroy.sh`
9. `scripts/generate-handoff.py`
10. `scripts/validate-handoff.py`
11. `scripts/check-state.sh`

### 4. No Inline Commands
```bash
# Check for direct terraform commands (should be 0 in workflow steps)
grep -n "^terraform init\|^terraform plan\|^terraform apply" terraform-skill.md
```

Expected: 0 results (all commands in scripts)

Exceptions: Examples in REFERENCE.md are OK

### 5. Security Audit (C2-C13)

**C2: .gitignore**
- [ ] Template exists in skill
- [ ] Contains: *.tfstate, *.tfvars, outputs.txt, handoff.json

**C3: Credentials**
- [ ] No "ask user for credentials" in chat
- [ ] setup-credentials.sh script exists
- [ ] Step 8.5 uses script

**C4: Sensitive Outputs**
- [ ] Step 15 writes to outputs.txt
- [ ] No outputs displayed in chat
- [ ] Only file path shown

**C6/C7: Handoff Schema**
- [ ] handoff.json schema defined in REFERENCE.md
- [ ] Schema version 1.0
- [ ] No sensitive data in handoff

**C8: Remote Backend**
- [ ] Documented as deferred
- [ ] Future enhancement section exists
- [ ] Migration instructions present

**C10: Script-Based Commands**
- [ ] All 11 scripts embedded
- [ ] No inline terraform commands
- [ ] Scripts have error handling

**C11: Validation Script**
- [ ] validate-config.py exists
- [ ] Field-by-field validation
- [ ] Config-level validation
- [ ] .inputs.json workflow documented

**C12: State Machine**
- [ ] check-state.sh exists
- [ ] State checks in tf-*.sh scripts
- [ ] State flow diagram in skill
- [ ] State matrix in REFERENCE.md

**C13: Inter-Agent Handoff**
- [ ] handoff.json at known path
- [ ] Structured format (not natural language)
- [ ] Schema explicitly defined

### 6. Structure Validation

**Main Skill Must Contain:**
- [ ] Brief description
- [ ] Workflow steps (conversation flow)
- [ ] Important restrictions
- [ ] State machine diagram
- [ ] Templates section

**Main Skill Must NOT Contain:**
- [ ] Validation logic (should be in scripts)
- [ ] Schema definitions (should be in REFERENCE.md)
- [ ] Error message templates (should be in REFERENCE.md)
- [ ] Detailed AWS lists (should be in REFERENCE.md)

**REFERENCE.md Must Contain:**
- [ ] Validation rules section
- [ ] Naming conventions
- [ ] AWS resource lists
- [ ] Schema definitions
- [ ] State transition matrix
- [ ] Error templates
- [ ] Future enhancements

**REFERENCE.md Must NOT Contain:**
- [ ] Conversation flow
- [ ] Step-by-step instructions
- [ ] "Ask user for..." statements

## Output Format

```
=== Terraform Skill Compliance Audit ===

DRY Compliance:
  ✅ No duplicated instructions found
  ✅ Validation rules only in REFERENCE.md
  ✅ Schema definitions only in REFERENCE.md

File Sizes:
  ✅ terraform-skill.md: 152 lines (target: ~150, max: 180)
  ✅ terraform-skill-REFERENCE.md: 148 lines (target: ~150, max: 180)

Template Count:
  ✅ 11/11 templates embedded

No Inline Commands:
  ✅ All terraform commands in scripts

Security Audit (C2-C13):
  ✅ C2: .gitignore template exists
  ✅ C3: Credentials via script
  ✅ C4: Outputs to file
  ✅ C6/C7: Handoff schema defined
  ⚠️  C8: Remote backend deferred (documented)
  ✅ C10: All scripts embedded
  ✅ C11: Validation scripts present
  ✅ C12: State machine implemented
  ✅ C13: Inter-agent handoff structured

Structure Validation:
  ✅ Main skill: Conversation flow only
  ✅ REFERENCE.md: Reference data only
  ✅ Clear separation of concerns

Overall: 11/13 PASSED (C8 deferred, C9 N/A)

Violations: None
Warnings: Remote backend not implemented (by design)
```

## Audit Script

You should execute these checks when running this command:

```bash
#!/bin/bash
# Terraform Skill Compliance Audit

echo "=== Terraform Skill Compliance Audit ==="
echo ""

VIOLATIONS=0
WARNINGS=0

# 1. Check file existence
echo "File Existence:"
if [ -f "terraform-skill.md" ]; then
  echo "  ✅ terraform-skill.md exists"
else
  echo "  ❌ terraform-skill.md missing"
  ((VIOLATIONS++))
fi

if [ -f "terraform-skill-REFERENCE.md" ]; then
  echo "  ✅ terraform-skill-REFERENCE.md exists"
else
  echo "  ❌ terraform-skill-REFERENCE.md missing"
  ((VIOLATIONS++))
fi
echo ""

# 2. Check file sizes
echo "File Sizes:"
MAIN_LINES=$(wc -l < terraform-skill.md 2>/dev/null || echo 0)
REF_LINES=$(wc -l < terraform-skill-REFERENCE.md 2>/dev/null || echo 0)

if [ "$MAIN_LINES" -le 180 ]; then
  echo "  ✅ terraform-skill.md: $MAIN_LINES lines (max: 180)"
else
  echo "  ❌ terraform-skill.md: $MAIN_LINES lines (exceeds max: 180)"
  ((VIOLATIONS++))
fi

if [ "$REF_LINES" -le 180 ]; then
  echo "  ✅ terraform-skill-REFERENCE.md: $REF_LINES lines (max: 180)"
else
  echo "  ❌ terraform-skill-REFERENCE.md: $REF_LINES lines (exceeds max: 180)"
  ((VIOLATIONS++))
fi
echo ""

# 3. Template count
echo "Template Count:"
TEMPLATE_COUNT=$(grep -c "### File:" terraform-skill.md 2>/dev/null || echo 0)
if [ "$TEMPLATE_COUNT" -eq 11 ]; then
  echo "  ✅ 11/11 templates embedded"
else
  echo "  ❌ $TEMPLATE_COUNT/11 templates found (expected 11)"
  ((VIOLATIONS++))
fi
echo ""

# 4. No inline terraform commands
echo "No Inline Commands:"
INLINE_COUNT=$(grep -c "^terraform init\|^terraform plan\|^terraform apply" terraform-skill.md 2>/dev/null || echo 0)
if [ "$INLINE_COUNT" -eq 0 ]; then
  echo "  ✅ No inline terraform commands"
else
  echo "  ⚠️  Found $INLINE_COUNT inline terraform commands"
  ((WARNINGS++))
fi
echo ""

# 5. Security audit
echo "Security Audit (C2-C13):"

# C2
if grep -q "### File: .gitignore" terraform-skill.md 2>/dev/null; then
  echo "  ✅ C2: .gitignore template exists"
else
  echo "  ❌ C2: .gitignore template missing"
  ((VIOLATIONS++))
fi

# C3
if grep -q "setup-credentials.sh" terraform-skill.md 2>/dev/null; then
  echo "  ✅ C3: Credentials via script"
else
  echo "  ❌ C3: setup-credentials.sh missing"
  ((VIOLATIONS++))
fi

# C4
if grep -q "outputs.txt" terraform-skill.md 2>/dev/null; then
  echo "  ✅ C4: Outputs to file"
else
  echo "  ❌ C4: outputs.txt workflow missing"
  ((VIOLATIONS++))
fi

# C6/C7
if grep -q "handoff.json" terraform-skill-REFERENCE.md 2>/dev/null; then
  echo "  ✅ C6/C7: Handoff schema defined"
else
  echo "  ❌ C6/C7: Handoff schema missing"
  ((VIOLATIONS++))
fi

# C8
if grep -q "Remote Backend\|remote backend" terraform-skill-REFERENCE.md 2>/dev/null; then
  echo "  ⚠️  C8: Remote backend deferred (documented)"
else
  echo "  ❌ C8: Remote backend not documented"
  ((VIOLATIONS++))
fi

# C10
if grep -q "tf-init.sh\|tf-plan.sh\|tf-apply.sh" terraform-skill.md 2>/dev/null; then
  echo "  ✅ C10: Script-based commands"
else
  echo "  ❌ C10: Scripts missing"
  ((VIOLATIONS++))
fi

# C11
if grep -q "validate-config.py" terraform-skill.md 2>/dev/null; then
  echo "  ✅ C11: Validation scripts present"
else
  echo "  ❌ C11: Validation scripts missing"
  ((VIOLATIONS++))
fi

# C12
if grep -q "check-state.sh" terraform-skill.md 2>/dev/null; then
  echo "  ✅ C12: State machine implemented"
else
  echo "  ❌ C12: State machine missing"
  ((VIOLATIONS++))
fi

# C13
if grep -q "inter-agent\|Inter-Agent" terraform-skill-REFERENCE.md 2>/dev/null; then
  echo "  ✅ C13: Inter-agent handoff documented"
else
  echo "  ❌ C13: Inter-agent handoff missing"
  ((VIOLATIONS++))
fi

echo ""
echo "=== Summary ==="
echo "Violations: $VIOLATIONS"
echo "Warnings: $WARNINGS"
echo ""

if [ "$VIOLATIONS" -eq 0 ]; then
  echo "✅ AUDIT PASSED"
  exit 0
else
  echo "❌ AUDIT FAILED"
  exit 1
fi
```

## Success Criteria

Audit passes when:
- ✅ 0 violations
- ✅ 11/13 security items pass (C8 deferred is acceptable)
- ✅ All files within size limits
- ✅ All templates present
- ✅ No duplication detected

## Next Steps After Failed Audit

1. Review violation details
2. Fix violations one by one
3. Re-run `/audit-skill`
4. Repeat until passing
5. Only then proceed to next phase
