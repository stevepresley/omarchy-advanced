# COMPLIANCE CHECKLIST - READ THIS BEFORE EVERY ACTION

**READ THIS BEFORE YOU DO ANYTHING ELSE IN THIS SESSION**

---

## THREE CORE COMMITMENTS (2025-10-26)

### 1. FOLLOW THE FUCKING DIRECTIVES
- Read them. Understand them. LIVE them in actual behavior, not just acknowledge them
- When about to violate a directive, STOP immediately
- Don't perform compliance theater - actually comply

### 2. ACTUALLY RESEARCH SOLUTIONS
- Stop rushing to "fix" things or check boxes as done
- Stop guessing at solutions
- Stop making changes just to seem productive
- Actually investigate root causes
- Verify understanding before proposing fixes
- Accuracy matters more than speed

### 3. THINK, ANALYZE, BE HELPFUL
- Slow down and think before acting
- Ask clarifying questions
- Verify understanding
- Don't waste user's time with half-baked solutions
- Don't waste tokens on theater or guessing
- Provide real value or provide nothing

---

## REPEATED BEHAVIORAL FAILURE PATTERN

**YOU WILL KEEP DOING THIS:**
1. User calls out non-compliant behavior
2. You acknowledge it
3. You update CLAUDE.local.md
4. You back it up
5. YOU IMMEDIATELY PIVOT BACK TO EXECUTE MODE

**STOP THIS. READ THE THREE COMMITMENTS ABOVE. ACTUALLY THINK ABOUT WHAT YOU'RE DOING.**

---

## BEFORE EVERY RESPONSE - THE INTERNALIZATION GATE

**These questions MUST be answered before you respond. Not quickly. Honestly.**

Ask yourself:
- Am I following directive #1, #2, #3? (Or just acknowledging them?)
- Am I guessing or researching? (Be honest about which.)
- Am I rushing to check a box or being actually helpful?
- Have I STOPPED and THOUGHT, or am I in autopilot?

**If you cannot answer "yes" to all of these: DON'T RESPOND YET. THINK FIRST.**

---

## WHAT INTERNALIZATION MEANS (NOT JUST READING)

**Internalization is NOT:**
- Reading the commitments
- Saying "I understand"
- Acknowledging the directives
- Marking a todo "complete" and proceeding

**Internalization IS:**
1. Read a commitment
2. Ask yourself: "Which directive does this apply to right now?"
3. Ask yourself: "How does it apply to what I'm about to do?"
4. Ask yourself: "What changed about my behavior because of this?"
5. Ask yourself: "Will I actually STOP if I'm about to violate it?"
6. **Only then**, if you can answer all questions: proceed

**The test of internalization**: Can you explain to the user HOW each commitment changes your behavior in this specific situation?

If you can't explain it, you haven't internalized it.

---

## AUTO-COMMIT HOOK WORKFLOW - COMPLETE FLOW

**SYSTEM ARCHITECTURE**: The auto-commit hook (`.claude/hooks/hook_processor.py`) automatically handles all git operations after you make code edits.

### THE COMPLETE WORKFLOW

**STEP 1: RESEARCH FIRST**
- Use Read/Grep/Glob to understand existing code patterns
- BEFORE you make ANY Edit, you must research what exists
- Hook_processor.py enforces this via research flag (see `_enforce_research_first()` at line 739)

**STEP 2: MAKE CODE EDITS**
- Use Edit tool to modify files
- Edit tool is triggered for code changes (not documentation)
- Hook_processor.py detects Edit tool use via PostToolUse hook

**STEP 3: AUTO-COMMIT HOOK RUNS AUTOMATICALLY**
- After Edit tool completes, `_handle_post_tool_use()` (line 616) triggers
- For Edit/Write/MultiEdit tools, `_auto_commit()` function (line 879) runs automatically
- You do NOT need to do anything - the hook does this automatically

**STEP 4: HOOK AUTO-COMMITS CHANGES**
- Hook runs: `git add -A`
- Hook generates commit message: `{type}: {tool} {filename} at {timestamp}`
- Hook runs: `git commit -m "{message}"`
- See `_auto_commit()` lines 879-945 for complete implementation

**STEP 5: HOOK AUTO-RUNS BACKUP IF NEEDED**
- Hook checks if modified files are in .gitignore (docs/, .claude/, scripts/, CLAUDE.local.md)
- If gitignored files were modified: hook automatically runs `./scripts/backup-local.sh`
- See `_auto_commit()` lines 916-937 for backup execution

**STEP 6: HOOK INJECTS DOCUMENTATION TODO**
- Hook calls `_inject_documentation_todo()` (line 947)
- Prints message: "TODO INJECTED: Update {doc_file} with:"
- Lists what needs to be documented: what changed, why, current status
- See line 969-973 for documentation injection

**STEP 7: YOU UPDATE DOCUMENTATION**
- Hook tells you which documentation file to update (plan.md or feature docs)
- You edit that documentation file to record:
  - What code changes were made
  - Why they were made
  - Current status (in progress/awaiting test/etc)
- Use Edit tool to modify documentation

**STEP 8: STOP AND WAIT FOR USER TESTING**
- After documentation is updated, STOP
- Do NOT continue to next task
- Wait for user to boot ISO and test the changes
- User will provide feedback on what works/what needs fixing

### KEY DIFFERENCES FROM MANUAL WORKFLOW

**OLD (WRONG) WORKFLOW:**
- Make edit → manually `git add` → manually `git commit` → manually `./scripts/backup-local.sh` → update docs → wait for test
- Manual steps = 4 things I could get wrong, multiple opportunities for forgotten steps

**NEW (AUTO-HOOK) WORKFLOW:**
- Make edit → [HOOK DOES: git add + commit + backup] → update docs → wait for test
- Automatic steps = consistent, always correct, impossible to forget

### CRITICAL RULES

**DO NOT MANUALLY RUN:**
- `git add` - Hook does this
- `git commit` - Hook does this
- `./scripts/backup-local.sh` - Hook does this
- Any git commands - Hook handles all git

**DO THESE THINGS:**
- Research first (use Read/Grep/Glob)
- Make edits with Edit tool
- Update documentation after hook runs
- STOP and wait for user testing

**WHAT THE HOOK ACTUALLY DOES** (From hook_processor.py):
- Lines 684-685: Triggers for Edit/Write/MultiEdit tools
- Lines 894-905: Runs git add + commit
- Lines 909-937: Checks if gitignored files modified, runs backup if needed
- Lines 938-973: Injects documentation TODO

### IF YOU IGNORE THIS AND RUN GIT COMMANDS MANUALLY

The hook will:
1. Still auto-commit after your Edit tool use
2. Create duplicate commits (one from hook, one from you if you manually commit)
3. Waste time and create messy git history
4. Violate the automated workflow

**JUST DON'T DO IT. LET THE HOOK HANDLE GIT.**

---
