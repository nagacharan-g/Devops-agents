# Pre-Phase - Verify Ready to Start Phase

Check prerequisites before starting a new implementation phase.

## What This Command Does

Validates that:
1. Previous phase is complete
2. All required files exist
3. Backups are in place
4. No blocking violations exist
5. Ready to proceed safely

## Usage

```bash
/pre-phase <N>
```

Examples:
```bash
/pre-phase 0    # Check ready for Phase 0 (Restructure)
/pre-phase 1    # Check ready for Phase 1 (Foundation)
/pre-phase 2    # Check ready for Phase 2 (Scripts)
```

## When to Use

- ✅ Before starting any phase
- ✅ After completing previous phase's /post-phase
- ✅ When resuming work after interruption

## What It Checks Per Phase

### Pre-Phase 0: Restructure
Prerequisites:
- [ ] COMPLIANCE-RULES.md exists
- [ ] IMPLEMENTATION-PLAN.md exists
- [ ] All fix plans (C2-C13) exist in fix-plans/
- [ ] Current skill file(s) exist to restructure
- [ ] Git status is clean OR user acknowledges uncommitted changes

Warnings:
- ⚠️ No backup exists yet (will be created during phase)

### Pre-Phase 1: Foundation
Prerequisites:
- [ ] Phase 0 complete (terraform-skill.md and REFERENCE.md exist)
- [ ] Both files within size limits
- [ ] /audit-skill passes
- [ ] Backup exists: terraform-skill.md.backup-phase0

Blockers:
- ❌ Phase 0 not complete
- ❌ Files exceed size limits
- ❌ Audit failures

### Pre-Phase 2: Scripts & Validation
Prerequisites:
- [ ] Phase 1 complete (.gitignore template added)
- [ ] /audit-skill passes
- [ ] Backup exists: terraform-skill.md.backup-phase1
- [ ] No C2 violations

Blockers:
- ❌ Phase 1 not complete
- ❌ .gitignore template missing

### Pre-Phase 3: Security & Credentials
Prerequisites:
- [ ] Phase 2 complete (validation scripts embedded)
- [ ] Template count = 8 (validation + terraform scripts)
- [ ] /audit-skill passes
- [ ] Backup exists: terraform-skill.md.backup-phase2

Blockers:
- ❌ Phase 2 not complete
- ❌ Validation scripts missing

### Pre-Phase 4: Outputs & Handoff
Prerequisites:
- [ ] Phase 3 complete (credentials script added)
- [ ] Template count = 9 (includes setup-credentials.sh)
- [ ] /audit-skill passes
- [ ] Backup exists: terraform-skill.md.backup-phase3

Blockers:
- ❌ Phase 3 not complete
- ❌ Credentials handling not implemented

### Pre-Phase 5: State Machine
Prerequisites:
- [ ] Phase 4 complete (handoff schema in REFERENCE.md)
- [ ] Template count = 10 (includes handoff scripts)
- [ ] /audit-skill passes
- [ ] Backup exists: terraform-skill.md.backup-phase4
- [ ] Handoff schema defined

Blockers:
- ❌ Phase 4 not complete
- ❌ Handoff schema missing

### Pre-Phase 6: End-to-End Testing
Prerequisites:
- [ ] Phase 5 complete (state machine implemented)
- [ ] Template count = 11 (all scripts present)
- [ ] /audit-skill passes with 0 violations
- [ ] Backup exists: terraform-skill.md.backup-phase5
- [ ] All C2-C13 implemented (except C8 deferred)

Blockers:
- ❌ Phase 5 not complete
- ❌ State machine not implemented
- ❌ Any audit violations

## Check Logic

