# Skill Tester

Test and debug Claude Code skills in an isolated environment with clear context boundaries.

## Problem Solved

When developing skills, you often face:
- **Context bleeding**: Claude responds instead of your skill
- **No clear exit**: Hard to switch back to Claude mid-session
- **Difficult iteration**: Can't easily test → modify → retest

Skill Tester solves all of these by creating a strict sandbox for skill testing.

## Quick Start

### Start Testing a Skill
```
Test my skill
```
or
```
Test coe-infra-deploy-aws skill
```

### Exit Back to Claude
During any test session, type:
- `:exit`
- `:back`
- `:claude`
- `:stop`
- `:quit`

## Features

### 1. Strict Isolation
When testing, ONLY the skill responds. Claude never interferes.

### 2. Clear Context Boundaries
Visual banners show exactly when you're talking to a skill vs. Claude:
```
╔══════════════════════════════════════════════════════════╗
║  SKILL TEST SESSION ACTIVE                               ║
║  You are now talking to: your-skill                      ║
║  Type :exit to return to Claude                          ║
╚══════════════════════════════════════════════════════════╝
```

### 3. Session Recording
Every test session is automatically saved to `.claude/test-sessions/` with full conversation history.

### 4. Debug Mode
See which step the skill is on and what it's expecting:
```
Skill: Environment Type? Staging or Production
[DEBUG] Step 1 | Waiting for: staging|production
```

### 5. Session Replay
Load and review previous test sessions, continue where you left off, or compare different test runs.

## Workflow

### Basic Testing Flow
1. **Start tester**: "Test my skill"
2. **Select skill**: Choose from available skills
3. **Test**: Interact with the skill
4. **Exit**: Type `:exit` to return to Claude
5. **Iterate**: Modify skill, test again

### Development Iteration
```
Test skill → :exit → Modify skill.md → Test again → :exit → Deploy
```

## Usage Examples

### Example 1: Basic Test
```
You: Test coe-infra-deploy-aws skill

Tester: [Shows available skills, loads selected one]

╔═══════════════════════════════════════════════╗
║  SKILL TEST SESSION ACTIVE                    ║
╚═══════════════════════════════════════════════╝

Skill: Environment Type? Staging or Production

You: Production

Skill: Project Name?

You: :exit

╔═══════════════════════════════════════════════╗
║  SKILL TEST SESSION ENDED                     ║
║  Session saved                                ║
╚═══════════════════════════════════════════════╝

Claude: You're back with Claude. What would you like to do?
```

### Example 2: Debug Mode
```
You: Test my skill with debug mode

Tester: [Loads skill with debug enabled]

Skill: Which cloud provider?
[DEBUG] Step 1 | Waiting for: AWS|DigitalOcean

You: AWS

Skill: Select region
[DEBUG] Step 2 | Waiting for: valid AWS region code
```

### Example 3: Iterative Development
```
You: Test my skill
[... discover issue during testing ...]
You: :exit

Claude: Back with Claude. How can I help?

You: The skill should validate the region input better

Claude: [Opens skill.md and adds validation]

You: Test the skill again
[... test with improved validation ...]
```

## Exit Commands

Type any of these during a test session to immediately return to Claude:

| Command | Effect |
|---------|--------|
| `:exit` | Exit and save session |
| `:back` | Return to Claude |
| `:claude` | Switch to Claude |
| `:stop` | Stop testing |
| `:quit` | Quit test session |

All commands save the session automatically.

## Session Management

### Automatic Saving
Sessions save to: `.claude/test-sessions/<skill-name>-<timestamp>.json`

Contains:
- Full conversation history
- Timestamps
- Step progression
- Exit reason

### Loading Previous Sessions
```
You: Test coe-infra-deploy-aws skill

Tester: Found 3 previous sessions. Load one?
1. 2025-03-19 14:30 (completed, 24 messages)
2. 2025-03-19 12:15 (interrupted, 8 messages)
3. 2025-03-18 16:45 (completed, 31 messages)

Your choice? (or 'new' for fresh session)
```

### Session Review
After exiting, review what was covered:
```
Session Summary:
- Duration: 5m 12s
- Messages: 24
- Steps completed: 8 of 16
- Status: Interrupted by user

Test coverage:
✓ Initial questions (Step 1)
✓ Management node config (Step 2)
✓ App node config (Step 3)
⚠ Stopped before RDS configuration
```

## How It Prevents Context Bleeding

### Problem 1: Claude Responds During Skill Session
**Solution**: Strict role adherence in execution loop
- Tester loads skill definition
- Responds ONLY as that skill
- Never breaks character

