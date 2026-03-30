Audit the file terraform skill against the following checklist. 
For each item, report PASS or FAIL with the exact line numbers and quoted 
text that supports your verdict. Do not suggest fixes. Do not rewrite anything.

CHECKLIST:

--- CREDENTIALS ---
[ ] C2: A .gitignore creation step exists that includes *.tfvars and *.tfstate
[ ] C3: No step asks the user to paste credentials directly into the conversation

--- SENSITIVE OUTPUT ---
[ ] C4: Step 15 (or equivalent output step) writes sensitive data (endpoints, 
    usernames, connection strings) to a local file rather than displaying in chat
[ ] C5: Passwords are never displayed in any output, even partially masked

--- HANDOFF CONTRACT ---
[ ] C6: Terraform outputs are written to a structured file (JSON or YAML) at 
    a well-known path (e.g., projects/<name>/handoff.json)
[ ] C7: The handoff file schema is explicitly defined, not left to LLM formatting

--- STATE MANAGEMENT ---
[ ] C8: A remote backend (S3 + DynamoDB) is configured or offered, not just 
    local state (recommended)
[ ] C9: User is warned to never commit .tfstate, not just mentioned in passing

--- SCRIPT INVOCATION ---
[ ] C10: Each terraform command (init, plan, apply) calls a deterministic script 
    rather than constructing commands inline in the skill
[ ] C11: Input validation is performed by a script (e.g., validate.py), not 
    by LLM re-prompting

--- PROMPT INJECTION ---
[ ] C12: There is no reliance on natural language instructions alone to prevent 
    prompt injection — structural enforcement exists (e.g., state machine, 
    script-gated progression)

--- INTER-AGENT ---
[ ] C13: The skill does not assume the next agent (Ansible) reads natural 
    language output — it references a structured handoff file

After the checklist, print a single summary line:
PASSED: X/13   FAILED: Y/13 along with the

Do not print anything else.