```bash
#!/bin/bash
# Pre-Phase Check Script

PHASE=$1

if [ -z "$PHASE" ]; then
  echo "Usage: /pre-phase <N>"
  echo "Example: /pre-phase 1"
  exit 1
fi

echo "=== Pre-Phase $PHASE Check ==="
echo ""

BLOCKERS=0
WARNINGS=0

case $PHASE in
  0)
    echo "Prerequisites for Phase 0 (Restructure):"

    # Check documentation exists
    if [ -f "fix-plans/COMPLIANCE-RULES.md" ]; then
      echo "  ✅ COMPLIANCE-RULES.md exists"
    else
      echo "  ❌ COMPLIANCE-RULES.md missing"
      ((BLOCKERS++))
    fi

    if [ -f "fix-plans/IMPLEMENTATION-PLAN.md" ]; then
      echo "  ✅ IMPLEMENTATION-PLAN.md exists"
    else
      echo "  ❌ IMPLEMENTATION-PLAN.md missing"
      ((BLOCKERS++))
    fi

    # Check git status
    if git status --porcelain 2>/dev/null | grep -q .; then
      echo "  ⚠️  Uncommitted changes detected"
      ((WARNINGS++))
    else
      echo "  ✅ Git status clean"
    fi
    ;;

  1)
    echo "Prerequisites for Phase 1 (Foundation):"

    # Check Phase 0 complete
    if [ -f "terraform-skill.md" ] && [ -f "terraform-skill-REFERENCE.md" ]; then
      echo "  ✅ Phase 0 complete (files exist)"
    else
      echo "  ❌ Phase 0 not complete (files missing)"
      ((BLOCKERS++))
    fi

    # Check file sizes
    MAIN_LINES=$(wc -l < terraform-skill.md 2>/dev/null || echo 999)
    if [ "$MAIN_LINES" -le 180 ]; then
      echo "  ✅ terraform-skill.md within size limit ($MAIN_LINES lines)"
    else
      echo "  ❌ terraform-skill.md too large ($MAIN_LINES lines)"
      ((BLOCKERS++))
    fi

    # Check backup exists
    if [ -f "terraform-skill.md.backup-phase0" ]; then
      echo "  ✅ Phase 0 backup exists"
    else
      echo "  ⚠️  Phase 0 backup missing"
      ((WARNINGS++))
    fi
    ;;

  2)
    echo "Prerequisites for Phase 2 (Scripts & Validation):"

    # Check .gitignore template added
    if grep -q "### File: .gitignore" terraform-skill.md 2>/dev/null; then
      echo "  ✅ .gitignore template present"
    else
      echo "  ❌ .gitignore template missing (Phase 1 incomplete)"
      ((BLOCKERS++))
    fi

    # Check backup
    if [ -f "terraform-skill.md.backup-phase1" ]; then
      echo "  ✅ Phase 1 backup exists"
    else
      echo "  ⚠️  Phase 1 backup missing"
      ((WARNINGS++))
    fi
    ;;

  3)
    echo "Prerequisites for Phase 3 (Security & Credentials):"

    # Check validation scripts present
    TEMPLATE_COUNT=$(grep -c "### File:" terraform-skill.md 2>/dev/null || echo 0)
    if [ "$TEMPLATE_COUNT" -ge 8 ]; then
      echo "  ✅ Validation scripts embedded (found $TEMPLATE_COUNT templates)"
    else
      echo "  ❌ Validation scripts missing (found $TEMPLATE_COUNT templates, need ≥8)"
      ((BLOCKERS++))
    fi

    if [ -f "terraform-skill.md.backup-phase2" ]; then
      echo "  ✅ Phase 2 backup exists"
    else
      echo "  ⚠️  Phase 2 backup missing"
      ((WARNINGS++))
    fi
    ;;

  4)
    echo "Prerequisites for Phase 4 (Outputs & Handoff):"

    # Check credentials script
    if grep -q "setup-credentials.sh" terraform-skill.md 2>/dev/null; then
      echo "  ✅ Credentials script present"
    else
      echo "  ❌ Credentials script missing (Phase 3 incomplete)"
      ((BLOCKERS++))
    fi

    if [ -f "terraform-skill.md.backup-phase3" ]; then
      echo "  ✅ Phase 3 backup exists"
    else
      echo "  ⚠️  Phase 3 backup missing"
      ((WARNINGS++))
    fi
    ;;

  5)
    echo "Prerequisites for Phase 5 (State Machine):"

    # Check handoff schema in REFERENCE.md
    if grep -q "handoff.json\|Handoff Schema" terraform-skill-REFERENCE.md 2>/dev/null; then
      echo "  ✅ Handoff schema documented"
    else
      echo "  ❌ Handoff schema missing (Phase 4 incomplete)"
      ((BLOCKERS++))
    fi

    if [ -f "terraform-skill.md.backup-phase4" ]; then
      echo "  ✅ Phase 4 backup exists"
    else
      echo "  ⚠️  Phase 4 backup missing"
      ((WARNINGS++))
    fi
    ;;

  6)
    echo "Prerequisites for Phase 6 (End-to-End Testing):"

    # Check all templates present
    TEMPLATE_COUNT=$(grep -c "### File:" terraform-skill.md 2>/dev/null || echo 0)
    if [ "$TEMPLATE_COUNT" -eq 11 ]; then
      echo "  ✅ All 11 templates embedded"
    else
      echo "  ❌ Missing templates (found $TEMPLATE_COUNT, need 11)"
      ((BLOCKERS++))
    fi

    # Check state machine
    if grep -q "check-state.sh" terraform-skill.md 2>/dev/null; then
      echo "  ✅ State machine implemented"
    else
      echo "  ❌ State machine missing (Phase 5 incomplete)"
      ((BLOCKERS++))
    fi

    if [ -f "terraform-skill.md.backup-phase5" ]; then
      echo "  ✅ Phase 5 backup exists"
    else
      echo "  ⚠️  Phase 5 backup missing"
      ((WARNINGS++))
    fi
    ;;

  *)
    echo "Unknown phase: $PHASE"
    echo "Valid phases: 0, 1, 2, 3, 4, 5, 6"
    exit 1
    ;;
esac

echo ""
echo "=== Summary ==="
echo "Blockers: $BLOCKERS"
echo "Warnings: $WARNINGS"
echo ""

if [ "$BLOCKERS" -eq 0 ]; then
  echo "✅ READY TO START PHASE $PHASE"
  echo ""
  echo "Next steps:"
  echo "1. Start implementing Phase $PHASE"
  echo "2. Run /audit-skill frequently during work"
  echo "3. Run /post-phase $PHASE when complete"
  exit 0
else
  echo "❌ NOT READY - BLOCKERS DETECTED"
  echo ""
  echo "Fix blockers before proceeding."
  exit 1
fi
```

