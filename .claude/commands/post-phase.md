# Post-Phase - Validate Phase Completion

Verify all deliverables are complete and update progress tracking.

## What This Command Does

After completing a phase:
1. Validates all deliverables exist
2. Checks quality (file sizes, audit)
3. Creates backup
4. Updates IMPLEMENTATION-PLAN.md tracker
5. Prepares for next phase

## Usage

```bash
/post-phase <N>
```

Examples:
```bash
/post-phase 0    # Validate Phase 0 (Restructure) complete
/post-phase 1    # Validate Phase 1 (Foundation) complete
/post-phase 2    # Validate Phase 2 (Scripts) complete
```

## When to Use

- ✅ After finishing all tasks in a phase
- ✅ Before moving to next phase
- ✅ Before committing phase changes

## What It Validates Per Phase

### Post-Phase 0: Restructure
Deliverables:
- [ ] terraform-skill.md exists (~150 lines)
- [ ] terraform-skill-REFERENCE.md exists (~150 lines)
- [ ] No instruction duplicated
- [ ] Skill loads without errors
- [ ] /audit-skill passes

Actions:
1. Verify file sizes
2. Check for duplication
3. Create backup: `terraform-skill.md.backup-phase0`
4. Create backup: `terraform-skill-REFERENCE.md.backup-phase0`
5. Update IMPLEMENTATION-PLAN.md Phase 0 status to ✅
6. Record actual time taken
7. Mark ready for Phase 1

### Post-Phase 1: Foundation
Deliverables:
- [ ] .gitignore template in skill
- [ ] Remote backend documented in REFERENCE.md
- [ ] Skill works after changes
- [ ] /audit-skill passes
- [ ] C2 implemented
- [ ] C8 documented

Actions:
1. Verify .gitignore template
2. Verify backend documentation
3. Create backup: `terraform-skill.md.backup-phase1`
4. Update IMPLEMENTATION-PLAN.md Phase 1 status to ✅
5. Mark C2 and C8 as complete
6. Mark ready for Phase 2

### Post-Phase 2: Scripts & Validation
Deliverables:
- [ ] 8 script templates embedded (validation + terraform scripts)
- [ ] Validation rules in REFERENCE.md
- [ ] Main skill references scripts (no inline logic)
- [ ] Scripts execute correctly (if testable)
- [ ] C10 implemented
- [ ] C11 implemented

Templates expected:
1. scripts/validate-input.sh
2. scripts/validate-config.py
3. scripts/tf-init.sh
4. scripts/tf-plan.sh
5. scripts/tf-apply.sh
6. scripts/tf-destroy.sh
7. scripts/generate-handoff.py
8. scripts/validate-handoff.py

Actions:
1. Count templates (must be 8)
2. Verify no inline terraform commands
3. Create backup: `terraform-skill.md.backup-phase2`
4. Update IMPLEMENTATION-PLAN.md Phase 2 status to ✅
5. Mark C10 and C11 as complete
6. Mark ready for Phase 3

### Post-Phase 3: Security & Credentials
Deliverables:
- [ ] Credential script template (setup-credentials.sh)
- [ ] No credentials asked in chat
- [ ] Credential options in REFERENCE.md
- [ ] Template count = 9
- [ ] C3 implemented

Actions:
1. Verify setup-credentials.sh template
2. Verify Step 8.5 added
3. Create backup: `terraform-skill.md.backup-phase3`
4. Update IMPLEMENTATION-PLAN.md Phase 3 status to ✅
5. Mark C3 as complete
6. Mark ready for Phase 4

### Post-Phase 4: Outputs & Handoff
Deliverables:
- [ ] outputs.txt workflow (not in chat)
- [ ] handoff.json created and valid
- [ ] Schema in REFERENCE.md
- [ ] Inter-agent contract documented
- [ ] Template count = 10
- [ ] C4, C6, C7, C13 implemented

Actions:
1. Verify outputs.txt workflow in Step 15
2. Verify handoff.json schema in REFERENCE.md
3. Create backup: `terraform-skill.md.backup-phase4`
4. Update IMPLEMENTATION-PLAN.md Phase 4 status to ✅
5. Mark C4, C6, C7, C13 as complete
6. Mark ready for Phase 5

