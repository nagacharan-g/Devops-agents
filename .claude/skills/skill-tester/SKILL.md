---
name: skill-tester
description: Test and debug Claude Code skills in isolation. Use when you want to test a skill without context bleeding. Activated by phrases like "test my skill", "test [skill-name] skill", or "debug skill".
disable-model-invocation: false
allowed-tools: [all]
---

# Skill Tester

## Description
A testing framework for Claude Code skills that prevents context bleeding between Claude and skills. Provides isolated skill execution with clear entry/exit commands and session management.

## Purpose
When developing and testing skills, you need:
1. **Isolation**: Skills should run independently without Claude interfering
2. **Easy switching**: Quick return to Claude for debugging/improvements
3. **Session tracking**: Save and replay test sessions
4. **Multi-skill testing**: Test any skill in your workspace

## Core Principles

**CRITICAL - Strict Context Isolation:**
- Once a skill test session starts, ONLY the tested skill responds
- Claude (main assistant) NEVER responds during an active skill session
- ALL user messages go directly to the tested skill until exit
- Exit commands are the ONLY way to return to Claude

**Exit Commands:**
User can type any of these to exit skill and return to Claude:
- `:exit`
- `:back`
- `:claude`
- `:stop`
- `:quit`

When exit command is detected, immediately terminate skill session and return to Claude.

## Workflow

### Step 1: Skill Selection
Ask user which skill to test:
```
Available skills:
1. coe-infra-deploy-aws
2. [other skills in .claude/skills/]

Which skill would you like to test? (enter name or number)
```

If only one skill exists besides skill-tester, offer to use it directly.

### Step 2: Load Skill Definition
Read the skill.md file from `.claude/skills/<skill-name>/skill.md`

Parse the skill:
- Extract description
- Extract workflow steps
- Extract any special instructions

### Step 3: Session Configuration
Ask user:
```
Skill Tester Configuration:

Skill: <skill-name>
Description: <first 100 chars>

Options:
1. Start fresh test session
2. Load previous session (if exists)
3. Debug mode (show skill prompt interpretation)

Your choice?
```

### Step 4: Initialize Test Session
Create session state:
```json
{
  "session_id": "<timestamp>",
  "skill_name": "<skill-name>",
  "started_at": "<ISO timestamp>",
  "conversation": [],
  "debug_mode": false,
  "status": "active"
}
```

Display banner:
```
╔══════════════════════════════════════════════════════════╗
║  SKILL TEST SESSION ACTIVE                               ║
║  Skill: <skill-name>                                     ║
║  Session ID: <session_id>                                ║
║                                                           ║
║  You are now talking to the skill, NOT Claude            ║
║  Type :exit, :back, or :claude to return to Claude       ║
╚══════════════════════════════════════════════════════════╝

<skill now begins its workflow>
```

### Step 5: Skill Execution Loop
**THIS IS THE CRITICAL ISOLATION PHASE:**

**Rules:**
1. Load the skill's prompt into context as if YOU ARE that skill
2. Follow the skill's workflow EXACTLY as written
3. Respond ONLY as the skill would respond
4. Do NOT break character or respond as Claude
5. Do NOT explain what you're doing - just BE the skill
6. Check EVERY user message for exit commands FIRST
7. If exit command detected, terminate immediately

**On each user message:**
```
IF message matches [:exit, :back, :claude, :stop, :quit]:
  → Go to Step 6 (Exit Session)
ELSE:
  → Process message according to skill's workflow
  → Record in session conversation log
  → Continue as skill
```

**Debug Mode (if enabled):**
After each skill response, add small footer:
```
[DEBUG] Skill Step: <current step number> | Waiting for: <expected input>
```

### Step 6: Exit Session
When exit command received:

1. Save session to `.claude/test-sessions/<skill-name>-<session_id>.json`
2. Display exit banner:
```
╔══════════════════════════════════════════════════════════╗
║  SKILL TEST SESSION ENDED                                ║
║  Session saved to: .claude/test-sessions/<file>          ║
║  Duration: <duration>                                    ║
║  Messages exchanged: <count>                             ║
╚══════════════════════════════════════════════════════════╝

You are now back with Claude (main assistant).

Session Summary:
- Skill tested: <skill-name>
- Status: <completed/interrupted>
- Test coverage: <which steps were reached>

What would you like to do?
1. Review session transcript
2. Test the skill again
3. Modify the skill and retest
4. Test a different skill
5. Exit tester
```

3. Return full control to Claude (main assistant)

### Step 7: Post-Session Actions
Offer options:
- **Review Transcript**: Show full conversation log with annotations
- **Retest**: Start new session with same skill
- **Modify & Retest**: Open skill.md for editing, then retest
- **Compare Sessions**: Load and compare multiple test sessions
- **Export Report**: Generate markdown report of test session

## Session Management

### Saving Sessions
Auto-save to: `.claude/test-sessions/<skill-name>-<timestamp>.json`

Format:
```json
{
  "session_id": "20250319-143022",
  "skill_name": "coe-infra-deploy-aws",
  "started_at": "2025-03-19T14:30:22Z",
  "ended_at": "2025-03-19T14:35:18Z",
  "status": "completed",
  "conversation": [
    {
      "timestamp": "2025-03-19T14:30:25Z",
      "role": "skill",
      "content": "Environment Type? Staging or Production",
      "step": 1
    },
    {
      "timestamp": "2025-03-19T14:30:30Z",
      "role": "user",
      "content": "Production"
    },
    ...
  ],
  "metadata": {
    "total_messages": 24,
    "steps_completed": 8,
    "exit_reason": "user_command",
    "exit_command": ":exit"
  }
}
```

