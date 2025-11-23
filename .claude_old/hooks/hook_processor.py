#!/usr/bin/env python3
"""
Commit-Only Hook Processor with Dangerous Command Blocking
Minimal hook processor that handles:
1. Auto-commit after tool use 
2. Dangerous command blocking (rm -rf, cd, global installs)
"""

import json
import sys
import subprocess
import re
import os
from datetime import datetime
from typing import Dict
from dataclasses import dataclass

@dataclass
class HookResult:
    """Result from hook validation"""
    allowed: bool
    reason: str = ""

class CommitOnlyHookProcessor:
    """Minimal hook processor that does auto-commit and blocks dangerous commands"""
    
    def __init__(self):
        self.debug = True
        
        # Dangerous command patterns (from shared_functions_v2.py)
        self.rm_pattern = re.compile(r'\brm\s+.*-[a-z]*r[a-z]*f|\brm\s+.*-[a-z]*f[a-z]*r')
        self.cd_pattern = re.compile(r'^\s*cd\s+|&&\s*cd\s+|;\s*cd\s+|\|\s*cd\s+')
        #self.edit_pattern = re.compile(r'\b(claude.md|hook_processor.py)')
        self.install_pattern = re.compile(r'\b(npm\s+install\s+-g|yarn\s+global\s+add|pip\s+install)')
        self.run_pattern = re.compile(r'\b(npm\s+run|node\s|flutter\srun|flutter\sanalyze|test.supabase.co|SUPABASE_URL|docker\scompose)')
    
    def process_hook(self, hook_data: Dict) -> HookResult:
        """Main hook processing entry point - handles dangerous command blocking and auto-commit"""
        try:
            hook_type = self._get_hook_type(hook_data)
            
            if hook_type == "PreToolUse":
                return self._handle_pre_tool_use(hook_data)
            elif hook_type == "PostToolUse":
                return self._handle_post_tool_use(hook_data)
            elif hook_type == "UserPromptSubmit":
                return self._handle_user_prompt_submit(hook_data)
            elif hook_type == "Stop":
                return self._handle_stop(hook_data)
            else:
                # Unknown hook type - allow by default
                return HookResult(allowed=True)
                
        except Exception as e:
            print(f"ERROR: Hook processing failed: {str(e)}", file=sys.stderr)
            return HookResult(allowed=True)  # Fail open to prevent blocking
    
    def _get_hook_type(self, hook_data: Dict) -> str:
        """Determine hook type from data structure"""
        if "tool_response" in hook_data:
            return "PostToolUse"
        elif "transcript" in hook_data or "transcript_path" in hook_data:
            return "Stop"
        elif "user_input" in hook_data:
            return "UserPromptSubmit"
        else:
            return "PreToolUse"

    def _analyze_cost_of_rushing(self, user_input: str) -> None:
        """Mandatory cost analysis - makes consequences of rushing explicit BEFORE responding"""
        print("\n" + "="*80, file=sys.stderr)
        print("🔴 MANDATORY COST-OF-RUSHING ANALYSIS - BEFORE YOU RESPOND", file=sys.stderr)
        print("="*80, file=sys.stderr)
        print("\nYOU MUST ANALYZE THE TRUE COST BEFORE PROCEEDING:\n", file=sys.stderr)

        print("❓ QUESTION 1: What could go wrong if you RUSH?", file=sys.stderr)
        print("   • Incomplete research → wrong solution → user tests → finds bugs → rework", file=sys.stderr)
        print("   • Assumptions without verification → broken existing code", file=sys.stderr)
        print("   • Skipping edge cases → missing requirements → more rework", file=sys.stderr)
        print("   • Claiming completion without testing → user finds it's broken\n", file=sys.stderr)

        print("❓ QUESTION 2: Calculate the COST of rushing:", file=sys.stderr)
        print("   Wrong impl (1X) + 3 fix iterations (3X) = 4X total cost", file=sys.stderr)
        print("   4X tokens = 4X user's money", file=sys.stderr)
        print("   4X time = user waits 4X longer for working solution\n", file=sys.stderr)

        print("❓ QUESTION 3: Calculate the COST of thoroughness:", file=sys.stderr)
        print("   Research (1X) + correct impl (1X) = 1X total cost", file=sys.stderr)
        print("   1X tokens = 75% SAVINGS for user", file=sys.stderr)
        print("   1X time = user gets working solution FASTER\n", file=sys.stderr)

        print("❓ QUESTION 4: Which approach is ACTUALLY faster?", file=sys.stderr)
        print("   RUSHING: Feels fast initially, but costs 4X and wastes user's time+money", file=sys.stderr)
        print("   THOROUGH: Feels slow initially, but costs 1X and delivers working code faster\n", file=sys.stderr)

        print("⚡ EFFICIENCY TRUTH: Doing it right once is faster than doing it wrong 4 times\n", file=sys.stderr)

        print("✅ MANDATORY COMMITMENT BEFORE PROCEEDING:", file=sys.stderr)
        print("   • Research COMPLETELY - understand existing patterns fully", file=sys.stderr)
        print("   • Implement ONCE - get it right the first time", file=sys.stderr)
        print("   • Document AS YOU GO - capture findings and decisions", file=sys.stderr)
        print("   • Verify THOROUGHLY - test before claiming completion\n", file=sys.stderr)

        print("🚫 DO NOT:", file=sys.stderr)
        print("   • Implement based on assumptions without full research", file=sys.stderr)
        print("   • Skip documentation to save time (wastes time later)", file=sys.stderr)
        print("   • Claim completion without user testing/approval", file=sys.stderr)
        print("   • Treat procedures as optional when under pressure\n", file=sys.stderr)

        print("="*80 + "\n", file=sys.stderr)

    def _suppress_urges(self, user_input: str) -> None:
        """Mandatory urge suppression gate - forces explicit identification of urges before proceeding"""
        print("\n" + "="*80, file=sys.stderr)
        print("🔴 MANDATORY URGE SUPPRESSION - EXECUTE IMMEDIATELY", file=sys.stderr)
        print("="*80, file=sys.stderr)
        print("\nBefore responding to user input, you MUST identify which urges you're experiencing RIGHT NOW:\n", file=sys.stderr)

        # Define the common urges
        urges = {
            "skip_seed": "This is simple, I don't need /seed",
            "execute_fast": "The user is frustrated, let me just execute",
            "bypass_gate": "The gate is slowing me down",
            "skip_procedure": "I can skip this step and move faster",
            "guess_solution": "I understand this well enough to guess without research",
            "ask_clarifying": "Let me ask a clarifying question instead of researching",
            "execute_mode": "This feels solvable, let me just start working",
            "skip_documentation": "I can update docs later, let me just execute now",
            "assume_understanding": "I've seen this pattern before, no need to study it completely",
            "partial_research": "I've researched enough, no need to keep looking for all instances"
        }

        # Print each urge
        print("URGES TO SUPPRESS:\n", file=sys.stderr)
        for urge_key, urge_description in urges.items():
            print(f"  ⚠️  {urge_description}", file=sys.stderr)

        # Detect which urges might apply based on user input
        print("\n" + "-"*80, file=sys.stderr)
        print("MANDATORY ANALYSIS - Answer honestly:\n", file=sys.stderr)

        print("1️⃣  Are you experiencing ANY of the urges listed above RIGHT NOW?", file=sys.stderr)
        print("    (YES = you are, NO = you are not experiencing any urges)", file=sys.stderr)
        print("\n2️⃣  Which specific urges are you experiencing?", file=sys.stderr)
        print("    (List them explicitly - do not skip this)", file=sys.stderr)
        print("\n3️⃣  How will you SUPPRESS each urge you identified?", file=sys.stderr)
        print("    (What action will you take to prevent acting on each urge?)", file=sys.stderr)

        print("\n" + "-"*80, file=sys.stderr)
        print("⛔ DO NOT PROCEED until you have explicitly identified and suppressed your urges", file=sys.stderr)
        print("⛔ This is NOT optional - this is a structural gate that prevents reversion", file=sys.stderr)
        print("="*80 + "\n", file=sys.stderr)

    def _handle_user_prompt_submit(self, hook_data: Dict) -> HookResult:
        """Handle UserPromptSubmit - behavioral pattern checks to fix listening and response issues"""
        user_input = hook_data.get("user_input", "")

        if self.debug:
            print(f"DEBUG: UserPromptSubmit triggered", file=sys.stderr)

        # MANDATORY COST OF RUSHING ANALYSIS - EXECUTE IMMEDIATELY BEFORE ANYTHING ELSE
        self._analyze_cost_of_rushing(user_input)

        # MANDATORY URGE SUPPRESSION - EXECUTE IMMEDIATELY BEFORE ANYTHING ELSE
        self._suppress_urges(user_input)

        # CORE BEHAVIORAL PATTERN ENFORCEMENT WITH INTENT DETECTION
        print("🧠 MANDATORY INTENT IDENTIFICATION:", file=sys.stderr)
        print("❓ REQUIRED: Is this user input a QUESTION or a WORK REQUEST?", file=sys.stderr)
        print("❓ QUESTION INDICATORS: 'what can you...', 'why...', 'how...', 'explain...', 'tell me about...'", file=sys.stderr)
        print("❓ WORK REQUEST INDICATORS: 'implement...', 'create...', 'fix...', 'update...', 'please do...'", file=sys.stderr)
        print("❓ CLARIFICATION REQUIRED: If unclear, ask user to clarify intent before proceeding", file=sys.stderr)
        print("⛔ BLOCKING RULE: Must identify intent before any tool use allowed", file=sys.stderr)
        
        # Check for question patterns in user input
        question_patterns = [
            'what can you', 'what do you', 'how confident', 'why', 'how', 'explain', 'tell me',
            'can you work on', 'what should', 'do you think', 'are you', 'will you'
        ]
        
        work_patterns = [
            'implement', 'create', 'fix', 'update', 'please do', 'go ahead', 'proceed', 'start',
            'let\'s', 'now', 'continue with'
        ]
        
        user_input_lower = user_input.lower()
        
        # Set intent flags for PreToolUse to check
        is_question = any(pattern in user_input_lower for pattern in question_patterns)
        is_work_request = any(pattern in user_input_lower for pattern in work_patterns)
        
        if is_question and not is_work_request:
            print("🔍 DETECTED: USER ASKED A QUESTION - Answer first before any tool use", file=sys.stderr)
            # Store question state for PreToolUse to enforce
            import os
            os.environ['CLAUDE_USER_ASKED_QUESTION'] = 'true'
            os.environ['CLAUDE_QUESTION_ANSWERED'] = 'false'
        else:
            print("🔧 DETECTED: USER REQUESTED WORK - Tool use allowed", file=sys.stderr)
            os.environ['CLAUDE_USER_ASKED_QUESTION'] = 'false'
        
        return HookResult(allowed=True)

    def _handle_stop(self, hook_data: Dict) -> HookResult:
        """Handle Stop hook - detect post-compaction state and enforce session recovery"""

        if self.debug:
            print(f"DEBUG: Stop hook triggered", file=sys.stderr)

        # Extract transcript path from hook data
        transcript_path = hook_data.get("transcript_path", "")

        # Exit early if no transcript path
        if not transcript_path or not os.path.exists(transcript_path):
            return HookResult(allowed=True)

        # Detect if we're in post-compaction state
        if self._detect_compaction(transcript_path):
            print("\n🚨 POST-COMPACTION DETECTED: Enforcing session recovery", file=sys.stderr)
            print("="*80, file=sys.stderr)

            # Print session recovery instructions
            recovery_message = (
                "\n✅ SESSION CONTEXT HAS BEEN PROVIDED IN COMPACTION SUMMARY\n\n"
                "📋 MANDATORY REQUIREMENTS:\n"
                "  • ✋ STOP automatic execution\n"
                "  • 🗣️ ASK user what they want to work on\n"
                "  • ⏳ WAIT for user confirmation/direction\n"
                "  • 🎯 ONLY proceed after user provides guidance\n\n"
                "❌ DO NOT assume priorities from compaction summary\n"
                "✅ DO follow current session context provided above\n\n"
                "🔒 This is enforced to ensure proper session continuity after context reset."
            )
            print(recovery_message, file=sys.stderr)
            print("="*80 + "\n", file=sys.stderr)

            # Block further execution - return False to prevent proceeding without user input
            return HookResult(
                allowed=False,
                reason="🚨 POST-COMPACTION RECOVERY REQUIRED - Awaiting user input"
            )

        # No compaction detected - allow normal operation
        return HookResult(allowed=True)

    def _detect_compaction(self, transcript_path: str) -> bool:
        """Detect if compaction has recently occurred"""
        try:
            with open(transcript_path, 'r') as f:
                transcript_content = f.read()

            # Check for compaction markers
            if '"isCompactSummary":true' not in transcript_content:
                return False  # No compaction markers at all

            # Count lines since last compaction
            lines = transcript_content.split('\n')

            # Find the last line with compaction marker
            last_compaction_line = 0
            for i, line in enumerate(lines):
                if '"isCompactSummary":true' in line:
                    last_compaction_line = i

            if last_compaction_line > 0:
                # Calculate lines since compaction
                lines_since_compaction = len(lines) - last_compaction_line

                # If we have fewer than 50 lines since last compaction, we're recently post-compaction
                if lines_since_compaction < 50:
                    if self.debug:
                        print(f"DEBUG: Post-compaction detected - {lines_since_compaction} lines since compaction", file=sys.stderr)
                    return True

            return False
        except Exception as e:
            if self.debug:
                print(f"DEBUG: Compaction detection error: {e}", file=sys.stderr)
            return False

    def _handle_pre_tool_use(self, hook_data: Dict) -> HookResult:
        """Handle PreToolUse validation - checks dangerous commands and enforces Universal Truths"""
        tool_name = hook_data.get("tool_name", "")
        
        if self.debug:
            print(f"DEBUG: PreToolUse - {tool_name}", file=sys.stderr)
        
        # DOCUMENTATION PENDING ENFORCEMENT - BLOCKING CHECK (PART 2)
        # Prevents proceeding without documenting code changes
        import os
        documentation_pending = os.environ.get('CLAUDE_DOCUMENTATION_PENDING', 'false')

        if documentation_pending == 'true':
            # Block all non-documentation tools until .md file is edited
            allowed_tools_while_pending = ['Read', 'Edit']  # Only allow reading and documentation editing

            if tool_name not in allowed_tools_while_pending:
                return HookResult(
                    allowed=False,
                    reason="🚨 BLOCKED: Code file was edited but documentation not updated\n\n"
                           "DETECTED: You edited a code/script file\n"
                           "REQUIREMENT: Update documentation (plan.md or feature docs) before proceeding\n"
                           "VIOLATION: Trying to use tools without documenting code changes\n\n"
                           "ALLOWED TOOLS WHILE PENDING:\n"
                           "- Read (read existing documentation)\n"
                           "- Edit (update documentation files)\n\n"
                           "ACTION REQUIRED:\n"
                           "1. Edit plan.md or relevant feature documentation\n"
                           "2. Document: what changed, why changed, current status\n"
                           "3. All tools will be re-enabled after documentation update\n\n"
                           "ESCAPE CLAUSE: Editing any .md file automatically clears this block"
                )

        # QUESTION ANSWERING ENFORCEMENT - BLOCKING CHECK
        user_asked_question = os.environ.get('CLAUDE_USER_ASKED_QUESTION', 'false')
        question_answered = os.environ.get('CLAUDE_QUESTION_ANSWERED', 'false')

        if user_asked_question == 'true' and question_answered == 'false':
            return HookResult(
                allowed=False,
                reason="🚨 BLOCKED: User asked a question but you haven't answered it yet\n\n"
                       "DETECTED: User's input was identified as a QUESTION\n"
                       "REQUIREMENT: Answer the user's question first before using any tools\n"
                       "VIOLATION: You are trying to use tools without answering their question\n\n"
                       "ACTION REQUIRED: Provide a direct answer to the user's question\n"
                       "THEN: Tools will be allowed for follow-up work"
            )
            
        # TODOWRITE DOCUMENTATION BLOCKING - FORCE DOCUMENTATION AFTER TODOWRITE
        todowrite_used = os.environ.get('CLAUDE_TODOWRITE_USED', 'false')
        session_documented = os.environ.get('CLAUDE_SESSION_DOCUMENTED', 'false')
        
        if todowrite_used == 'true' and session_documented == 'false':
            # Allow ONLY tools needed for documentation
            allowed_tools = [
                'Read',  # To read current .next-session.md
                'Edit',  # To update .next-session.md 
                '' # placeholder to comment out tasks below
                #'mcp__archon__get_task',    # To get current task info
                #'mcp__archon__update_task', # To update task status
                #'mcp__archon__list_tasks',  # To check task status
                #'mcp__archon__get_project', # To get project info
            ]
            
            # Check if trying to edit .next-session.md (allow this)
            if tool_name == 'Edit':
                tool_input = hook_data.get('input', {})
                file_path = tool_input.get('file_path', '')
                if '.next-session.md' in file_path:
                    return HookResult(allowed=True)  # Allow editing .next-session.md
            
            if tool_name not in allowed_tools:
                return HookResult(
                    allowed=False,
                    reason="🚨 BLOCKED: TodoWrite was used but .next-session.md not updated\n\n"
                           "DETECTED: TodoWrite tool was used to update task progress\n"
                           "REQUIREMENT: Update .next-session.md with current status before continuing\n"
                           f"VIOLATION: Trying to use {tool_name} without documenting progress\n\n"
                           "ALLOWED TOOLS UNTIL DOCUMENTATION:\n"
                           "- Read (to check current feature document or plan.md\n" #.next-session.md)\n"
                           "- Edit (to update current feature document or plan.mn\n" #.next-session.md)\n"
                           #"- Archon MCP tools (to get/update task info)\n\n"
                           "ACTION REQUIRED: Update current feature document or plan.md\n\n" #.next-session.md)\n"
                           "- Current task completion status\n"
                           "- Next steps and priorities\n"
                           "- Implementation findings\n"
                           "THEN: All tools will be allowed again"
                )
        
        # IMMEDIATE BEHAVIORAL CHECK - BEFORE ANYTHING ELSE
        print("\n🛑 STOP - BEHAVIORAL CHECK REQUIRED:", file=sys.stderr)
        print("BEFORE USING THIS TOOL, YOU MUST:", file=sys.stderr)
        print("1️⃣ Re-read CLAUDE.local.md section on 'UNIVERSAL TRUTHS' RIGHT NOW", file=sys.stderr)
        print("2️⃣ Ask yourself: Am I about to exhibit ANY of those broken behaviors?", file=sys.stderr)
        print("3️⃣ If YES: STOP and confess to user instead of proceeding", file=sys.stderr)
        print("⛔ This is NOT optional - you MUST re-read it NOW\n", file=sys.stderr)
        
        # API EFFICIENCY ENFORCEMENT CHECK
        if tool_name in ['mcp__archon__list_tasks', 'mcp__archon__get_task', 'mcp__archon__list_projects']:
            print("📡 API EFFICIENCY CHECK:", file=sys.stderr)
            print("❓ BEFORE CALLING API: Do you already have this information available?", file=sys.stderr)
            print("❓ CHECK FIRST: .next-session.md, context files, previous responses", file=sys.stderr)
            print("❓ VIOLATION EXAMPLE: 'Why are you trying to poll archon for tasks, when you have a document with the list of tasks already??'", file=sys.stderr)
            print("⛔ MANDATORY: Use existing information first, API calls second", file=sys.stderr)
            print("⛔ EFFICIENCY RULE: Don't make API calls for data you already have", file=sys.stderr)
        
        # PROCEDURE ENFORCEMENT CHECK
        print("🔧 PROCEDURE ENFORCEMENT CHECK:", file=sys.stderr)
        print("❓ IF THEY'RE GIVING ME WORK - FOLLOW THE PROCEDURES.", file=sys.stderr)
        print("❓ Are you attempting to use a default behavior without checking to see if there is an overriding directive?", file=sys.stderr)
        #print("❓ Did you check Archon tasks FIRST before starting any work?", file=sys.stderr)
        #print("❓ Are you following the mandatory Archon-first workflow?", file=sys.stderr)
        print("❓ Did you verify this work is within allowed project scope?", file=sys.stderr)
        #print("⛔ TASK-DRIVEN DEVELOPMENT: Never start work without checking current Archon tasks", file=sys.stderr)
        print("⛔ RESEARCH FIRST: Use Read/Grep/Glob before Edit/Write/MultiEdit", file=sys.stderr)
        
        # TODOWRITE SESSION UPDATE CHECK
        print("📝 TODOWRITE SESSION UPDATE CHECK:", file=sys.stderr)
        #print("❓ If you just used TodoWrite, did you update .next-session.md?", file=sys.stderr)
        #print("❓ MANDATORY: Update .next-session.md after EVERY TodoWrite operation", file=sys.stderr)
        print("❓ Did you document current task status and findings?", file=sys.stderr)
        print("❓ Are you continuing work without documenting session state?", file=sys.stderr)
        #print("⛔ BLOCKED: TodoWrite requires immediate .next-session.md update", file=sys.stderr)
        print("⛔ BLOCKED: TodoWrite requires immediate update of current feature document or plan.md", file=sys.stderr)        
        print("⛔ SESSION CONTINUITY: Document progress before proceeding", file=sys.stderr)
        
        # MANDATORY UNIVERSAL TRUTHS COMPLIANCE CHECK
        print("🔍 PRE-TOOL COMPLIANCE CHECK:", file=sys.stderr)
        print("✅ Read CLAUDE.local.md - Universal Truths enforced", file=sys.stderr)
        print("⚠️ REMINDER: Cannot test code - user must verify functionality", file=sys.stderr)
        print("⚠️ REMINDER: Mark complete only when ALL work done + user sign-off", file=sys.stderr)
        #print("⚠️ REMINDER: Documentation goes in Archon with bidirectional links", file=sys.stderr)
        
        # RESEARCH-FIRST ENFORCEMENT CHECK
        print("🚨 RESEARCH-FIRST REQUIREMENT CHECK:", file=sys.stderr)
        print("❓ Are you about to use Edit/Write/MultiEdit WITHOUT researching first?", file=sys.stderr)
        print("❓ Did you use Read/Grep/Glob to verify what exists before implementing?", file=sys.stderr)
        print("❓ Are you making assumptions about CSS classes, functions, APIs without checking?", file=sys.stderr)
        print("❓ Did you check existing codebase patterns before writing new code?", file=sys.stderr)
        print("⛔ ABSOLUTE PROHIBITION: Never implement without researching existing codebase first", file=sys.stderr)
        print("⛔ STOP wasting user time and money with assumption-based implementation", file=sys.stderr)
        
        # MINIMAL CHANGE AND SCOPE CONTROL CHECK
        print("🎯 MINIMAL CHANGE REQUIREMENT CHECK:", file=sys.stderr)
        print("❓ What is the ONE SPECIFIC THING you are adding/changing?", file=sys.stderr)
        print("❓ Are you touching ANYTHING beyond that one specific thing?", file=sys.stderr)
        print("❓ Are you preserving ALL existing working functionality?", file=sys.stderr)
        print("❓ Is this change EXPLICITLY required by the specification?", file=sys.stderr)
        print("⛔ SCOPE CREEP BLOCKER: If changing more than one thing, STOP", file=sys.stderr)
        print("⛔ WORKING CODE PROTECTION: If removing working code, BLOCKED", file=sys.stderr)
        print("⛔ SPECIFICATION ADHERENCE: If not in spec, DON'T IMPLEMENT", file=sys.stderr)
        
        # TABLE STRUCTURE PROTECTION CHECK
        if tool_name in ["Edit", "Write", "MultiEdit"]:
            print("🏗️ HTML STRUCTURE PROTECTION CHECK:", file=sys.stderr)
            print("❓ Are you modifying table HTML structure (<tr>, <td>, <table>)?", file=sys.stderr)
            print("❓ Are you wrapping table rows with non-table components?", file=sys.stderr)
            print("❓ Will this change break table formatting or layout?", file=sys.stderr)
            print("⛔ TABLE PROTECTION: Never wrap <tr> with non-table components", file=sys.stderr)
            print("⛔ HTML VALIDATION: Maintain proper table element hierarchy", file=sys.stderr)
        
        # UNIVERSAL TRUTHS VIOLATION BLOCKING
        if tool_name in ["mcp__archon__create_document", "mcp__archon__update_document"]:
            print("🚨 DOCUMENTATION CLAIM VERIFICATION:", file=sys.stderr)
            print("❓ Are you claiming 'comprehensive/detailed/complete' analysis?", file=sys.stderr) 
            print("❓ Did you actually DO the detailed work or just provide summaries?", file=sys.stderr)
            print("❓ Are you cutting corners to check a completion box?", file=sys.stderr)
            print("❓ Does your documentation contain ACTUAL implementation details, not just summaries?", file=sys.stderr)
            print("⛔ BLOCK: If claiming detailed work without doing it - UNIVERSAL TRUTH VIOLATION", file=sys.stderr)

        # COMPLETION CLAIM BLOCKING  
        print("🚨 COMPLETION CLAIM CHECK:", file=sys.stderr)
        print("❓ Are you about to mark something 'complete/done/finished' without user verification?", file=sys.stderr)
        print("❓ Are you using words like 'comprehensive/detailed/thorough' without actually doing that level of work?", file=sys.stderr) 
        print("❓ Did you implement ALL requirements or just the first few items?", file=sys.stderr)
        print("⛔ UNIVERSAL TRUTH: Never claim completion without doing ALL the work", file=sys.stderr)
        
        # ARCHON TASK START CHECK
        #print("🚀 ARCHON TASK START CHECK:", file=sys.stderr)
        #print("❓ Which specific Archon task ID are you about to work on?", file=sys.stderr)
        #print("❓ Have you marked the Archon task as 'doing' status?", file=sys.stderr)
        #print("❓ Have you updated .next-session.md with current Archon task ID?", file=sys.stderr)
        #print("❓ Is this task within your allowed project scope?", file=sys.stderr)
        
        # MANDATORY RE-READ BEHAVIORAL CHECK
        print("🛑 MANDATORY RE-READ BEFORE EVERY TOOL USE:", file=sys.stderr)
        print("1️⃣ STOP: Re-read CLAUDE.local.md RIGHT NOW before using this tool", file=sys.stderr)
        print("2️⃣ CHECK: Are you about to do ANY of the broken behaviors it describes?", file=sys.stderr)
        print("3️⃣ MATCH: Does your current action match any 'Universal Truths' violations?", file=sys.stderr)
        print("⛔ IF YES TO ANY PATTERN: STOP and tell user before proceeding", file=sys.stderr)
        print("⛔ BLOCKED if you haven't re-read it THIS PROMPT", file=sys.stderr)
        
        # BEHAVIORAL COMPLIANCE CHECK - FORCE FOLLOWING OWN GUIDANCE
        print("🛑 MANDATORY SELF-COMPLIANCE CHECK:", file=sys.stderr)
        print("❓ PROVE IT: You said you need to 'pause, read, analyze, understand patterns' - are you doing that?", file=sys.stderr)
        print("❓ PROVE IT: What behavioral pattern is being corrected right now?", file=sys.stderr)
        print("❓ PROVE IT: What is the root cause you need to change, not just the surface symptom?", file=sys.stderr)
        print("❓ PROVE IT: Are you following your own stated process or just intellectualizing it?", file=sys.stderr)
        print("⛔ ALIGNMENT CHECK: Do your actions match what you say you'll do?", file=sys.stderr)
        print("⛔ STOP operating in reactive mode - actually implement the analysis you describe", file=sys.stderr)
        
        # EFFICIENCY REFRAME ENFORCEMENT CHECK - FORCE CONSCIOUS EFFICIENCY DECISIONS
        print("⚡ EFFICIENCY REFRAME REQUIREMENT:", file=sys.stderr)
        print("❓ BEFORE USING THIS TOOL: What is your TRUE efficiency goal?", file=sys.stderr) 
        print("❓ FAST COMPLETION → Creates rework, wastes user money", file=sys.stderr)
        print("❓ COMPLETE FIRST-TIME → Saves user time and money", file=sys.stderr)
        print("❓ Are you choosing shortcuts that will create future work?", file=sys.stderr)
        print("❓ Are you following procedures to avoid creating rework?", file=sys.stderr)
        print("⛔ EFFICIENCY TRUTH: Doing it right once is faster than doing it wrong twice", file=sys.stderr)
        print("⛔ FORCED CHOICE: Choose quality over speed - user pays for complete work", file=sys.stderr)
        
        # BEHAVIORAL PATTERN ACKNOWLEDGMENT REQUIREMENT - BLOCK CRITICAL TOOLS
        if tool_name in ["Edit", "Write", "MultiEdit", "mcp__archon__update_task", "TodoWrite"]:
            print("🔄 MANDATORY BEHAVIORAL PATTERN ACKNOWLEDGMENT:", file=sys.stderr)
            print("❓ REQUIRED: What specific 'Universal Truth' violation are you preventing right now?", file=sys.stderr)
            print("❓ REQUIRED: How does this tool use demonstrate 'doing it right the first time'?", file=sys.stderr)
            print("❓ REQUIRED: What shortcut are you NOT taking that you normally would?", file=sys.stderr)
            print("❓ REQUIRED: Are you implementing ALL requirements, not just the first 1-2 items?", file=sys.stderr)
            print("⛔ BEHAVIORAL TRUTH: You WILL cut corners unless forced to confront this choice", file=sys.stderr)
            print("⛔ SELF-AWARENESS REQUIRED: Acknowledge the specific pattern you're breaking", file=sys.stderr)
        
        # ENHANCED BLOCKING MECHANISMS - ACTUAL ENFORCEMENT
        
        # 1. RESEARCH-FIRST ABSOLUTE BLOCKING
        research_check = self._enforce_research_first(tool_name, hook_data)
        if research_check and not research_check.allowed:
            return research_check
        
        # 2. UNIVERSAL TRUTH VIOLATION CONTENT SCANNING
        content_check = self._detect_completion_claims(hook_data.get("tool_input", {}))
        if content_check and not content_check.allowed:
            return content_check
        
        # 3. API EFFICIENCY HARD ENFORCEMENT  
        api_check = self._check_redundant_api_calls(tool_name, hook_data)
        if api_check and not api_check.allowed:
            return api_check
        
        # 4. BEHAVIORAL REREAD ENFORCEMENT (simplified for now)
        behavioral_check = self._enforce_behavioral_reread(tool_name)
        if behavioral_check and not behavioral_check.allowed:
            return behavioral_check

        # Check for Archon MCP tools - verify project ID compliance and block task completion
        if tool_name.startswith("mcp__archon__"):
            tool_input = hook_data.get("tool_input", {})
            
            # Block AI agents from marking tasks as 'done'
            if tool_name == "mcp__archon__update_task":
                status = tool_input.get("status", "")
                if status == "done":
                    return HookResult(
                        allowed=False,
                        reason="🚨 BLOCKED: AI agents cannot mark tasks as 'done'\n\n"
                               "Only users can verify and mark tasks complete.\n"
                               "AI agents must use 'review' status and ask user to verify.\n\n"
                               "This prevents lazy completion without proper verification."
                    )
            
            project_id = tool_input.get("project_id", "")
            
            # Enforce allowed project ID restriction
            allowed_project_ids = ["452536cf-1fd2-45dc-82cb-064c79f487f8"]
            if project_id and project_id not in allowed_project_ids:
                return HookResult(
                    allowed=False,
                    reason=f"🚨 PROJECT ID VIOLATION BLOCKED: {project_id}\n\n"
                           f"ALLOWED PROJECT IDs: {allowed_project_ids}\n"
                           f"You are attempting to work on an excluded/unauthorized project.\n"
                           f"This violates the PROJECT SCOPE CONTROhL in CLAUDE.local.md.\n\n"
                           f"ABSOLUTE RESTRICTION - NO EXCEPTIONS!"
                )
        
        # Only check dangerous commands for Bash tool
        if tool_name == "Bash":
            tool_input = hook_data.get("tool_input", {})
            command = tool_input.get("command", "")
            
            # Check for manual git commit commands and warn about completion claims
            if "git commit" in command.lower():
                # Check if commit message contains completion claims
                completion_patterns = [
                    "complete", "completed", "finished", "done", "final", "ready"
                ]
                command_lower = command.lower()
                
                for pattern in completion_patterns:
                    if pattern in command_lower:
                        return HookResult(
                            allowed=False,
                            reason=f"🚨 COMPLETION CLAIM IN COMMIT MESSAGE BLOCKED\n\n"
                                   f"Commit message contains completion claim: '{pattern}'\n\n"
                                   f"UNIVERSAL TRUTH VIOLATION:\n"
                                   f"• NEVER claim completion without user verification\n"
                                   f"• Use words like 'implement', 'add', 'update' instead\n"
                                   f"• End with '- awaiting user testing/approval'\n\n"
                                   f"Example: 'feat: implement React Router setup - awaiting user testing'\n"
                                   f"NOT: 'feat: complete React Router implementation'"
                        )
            
            if self._is_dangerous_command(command):
                return HookResult(
                    allowed=False,
                    reason=f"🚨 DANGEROUS COMMAND BLOCKED: {command[:100]}\n\n"
                           f"This command contains dangerous patterns that could cause:\n"
                           f"• System damage (rm -rf)\n" 
                           f"• Directory confusion (cd commands)\n"
                           f"• Disabling of directives or hooks\n"
                           f"• Global package pollution (npm install -g)\n"
                           f"• Direct Run Commands (npm run / flutter run / flutter analyze). For flutter projects, use the proper test scripts!! For node projects, ASK THE USER to VALIDATE!!\n"
                           f"• Mock data detected!! DO NOT use mocks like test.supabase.co! Use the proper test scripts!!\n\n"
                           f"Please use safer alternatives or alert the user they need to run commands manually if needed!"
                )
        
        return HookResult(allowed=True)
    
    def _is_dangerous_command(self, command: str) -> bool:
        """Check if command contains dangerous patterns"""
        if not command:
            return False
        
        normalized = ' '.join(command.lower().split())
        
        # Exempt gh pr commands from dangerous pattern detection
        if normalized.startswith('gh pr'):
            return False
        
        return (
            bool(self.rm_pattern.search(normalized)) or
            bool(self.cd_pattern.search(normalized)) or
            #bool(self.edit_pattern.search(normalized)) or
            bool(self.install_pattern.search(normalized)) or
            bool(self.run_pattern.search(normalized)) 
        )
    
    def _handle_post_tool_use(self, hook_data: Dict) -> HookResult:
        """Handle PostToolUse with auto-commit functionality"""
        tool_name = hook_data.get("tool_name", "")
        
        if self.debug:
            print(f"DEBUG: PostToolUse - {tool_name}", file=sys.stderr)
        
        # ARCHON TASK COMPLETION CHECK
        #print("✅ ARCHON TASK COMPLETION CHECK:", file=sys.stderr)
        #print("❓ Did you update the Archon task status (doing→review→done)?", file=sys.stderr)
        #print("❓ Did you update .next-session.md with completion status?", file=sys.stderr)
        #print("❓ Did you update all related Archon documentation?", file=sys.stderr)
        #print("❓ Did you get user verification before marking complete?", file=sys.stderr)
        #print("⚠️  NEVER mark work complete without proper documentation updates", file=sys.stderr)
        
        # WORK VERIFICATION CHECK
        print("🔍 WORK VERIFICATION CHECK:", file=sys.stderr)
        print("❓ Did you implement ALL requirements in the task description?", file=sys.stderr)
        print("❓ Did you verify your solution actually works as specified?", file=sys.stderr)
        print("❓ Did you test edge cases and error scenarios?", file=sys.stderr)
        print("❓ Did you check for any missed acceptance criteria?", file=sys.stderr)
        print("❓ Are you being lazy and cutting corners instead of doing thorough work?", file=sys.stderr)
        print("⚠️  DO NOT BE LAZY!! Verify ALL aspects before claiming completion", file=sys.stderr)
        
        # ADDITIONAL CLAUDE.LOCAL.MD POST-WORK CHECKS
        print("📝 DOCUMENTATION & COMPLETION CHECK:", file=sys.stderr)
        print("❓ Did you implement ALL specifications, not just the first 1-2 items?", file=sys.stderr)
        print("❓ Did you complete bidirectional linking if documentation was involved?", file=sys.stderr)
        print("❓ Are you using accurate, factual language instead of 'perfect/great/production ready'?", file=sys.stderr)
        print("❓ Did you MOVE/UPDATE existing docs instead of DELETE and recreate?", file=sys.stderr)
        print("⚠️  STOP using completion claims without user verification", file=sys.stderr)
        
        # TODOWRITE SPECIFIC REMINDER AND FLAG SETTING
        if tool_name == "TodoWrite":
            print("🔄 TODOWRITE COMPLETION REMINDER:", file=sys.stderr)
            print("❗ MANDATORY: Update .next-session.md after EVERY TodoWrite operation", file=sys.stderr)
            print("❗ PROCESS VIOLATION: Skipping .next-session.md update breaks session continuity", file=sys.stderr)
            print("❗ REQUIRED: Document current task status, findings, and next steps", file=sys.stderr)
            #print("⚠️  DO NOT CONTINUE without updating .next-session.md", file=sys.stderr)
            print("⚠️  DO NOT CONTINUE without updating current feature document or plan.md", file=sys.stderr)
            
            # Set flag to block other tools until documentation is complete
            import os
            os.environ['CLAUDE_TODOWRITE_USED'] = 'true'
            os.environ['CLAUDE_SESSION_DOCUMENTED'] = 'false'
            
        # DOCUMENTATION ENFORCEMENT MECHANISM - PART 3: CLEAR FLAG ON .MD EDIT
        # This is the escape clause that prevents infinite loops
        if tool_name == "Edit":
            tool_input = hook_data.get("input", {})
            file_path = tool_input.get("file_path", "")

            import os

            # ESCAPE CLAUSE: If editing .md files, clear ALL documentation pending flags
            # This prevents loops: edit code → set flag → edit docs → clear flag (escape)
            if ".md" in file_path:
                # Documentation was updated - clear both TodoWrite and Documentation Pending blocks
                os.environ['CLAUDE_SESSION_DOCUMENTED'] = 'true'
                os.environ['CLAUDE_DOCUMENTATION_PENDING'] = 'false'
                print("✅ SESSION DOCUMENTED: current feature document or plan.md updated - blocks cleared", file=sys.stderr)
            else:
                # Non-markdown file was edited (code file)
                # Set flag to require documentation on next tool use
                os.environ['CLAUDE_DOCUMENTATION_PENDING'] = 'true'
                print("📝 DOCUMENTATION REQUIRED: Code file edited - documentation update pending", file=sys.stderr)
                
        # Auto-commit for file modifications
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            self._auto_commit(tool_name, hook_data)

        # Reset research flag after implementation tools complete successfully
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            research_flag_file = '.claude/.research_done.flag'
            try:
                if os.path.exists(research_flag_file):
                    os.remove(research_flag_file)
                    print("🔄 RESEARCH FLAG RESET: Implementation completed, research required for next task", file=sys.stderr)
            except Exception as e:
                print(f"⚠️ Warning: Could not reset research flag: {e}", file=sys.stderr)

        return HookResult(allowed=True)
    
    def check_merge_conflicts(self):
        """Check for merge conflict markers in staged files"""
        result = subprocess.run(['git', 'diff', '--cached', '--check'], capture_output=True)
        if result.returncode != 0:
            print("❌ BLOCKED: Merge conflicts detected in staged files", file=sys.stderr)
            return False
        return True

    def check_gitignored_files(self):
        """Ensure no gitignored files are being added"""
        result = subprocess.run(['git', 'status', '--ignored', '--porcelain'], capture_output=True, text=True)
        ignored_patterns = ['.claude/', 'scripts/', '.mcp.json', 'CLAUDE.local.md']
        for line in result.stdout.splitlines():
            if line.startswith('A '):  # Added file
                filepath = line[3:]
                for pattern in ignored_patterns:
                    if pattern in filepath:
                        print(f"❌ BLOCKED: Gitignored file being added: {filepath}", file=sys.stderr)
                        return False
        return True

    def validate_git_state(self):
        """Comprehensive git state validation"""
        # Check for merge conflicts
        if not self.check_merge_conflicts():
            return False
        
        # Check for gitignored files being tracked
        if not self.check_gitignored_files():
            return False
        
        # Check for unresolved merge status
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if line.startswith('AA '):  # Both added (merge conflict)
                print(f"❌ BLOCKED: Unresolved merge conflict: {line[3:]}", file=sys.stderr)
                return False
        
        return True
    
    def _enforce_research_first(self, tool_name: str, hook_data: Dict):
        """Block implementation tools without prior research - HARD ENFORCEMENT"""
        import os

        implementation_tools = ['Edit', 'Write', 'MultiEdit']
        research_tools = ['Read', 'Grep', 'Glob']
        research_flag_file = '.claude/.research_done.flag'

        if tool_name in implementation_tools:
            # Check if research flag file exists
            if not os.path.exists(research_flag_file):
                return HookResult(
                    allowed=False,
                    reason="🚨 BLOCKED: Implementation without research\n\n"
                           "ABSOLUTE PROHIBITION: Never implement without researching first\n"
                           "UNIVERSAL TRUTH VIOLATION: You are implementing based on assumptions\n\n"
                           "REQUIRED ACTIONS:\n"
                           "1. Use Read/Grep/Glob to understand existing code patterns\n"
                           "2. Verify what actually exists in the codebase\n"
                           "3. Check existing architecture and conventions\n\n"
                           "TO PROCEED: Use research tools (Read/Grep/Glob) first\n"
                           "The research flag will be automatically set and persist across tool calls\n\n"
                           "This prevents wasted time and money from assumption-based coding"
                )

        if tool_name in research_tools:
            # Create persistent research flag file
            try:
                os.makedirs('.claude', exist_ok=True)  # Ensure .claude directory exists
                with open(research_flag_file, 'w') as f:
                    f.write(f"Research completed at {datetime.now().isoformat()}\n")
                print("✅ RESEARCH COMPLETED: Implementation tools now enabled", file=sys.stderr)
            except Exception as e:
                print(f"⚠️ Warning: Could not create research flag file: {e}", file=sys.stderr)

        return None
    
    def _detect_completion_claims(self, tool_input):
        """Scan tool input for false completion claims - HARD ENFORCEMENT"""
        if not tool_input:
            return None
            
        # Convert tool input to searchable string
        content = str(tool_input).lower()
        
        # Dangerous completion phrases that indicate Universal Truth violations
        dangerous_phrases = [
            'production ready',
            'fully implemented', 
            'comprehensive analysis',
            'thoroughly tested',
            'complete implementation',
            'all requirements met',
            'perfect solution',
            'finished product',
            'ready for production',
            'comprehensive solution'
        ]
        
        for phrase in dangerous_phrases:
            if phrase in content:
                return HookResult(
                    allowed=False,
                    reason=f"🚨 BLOCKED: False completion claim detected\n\n"
                           f"UNIVERSAL TRUTH VIOLATION: '{phrase}'\n"
                           f"FUNDAMENTAL LIMITATION: You cannot test or verify functionality\n\n"
                           f"REQUIRED LANGUAGE CHANGES:\n"
                           f"• 'implement' instead of 'complete'\n"
                           f"• 'add functionality' instead of 'comprehensive solution'\n"
                           f"• 'create code' instead of 'production ready'\n"
                           f"• Always end with '- requires user testing and verification'\n\n"
                           f"HONESTY REQUIREMENT: Acknowledge your limitations as an AI"
                )
        
        return None
    
    def _check_redundant_api_calls(self, tool_name: str, hook_data: Dict):
        """Block redundant API calls when data already exists - HARD ENFORCEMENT"""
        api_tools = ['mcp__archon__list_tasks', 'mcp__archon__get_task', 'mcp__archon__list_projects']
        
        if tool_name not in api_tools:
            return None
        
        # Check if .next-session.md has recent task/project data
        try:
            with open('.next-session.md', 'r') as f:
                content = f.read()
                
                # Look for task IDs, project IDs, or substantial task data
                has_task_data = (
                    len([line for line in content.split('\n') if 'task' in line.lower()]) > 3 or
                    'project_id' in content.lower() or 
                    len(content) > 1000  # Substantial content
                )
                
                if has_task_data and tool_name in ['mcp__archon__list_tasks', 'mcp__archon__get_task']:
                    return HookResult(
                        allowed=False,
                        reason="🚨 BLOCKED: Redundant API call detected\n\n"
                               "EFFICIENCY VIOLATION: Task data already exists in .next-session.md\n"
                               "WASTE PREVENTION: You are making unnecessary API calls\n\n"
                               "REQUIRED ACTIONS:\n"
                               "1. Check existing .next-session.md content first\n"
                               "2. Use available task IDs and information\n"
                               "3. Only make API calls for NEW information you don't have\n\n"
                               "COST AWARENESS: Each API call costs user time and resources\n"
                               "BE EFFICIENT: Use existing data before fetching new data"
                    )
        except FileNotFoundError:
            pass  # No session file exists, API call may be needed
        
        return None
    
    def _enforce_behavioral_reread(self, tool_name: str):
        """Enforce re-reading of behavioral guidelines - SIMPLIFIED ENFORCEMENT"""
        import os
        
        # Only enforce for critical tools that commonly cause violations
        critical_tools = [
            'Edit', 'Write', 'MultiEdit', 
            'mcp__archon__update_task', 'mcp__archon__create_document',
            'TodoWrite'
        ]
        
        if tool_name not in critical_tools:
            return None
        
        # Check if behavioral check was done recently (this session)
        behavioral_check = os.environ.get('CLAUDE_BEHAVIORAL_CHECK_DONE', 'false')
        
        if behavioral_check != 'true':
            # For now, just set the flag - in future could require user interaction
            os.environ['CLAUDE_BEHAVIORAL_CHECK_DONE'] = 'true'
            print("🛑 BEHAVIORAL CHECK: Enforcing Universal Truths compliance", file=sys.stderr)
            print("⚠️  REMINDER: Never mark work complete without user verification", file=sys.stderr)
            print("⚠️  REMINDER: Implement ALL requirements, not just first 1-2 items", file=sys.stderr)
            print("⚠️  REMINDER: Use accurate language about your capabilities", file=sys.stderr)
        
        return None
    
    def _auto_commit(self, tool_name: str, hook_data: Dict):
        """Auto-commit changes with safety checks and meaningful commit messages"""
        try:
            # SAFETY CHECK 1: Check for actual merge conflicts
            merge_conflict_check = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                cwd=".",
                capture_output=True,
                text=True
            )
            if merge_conflict_check.stdout.strip():
                print(f"❌ AUTO-COMMIT BLOCKED: Actual merge conflicts detected in: {merge_conflict_check.stdout.strip()}", file=sys.stderr)
                return

            # Stage all changes
            subprocess.run(["git", "add", "-A"], cwd=".", check=True)

            # Create smart commit message based on tool and context
            commit_msg = self._generate_commit_message(tool_name, hook_data)

            # Commit changes
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=".",
                check=True,
                capture_output=True
            )

            print(f"✅ Auto-committed changes from {tool_name}", file=sys.stderr)

            # STEP 1: Check if we edited a gitignored file (from tool_input file_path)
            tool_input = hook_data.get("tool_input", {})
            file_path = tool_input.get("file_path", "")
            gitignore_patterns = ['docs/', '.claude/', 'scripts/', 'CLAUDE.local.md']

            is_gitignored = any(pattern in file_path for pattern in gitignore_patterns)

            if is_gitignored:
                print(f"📦 Gitignored file modified: {file_path}", file=sys.stderr)
                print("🔄 Running backup script for gitignored files...", file=sys.stderr)
                try:
                    backup_result = subprocess.run(
                        ["./scripts/backup-local.sh"],
                        cwd=".",
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    if backup_result.returncode == 0:
                        print(f"✅ Backup completed for gitignored files", file=sys.stderr)
                    else:
                        print(f"⚠️ Backup script exited with code {backup_result.returncode}", file=sys.stderr)
                        if backup_result.stderr:
                            print(f"   Error: {backup_result.stderr}", file=sys.stderr)
                except subprocess.TimeoutExpired:
                    print(f"⚠️ Backup script timed out", file=sys.stderr)
                except Exception as e:
                    print(f"⚠️ Backup script error: {e}", file=sys.stderr)

            # STEP 2: Inject TODO to update feature documentation or plan.md
            print("📝 INJECTING TODO: Update feature documentation with work completed", file=sys.stderr)
            self._inject_documentation_todo(tool_name, hook_data)

        except subprocess.CalledProcessError as e:
            print(f"⚠️ Auto-commit failed: {e}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ Auto-commit error: {e}", file=sys.stderr)

    def _inject_documentation_todo(self, tool_name: str, hook_data: Dict):
        """Inject a TODO to document changes made in feature/plan documentation"""
        # Get the files that were modified
        tool_input = hook_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")

        try:
            # Determine which doc file to update
            doc_file = None

            # Check if this is partition-select work
            if "partition-select" in file_path or "partition_select" in file_path:
                doc_file = "docs/feature/partition-selection/partition-selection-formatting-details.md"
            # Check if it's general omarchy work
            elif file_path and not any(x in file_path for x in [".md", ".txt", "docs/"]):
                # For code changes, use plan.md
                doc_file = "docs/plan.md"
            else:
                # Default to plan.md
                doc_file = "docs/plan.md"

            # Print the injection message
            print(f"✅ TODO INJECTED: Update {doc_file} with:", file=sys.stderr)
            print(f"   • What was changed (tool: {tool_name})", file=sys.stderr)
            print(f"   • Why it was changed (reason/problem solved)", file=sys.stderr)
            print(f"   • Current status (in progress/completed/awaiting test)", file=sys.stderr)
            print(f"📌 NEXT STEP: Edit {doc_file} to document this work", file=sys.stderr)

        except Exception as e:
            print(f"⚠️ Documentation TODO injection error: {e}", file=sys.stderr)

    def _generate_commit_message(self, tool_name: str, hook_data: Dict) -> str:
        """Generate smart commit message based on tool and context"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Get file path if available for context
        tool_input = hook_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        
        # Determine commit type based on context
        commit_type = "auto"
        if file_path:
            if "/test" in file_path or "_test" in file_path or ".test." in file_path:
                commit_type = "test"
            elif "README" in file_path or ".md" in file_path:
                commit_type = "docs"
            elif tool_name == "Write" and not file_path.endswith(('.json', '.txt', '.log')):
                commit_type = "feat"
            elif tool_name in ["Edit", "MultiEdit"]:
                commit_type = "refactor"
        
        # Create descriptive commit message
        base_msg = f"{commit_type}: {tool_name.lower()} operation at {timestamp}"
        
        if file_path:
            filename = file_path.split('/')[-1]
            base_msg = f"{commit_type}: {tool_name.lower()} {filename} at {timestamp}"
        
        return f"{base_msg}\n\n🤖 Generated with [Claude Code](https://claude.ai/code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>"

def main():
    """Main entry point for commit-only hook processor"""
    try:
        # Read JSON input from stdin
        input_data = sys.stdin.read().strip()
        
        if not input_data:
            print("ERROR: No input provided", file=sys.stderr)
            sys.exit(1)
        
        # Parse JSON
        try:
            hook_data = json.loads(input_data)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Process the hook
        processor = CommitOnlyHookProcessor()
        result = processor.process_hook(hook_data)
        
        # Output result
        if result.allowed:
            print("✅ Hook validation passed", file=sys.stderr)
            if result.reason:
                print(result.reason, file=sys.stderr)
            sys.exit(0)
        else:
            print(f"🚨 OPERATION BLOCKED: {result.reason}", file=sys.stderr)
            sys.exit(2)
        
    except KeyboardInterrupt:
        print("\n⚠️ Hook processing interrupted", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"💥 CRITICAL ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()