### Post-Phase 5: State Machine
Deliverables:
- [ ] State checking script (check-state.sh)
- [ ] State matrix in REFERENCE.md
- [ ] Scripts block invalid transitions
- [ ] Main skill shows state flow
- [ ] Template count = 11 (all scripts)
- [ ] C12 implemented

Actions:
1. Verify check-state.sh template
2. Verify state checks in tf-*.sh scripts
3. Create backup: `terraform-skill.md.backup-phase5`
4. Update IMPLEMENTATION-PLAN.md Phase 5 status to ✅
5. Mark C12 as complete
6. Mark ready for Phase 6

### Post-Phase 6: End-to-End Testing
Deliverables:
- [ ] End-to-end test passes
- [ ] Audit score: 11/13 (C8 deferred, C9 N/A)
- [ ] No duplicated instructions
- [ ] All files under ~150 lines
- [ ] Full deployment test successful

Actions:
1. Verify test results
2. Run full /audit-skill
3. Create final backup: `terraform-skill.md.backup-final`
4. Update IMPLEMENTATION-PLAN.md Phase 6 status to ✅
5. Mark overall status as COMPLETE
6. Celebrate! 🎉

## Validation Script

```bash
#!/bin/bash
# Post-Phase Validation Script

PHASE=$1

if [ -z "$PHASE" ]; then
  echo "Usage: /post-phase <N>"
  echo "Example: /post-phase 1"
  exit 1
fi

echo "=== Post-Phase $PHASE Validation ==="
echo ""

FAILURES=0
WARNINGS=0

case $PHASE in
  0)
    echo "Deliverables for Phase 0 (Restructure):"

    # Check files exist
    if [ -f "terraform-skill.md" ]; then
      MAIN_LINES=$(wc -l < terraform-skill.md)
      echo "  ✅ terraform-skill.md exists ($MAIN_LINES lines)"

      if [ "$MAIN_LINES" -gt 180 ]; then
        echo "     ⚠️  Exceeds target (~150 lines)"
        ((WARNINGS++))
      fi
    else
      echo "  ❌ terraform-skill.md missing"
      ((FAILURES++))
    fi

    if [ -f "terraform-skill-REFERENCE.md" ]; then
      REF_LINES=$(wc -l < terraform-skill-REFERENCE.md)
      echo "  ✅ terraform-skill-REFERENCE.md exists ($REF_LINES lines)"

      if [ "$REF_LINES" -gt 180 ]; then
        echo "     ⚠️  Exceeds target (~150 lines)"
        ((WARNINGS++))
      fi
    else
      echo "  ❌ terraform-skill-REFERENCE.md missing"
      ((FAILURES++))
    fi

    # Create backups
    if [ "$FAILURES" -eq 0 ]; then
      echo ""
      echo "Creating backups..."
      cp terraform-skill.md terraform-skill.md.backup-phase0
      cp terraform-skill-REFERENCE.md terraform-skill-REFERENCE.md.backup-phase0
      echo "  ✅ Backups created"
    fi
    ;;

  1)
    echo "Deliverables for Phase 1 (Foundation):"

    # Check .gitignore template
    if grep -q "### File: .gitignore" terraform-skill.md; then
      echo "  ✅ .gitignore template present"
    else
      echo "  ❌ .gitignore template missing"
      ((FAILURES++))
    fi

    # Check remote backend docs
    if grep -q -i "remote backend\|Remote Backend" terraform-skill-REFERENCE.md; then
      echo "  ✅ Remote backend documented"
    else
      echo "  ❌ Remote backend documentation missing"
      ((FAILURES++))
    fi

    # Create backup
    if [ "$FAILURES" -eq 0 ]; then
      echo ""
      echo "Creating backup..."
      cp terraform-skill.md terraform-skill.md.backup-phase1
      echo "  ✅ Backup created"
    fi
    ;;

  2)
    echo "Deliverables for Phase 2 (Scripts & Validation):"

    # Count templates
    TEMPLATE_COUNT=$(grep -c "### File:" terraform-skill.md)
    if [ "$TEMPLATE_COUNT" -ge 8 ]; then
      echo "  ✅ Script templates embedded ($TEMPLATE_COUNT/8+)"
    else
      echo "  ❌ Missing script templates ($TEMPLATE_COUNT/8)"
      ((FAILURES++))
    fi

    # Check validation scripts
    if grep -q "validate-config.py" terraform-skill.md; then
      echo "  ✅ Validation scripts present"
    else
      echo "  ❌ Validation scripts missing"
      ((FAILURES++))
    fi

    # Check no inline commands
    INLINE_COUNT=$(grep -c "^terraform init\|^terraform plan\|^terraform apply" terraform-skill.md || echo 0)
    if [ "$INLINE_COUNT" -eq 0 ]; then
      echo "  ✅ No inline terraform commands"
    else
      echo "  ⚠️  Found $INLINE_COUNT inline commands"
      ((WARNINGS++))
    fi

    # Create backup
    if [ "$FAILURES" -eq 0 ]; then
      echo ""
      echo "Creating backup..."
      cp terraform-skill.md terraform-skill.md.backup-phase2
      echo "  ✅ Backup created"
    fi
    ;;

  3)
    echo "Deliverables for Phase 3 (Security & Credentials):"

    # Check credential script
    if grep -q "setup-credentials.sh" terraform-skill.md; then
      echo "  ✅ Credential script template present"
    else
      echo "  ❌ Credential script missing"
      ((FAILURES++))
    fi

    # Check Step 8.5
    if grep -q "Step 8.5\|Step 8\.5" terraform-skill.md; then
      echo "  ✅ Step 8.5 added"
    else
      echo "  ⚠️  Step 8.5 not clearly marked"
      ((WARNINGS++))
    fi

    # Create backup
    if [ "$FAILURES" -eq 0 ]; then
      echo ""
      echo "Creating backup..."
      cp terraform-skill.md terraform-skill.md.backup-phase3
      echo "  ✅ Backup created"
    fi
    ;;

  4)
    echo "Deliverables for Phase 4 (Outputs & Handoff):"

    # Check outputs.txt workflow
    if grep -q "outputs.txt" terraform-skill.md; then
      echo "  ✅ outputs.txt workflow present"
    else
      echo "  ❌ outputs.txt workflow missing"
      ((FAILURES++))
    fi

    # Check handoff schema
    if grep -q "handoff.json\|Handoff Schema" terraform-skill-REFERENCE.md; then
      echo "  ✅ Handoff schema documented"
    else
      echo "  ❌ Handoff schema missing"
      ((FAILURES++))
    fi

    # Create backup
    if [ "$FAILURES" -eq 0 ]; then
      echo ""
      echo "Creating backup..."
      cp terraform-skill.md terraform-skill.md.backup-phase4
      echo "  ✅ Backup created"
    fi
    ;;

  5)
    echo "Deliverables for Phase 5 (State Machine):"

    # Check state script
    if grep -q "check-state.sh" terraform-skill.md; then
      echo "  ✅ State checking script present"
    else
      echo "  ❌ check-state.sh missing"
      ((FAILURES++))
    fi

    # Check state matrix
    if grep -q -i "state transition\|State Machine" terraform-skill-REFERENCE.md; then
      echo "  ✅ State matrix documented"
    else
      echo "  ❌ State matrix missing"
      ((FAILURES++))
    fi

    # Check template count
    TEMPLATE_COUNT=$(grep -c "### File:" terraform-skill.md)
    if [ "$TEMPLATE_COUNT" -eq 11 ]; then
      echo "  ✅ All 11 templates present"
    else
      echo "  ❌ Template count mismatch ($TEMPLATE_COUNT/11)"
      ((FAILURES++))
    fi

    # Create backup
    if [ "$FAILURES" -eq 0 ]; then
      echo ""
      echo "Creating backup..."
      cp terraform-skill.md terraform-skill.md.backup-phase5
      echo "  ✅ Backup created"
    fi
    ;;

  6)
    echo "Deliverables for Phase 6 (End-to-End Testing):"

    # Run audit
    echo "  Running full audit..."
    # (Would run /audit-skill here)

    echo "  ⚠️  Manual verification required:"
    echo "     - End-to-end deployment test"
    echo "     - All features working"
    echo "     - No regressions"

    # Create final backup
    echo ""
    echo "Creating final backup..."
    cp terraform-skill.md terraform-skill.md.backup-final
    cp terraform-skill-REFERENCE.md terraform-skill-REFERENCE.md.backup-final
    echo "  ✅ Final backups created"
    ;;

  *)
    echo "Unknown phase: $PHASE"
    echo "Valid phases: 0, 1, 2, 3, 4, 5, 6"
    exit 1
    ;;
esac

echo ""
echo "=== Summary ==="
echo "Failures: $FAILURES"
echo "Warnings: $WARNINGS"
echo ""

if [ "$FAILURES" -eq 0 ]; then
  echo "✅ PHASE $PHASE COMPLETE"
  echo ""
  echo "Next steps:"
  echo "1. Review changes"
  echo "2. Commit changes (optional): git add -A && git commit -m \"Phase $PHASE complete\""

  NEXT_PHASE=$((PHASE + 1))
  if [ "$NEXT_PHASE" -le 6 ]; then
    echo "3. Run /pre-phase $NEXT_PHASE to start next phase"
  else
    echo "3. 🎉 ALL PHASES COMPLETE!"
  fi

  exit 0
else
  echo "❌ PHASE $PHASE INCOMPLETE"
  echo ""
  echo "Fix failures before proceeding."
  exit 1
fi
```