## Output Format

### Successful Check
```
=== Pre-Phase 1 Check ===

Prerequisites for Phase 1 (Foundation):
  ✅ Phase 0 complete (files exist)
  ✅ terraform-skill.md within size limit (152 lines)
  ✅ terraform-skill-REFERENCE.md within size limit (148 lines)
  ✅ Phase 0 backup exists
  ✅ /audit-skill passes

=== Summary ===
Blockers: 0
Warnings: 0

✅ READY TO START PHASE 1

Next steps:
1. Start implementing Phase 1
2. Run /audit-skill frequently during work
3. Run /post-phase 1 when complete
```

### Failed Check
```
=== Pre-Phase 2 Check ===

Prerequisites for Phase 2 (Scripts & Validation):
  ❌ .gitignore template missing (Phase 1 incomplete)
  ⚠️  Phase 1 backup missing
  ❌ /audit-skill fails with 3 violations

=== Summary ===
Blockers: 2
Warnings: 1

❌ NOT READY - BLOCKERS DETECTED

Fix blockers before proceeding:
1. Complete Phase 1 (.gitignore template)
2. Create backup: cp terraform-skill.md terraform-skill.md.backup-phase1
3. Fix audit violations
4. Re-run /pre-phase 2
```

## Success Criteria

Phase start is allowed when:
- ✅ 0 blockers
- ✅ Previous phase complete
- ✅ Backups exist (when applicable)
- ✅ /audit-skill passes (from Phase 1 onward)

Warnings are informative but don't block.

## Enforcement

This command will:
1. Check all prerequisites
2. Count blockers and warnings
3. Return exit code 0 if ready, 1 if blocked
4. Display clear next steps

If blocked, do NOT proceed with phase implementation until blockers are fixed.
