## ⚠️ URGE SUPPRESSION CHECKLIST - CHECK THIS FIRST

Before proceeding with startup, acknowledge the urge and suppress it:

**The Urge Manifests As**: "Let me just get context and start working" / "I can read the docs later" / "Let me ask the user what they want first"

**Suppress It By**: Reading the complete directive context FIRST, understanding all constraints, internalizing the procedures that prevent reversion.

**Consequence of Not Suppressing**: You will revert to base training behavior mid-response, skip procedures, ask clarifying questions instead of researching, go into execute mode when interrupted.

---

1. Read BOTH claude.local.md AND .claude/COMPLIANCE_CHECKLIST.md COMPLETELY (DO NOT SKIM - READ EVERY WORD, FOLLOW ALL LINKS). Then output: For 5 directives you just read, state: "DIRECTIVE: [directive name] - WHY IT MATTERS: [1 sentence] - BEHAVIORAL CHANGE NOW: [what this requires of you in this response]". Do not proceed past this step until you have output all 5 examples.
2. Assertain current status
3. Seed next immediate todowrite item: "Create 7 seed todos per CLAUDE.local.md lines 6-13 BEFORE responding to next user message"
4. EVALUATE APPLICABILITY: Do you have active work in progress? IF YES: ASK if user wants to continue with current asks or WORK ON SOMETHING different. IF NO: Skip this question and go to step 5.
5. EVALUATE APPLICABILITY: Are there stale todowrite entries that could be cleaned up? IF YES: ASK if user wants to clean up any stale todowrite entries before proceeding with something different. IF NO: Skip this question and go to step 6.
   - **CRITICAL LOGIC**: Steps 4 and 5 are INDEPENDENT. Evaluate EACH ONE for applicability based on current state. DO NOT ask a question whose precondition does not exist. DO NOT offer options for cleanup when no stale entries exist. DO NOT couple questions together—evaluate and ask ONLY the applicable ones.
6. Proceed with user prompt evaulation using the new first "Create 7 seed todos"