## Tracker Update

After successful validation, this command updates `fix-plans/IMPLEMENTATION-PLAN.md`:

```markdown
### Phase X: [Name] ✅

| Task | Status | Time Est | Actual | Notes |
|------|--------|----------|--------|-------|
| Task 1 | ✅ | 10 min | 12 min | Done |
| Task 2 | ✅ | 15 min | 14 min | Done |
| **Phase X Total** | ✅ | **25 min** | **26 min** | |

**Deliverables**:
- [x] Deliverable 1
- [x] Deliverable 2
- [x] Deliverable 3
```

## Output Format

### Successful Validation
```
=== Post-Phase 1 Validation ===

Deliverables for Phase 1 (Foundation):
  ✅ .gitignore template present
  ✅ Remote backend documented
  ✅ Skill works after changes
  ✅ /audit-skill passes

Creating backup...
  ✅ Backup created

Updating tracker...
  ✅ IMPLEMENTATION-PLAN.md updated
  ✅ Phase 1 marked complete
  ✅ C2 marked complete
  ✅ C8 marked complete

=== Summary ===
Failures: 0
Warnings: 0

✅ PHASE 1 COMPLETE

Next steps:
1. Review changes
2. Commit changes (optional): git add -A && git commit -m "Phase 1 complete"
3. Run /pre-phase 2 to start next phase
```

### Failed Validation
```
=== Post-Phase 2 Validation ===

Deliverables for Phase 2 (Scripts & Validation):
  ❌ Missing script templates (6/8)
  ❌ Validation scripts missing
  ⚠️  Found 2 inline commands

=== Summary ===
Failures: 2
Warnings: 1

❌ PHASE 2 INCOMPLETE

Fix failures before proceeding:
1. Add missing script templates (need 2 more)
2. Add validate-config.py template
3. Remove inline terraform commands
4. Re-run /post-phase 2
```

## Success Criteria

Phase is complete when:
- ✅ 0 failures
- ✅ All deliverables present
- ✅ Backups created
- ✅ Tracker updated
- ✅ Ready to move to next phase

Warnings are noted but don't block completion.

## Enforcement

This command will:
1. Verify all deliverables
2. Count failures and warnings
3. Create backups if passing
4. Update IMPLEMENTATION-PLAN.md
5. Return exit code 0 if complete, 1 if incomplete
6. Show clear next steps

If incomplete, fix failures and re-run before proceeding to next phase.