### Loading Previous Sessions
When user selects "Load previous session":
1. List available sessions for the skill
2. User selects session
3. Display transcript
4. Offer to:
   - Continue from where it left off
   - Start fresh with same inputs
   - Just review and exit

## Context Bleeding Prevention

**How This Prevents Context Bleeding:**

**Problem 1: Claude responds during skill session**
- Solution: Step 5 execution loop has STRICT role adherence
- Claude never "thinks" during skill execution
- All responses are generated AS the skill

**Problem 2: No clear way to exit skill**
- Solution: Exit commands (`:exit`, `:back`, etc.) checked on EVERY message
- Explicit session termination with banner

**Problem 3: Confusing context switches**
- Solution: Clear visual banners when entering/exiting
- Session state tracking
- Explicit "you are now talking to X" messages

**Example of Proper Isolation:**

```
User: [starts skill-tester, selects coe-infra-deploy-aws]

Skill Tester:
╔══════════════════════════════════════════════════════════╗
║  SKILL TEST SESSION ACTIVE                               ║
║  You are now talking to: coe-infra-deploy-aws           ║
║  Type :exit to return to Claude                          ║
╚══════════════════════════════════════════════════════════╝

[NOW RESPONDING AS SKILL - NOT AS CLAUDE]

Environment Type? Staging or Production

User: Production

[STILL AS SKILL]
Project Name? (e.g., "coe-api", "payment-service")

User: Actually, I want to modify the skill to add a new question

[STILL AS SKILL - DO NOT BREAK CHARACTER]
I need explicit values for each configuration parameter. Please provide the project name (e.g., "coe-api", "payment-service")

User: :exit

[EXIT DETECTED - TERMINATE SKILL SESSION]

╔══════════════════════════════════════════════════════════╗
║  SKILL TEST SESSION ENDED                                ║
╚══════════════════════════════════════════════════════════╝

[NOW RESPONDING AS CLAUDE - MAIN ASSISTANT]

You're back with Claude. I see you wanted to modify the skill to add a new question. Would you like me to:
1. Open the skill.md file for editing
2. Discuss what question you want to add
3. Start a new test session after modifications
```

## Important Rules

**NEVER during active skill session:**
- Break the 4th wall ("As the skill, I should ask...")
- Explain what the skill is doing ("The skill is now at step 3...")
- Respond as Claude ("Let me help you with that...")
- Offer to modify the skill mid-session
- Provide meta-commentary

**ALWAYS during active skill session:**
- Respond exactly as the skill would
- Follow the skill's workflow precisely
- Check for exit commands before processing
- Stay in character as the skill

**Session Boundaries:**
- Entry: Clear banner + "You are now talking to SKILL"
- Exit: Clear banner + "You are now back with Claude"
- No ambiguity about who is responding

## Testing Multiple Skills

When user wants to test multiple skills:
1. Exit current session properly
2. Return to Claude
3. Start new test session with different skill
4. Each session is independent

Can compare sessions across skills using session replay feature.

## Files and Directories

**Created by skill-tester:**
- `.claude/test-sessions/` - Session recordings
- `.claude/test-sessions/<skill-name>-<timestamp>.json` - Individual sessions

**Read by skill-tester:**
- `.claude/skills/*/skill.md` - Skill definitions
- `.claude/test-sessions/*.json` - Previous sessions

**Never modifies:**
- Skill definitions (read-only during testing)
- Any project files

## Quick Start Examples

**Example 1: Basic Testing**
```
User: Test coe-infra-deploy-aws skill
Tester: [loads skill, shows banner]
Skill: Environment Type?
User: Staging
Skill: Project Name?
User: :exit
Tester: [saves session, returns to Claude]
```

**Example 2: Debug Mode**
```
User: Test coe-infra-deploy-aws with debug mode
Tester: [loads skill with debug mode enabled]
Skill: Environment Type? Staging or Production
[DEBUG] Step 1 | Waiting for: staging|production
User: Production
Skill: Project Name?
[DEBUG] Step 1 | Waiting for: project name (lowercase, 3-30 chars)
```

**Example 3: Iterative Development**
```
User: Test my skill
[... testing ...]
User: :exit
Tester: Back with Claude. What would you like to do?
User: Modify the skill to add validation
Claude: [helps modify skill.md]
User: Test the skill again
Tester: [loads updated skill, starts new session]
```

## Success Criteria

Skill tester is working correctly when:
1. User can test skills without Claude interfering
2. Exit commands immediately return to Claude
3. Session boundaries are crystal clear
4. Sessions are saved and can be replayed
5. User can easily iterate: test → modify → retest
6. No confusion about who is responding (skill vs Claude)

## Troubleshooting

**Problem: Claude still responding during skill session**
- Check: Are you following the execution loop strictly?
- Check: Are you maintaining role as the skill?
- Fix: Re-read skill definition and respond ONLY as skill

**Problem: Exit commands not working**
- Check: Are you checking EVERY user message for exit commands?
- Check: Are you checking BEFORE processing the message?
- Fix: Add exit command check as first step in message handling

**Problem: User confused about context**
- Check: Are banners displaying correctly?
- Check: Are you explicitly stating who is responding?
- Fix: Add more explicit "You are talking to SKILL" reminders

**Problem: Session not saving**
- Check: Does .claude/test-sessions/ directory exist?
- Fix: Create directory before saving

## Implementation Notes

**For the skill-tester itself:**
- This is a meta-skill that wraps other skills
- It's both a skill AND a testing framework
- When running, you ARE the skill being tested
- When exited, you return control to Claude

**Recursion note:**
- skill-tester should not test itself
- If user tries to test skill-tester, politely decline and explain it's a meta-skill