### Problem 2: No Clear Exit Path
**Solution**: Multiple exit commands checked on every message
- Commands work from anywhere in the conversation
- Immediate session termination
- Clear visual feedback

### Problem 3: Confusing Context Switches
**Solution**: Visual boundaries and explicit state
- Banners on entry/exit
- "You are now talking to X" messages
- Session state tracking

## Best Practices

### For Skill Development
1. **Test early and often**: Catch issues before they compound
2. **Use debug mode**: See exactly what the skill is thinking
3. **Save sessions**: Compare behavior before/after changes
4. **Test edge cases**: Try invalid inputs, unexpected flows

### For Testing
1. **One skill at a time**: Keep sessions focused
2. **Use exit commands**: Don't try to break character
3. **Review sessions**: Learn from conversation patterns
4. **Iterate quickly**: test → :exit → modify → test

### For Collaboration
1. **Share sessions**: Export session JSON for others to review
2. **Document issues**: Session transcripts show exact problems
3. **Compare approaches**: Test different skill versions side-by-side

## Technical Details

### Directory Structure
```
.claude/
├── skills/
│   ├── skill-tester/
│   │   ├── skill.md           # Tester implementation
│   │   └── README.md          # This file
│   └── your-skill/
│       └── skill.md           # Your skill being tested
└── test-sessions/             # Created by tester
    ├── your-skill-20250319-143022.json
    ├── your-skill-20250319-151145.json
    └── ...
```

### Session File Format
```json
{
  "session_id": "20250319-143022",
  "skill_name": "your-skill",
  "started_at": "2025-03-19T14:30:22Z",
  "ended_at": "2025-03-19T14:35:18Z",
  "status": "completed",
  "conversation": [
    {
      "timestamp": "2025-03-19T14:30:25Z",
      "role": "skill",
      "content": "First question?",
      "step": 1
    },
    {
      "timestamp": "2025-03-19T14:30:30Z",
      "role": "user",
      "content": "Answer"
    }
  ],
  "metadata": {
    "total_messages": 24,
    "steps_completed": 8,
    "exit_reason": "user_command",
    "exit_command": ":exit"
  }
}
```

## Troubleshooting

### Claude still responds during testing
- Restart the test session
- Ensure skill.md is properly formatted
- Check that tester is loaded correctly

### Exit commands not working
- Try different exit command (`:exit`, `:back`, etc.)
- Commands are case-sensitive, use lowercase
- Make sure you're in an active test session

### Session not saving
- Check `.claude/test-sessions/` directory exists
- Verify write permissions
- Sessions save even if Claude encounters an error

### Can't find my skill
- Ensure skill is in `.claude/skills/<skill-name>/skill.md`
- Check skill.md file exists and is readable
- Try listing skills: "List available skills"

## Advanced Usage

### Compare Multiple Sessions
```
You: Compare my last 3 test sessions for coe-infra-deploy-aws

Tester: [Loads and analyzes sessions]

Session comparison:
- Session 1: Stopped at step 3, 12 messages
- Session 2: Stopped at step 5, 18 messages
- Session 3: Completed, 31 messages

Common issue: Database password validation triggered in all sessions
Improvement: Sessions getting longer → skill flow improving
```

### Export Test Report
```
You: Export test report for today's sessions

Tester: [Generates markdown report]

Created: test-report-20250319.md
- Total sessions: 8
- Skills tested: 2
- Issues found: 4
- Total test time: 1h 23m
```

### Regression Testing
Keep successful session JSONs in version control. Load and replay to ensure skill changes don't break existing flows.

## FAQ

**Q: Can I test the skill-tester itself?**
A: No, skill-tester is a meta-skill. Testing it would create infinite recursion.

**Q: Do sessions persist across Claude restarts?**
A: Yes! Sessions are saved to disk and reload automatically.

**Q: Can I edit sessions?**
A: Sessions are read-only for integrity. Create a new test session instead.

**Q: What if my skill has bugs?**
A: That's what the tester is for! Debug mode shows exactly where things go wrong.

**Q: Can I test multiple skills in one session?**
A: No, one skill per session. Exit and start a new session for different skills.

## Next Steps

1. **Test your first skill**: `Test coe-infra-deploy-aws skill`
2. **Try debug mode**: `Test my skill with debug mode`
3. **Review a session**: `Show me my last test session`
4. **Iterate**: Test → Exit → Modify → Test

## Support

- **Skill Tester Issues**: Check this README and troubleshooting section
- **Skill Development**: See `.claude/README.md` for skill creation guide
- **Claude Code Help**: Use `/help` or visit [docs](https://claude.com/claude-code)
