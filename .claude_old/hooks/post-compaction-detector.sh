#!/bin/bash
# Post-Compaction Detection Hook
# Purpose: Detect when Claude Code has performed compaction and enforce session recovery
# Triggers: STOP hook - runs when Claude finishes responding

set -euo pipefail

# Use PROJECT_ROOT if set, otherwise find it
if [ -z "${PROJECT_ROOT:-}" ]; then
    PROJECT_ROOT=$(pwd)
    while [[ "$PROJECT_ROOT" != "/" && ! -f "$PROJECT_ROOT/.claude/settings.local.json" ]]; do
        PROJECT_ROOT=$(dirname "$PROJECT_ROOT")
    done
    
    if [[ ! -f "$PROJECT_ROOT/.claude/settings.local.json" ]]; then
        echo "❌ ERROR: Could not find .claude/settings.local.json - not in a project-standards project?"
        exit 1
    fi
fi

# Source configuration from project root
if [ -f "$PROJECT_ROOT/.claude-hooks-config.sh" ]; then
    source "$PROJECT_ROOT/.claude-hooks-config.sh"
fi

# Read JSON input from stdin
input_json=$(cat)

# Extract transcript path
transcript_path=$(echo "$input_json" | jq -r '.transcript_path // ""')

# Exit early if no transcript path
if [[ -z "$transcript_path" || ! -f "$transcript_path" ]]; then
    exit 0
fi

# =============================================================================
# POST-COMPACTION DETECTION LOGIC
# =============================================================================

detect_compaction() {
    local transcript="$1"
    
    # First check: Look for ANY compaction markers in the transcript
    if ! grep -q '"isCompactSummary":true' "$transcript" 2>/dev/null; then
        return 1  # No compaction markers at all
    fi
    
    # Second check: Look for recent session start that might indicate we need enforcement
    # Get conversation count since last compaction summary
    local lines_since_compaction
    local last_compaction_line
    last_compaction_line=$(grep -n '"isCompactSummary":true' "$transcript" | tail -1 | cut -d: -f1)
    
    if [[ -n "$last_compaction_line" ]]; then
        local total_lines
        total_lines=$(wc -l < "$transcript" 2>/dev/null || echo "0")
        lines_since_compaction=$((total_lines - last_compaction_line))
        
        # If we have fewer than 50 lines since last compaction, we're likely at start of new session
        if [[ $lines_since_compaction -lt 50 ]]; then
            return 0  # Recently post-compaction - enforce recovery
        fi
    fi
    
    return 1  # No recent compaction detected
}

# =============================================================================
# SESSION RECOVERY ENFORCEMENT
# =============================================================================

enforce_session_recovery() {
    echo ""
    echo "🚨 POST-COMPACTION DETECTED: Enforcing session recovery protocol"
    echo "=================================================================="
    echo ""
    
    # Run the session start enforcer to get proper context
    if [[ -x "./.claude/hooks/session-start-enforcer.sh" ]]; then
        echo "🔄 Running session recovery enforcement..."
        ./.claude/hooks/session-start-enforcer.sh
        
        # Return blocking decision with session recovery instructions
        cat << 'EOF'
{
  "decision": "block",
  "reason": "🚨 POST-COMPACTION RECOVERY REQUIRED\n\n✅ SESSION CONTEXT HAS BEEN PROVIDED ABOVE\n\n📋 MANDATORY REQUIREMENTS:\n• ✋ STOP automatic execution\n• 🗣️ ASK user what they want to work on\n• ⏳ WAIT for user confirmation/direction\n• 🎯 ONLY proceed after user provides guidance\n\n❌ DO NOT assume priorities from compaction summary\n✅ DO follow current session context provided above\n\n🔒 This is enforced to ensure proper session continuity after context reset."
}
EOF
    else
        echo "⚠️ session-start-enforcer.sh not found - basic recovery only"
        
        # Basic recovery without session enforcer
        cat << 'EOF'
{
  "decision": "block", 
  "reason": "🚨 POST-COMPACTION DETECTED\n\n📋 RECOVERY REQUIRED:\n• Check .current-session file for active session\n• Ask user for direction before proceeding\n• Do not assume priorities from summary\n\n⚠️ session-start-enforcer.sh not available for full recovery"
}
EOF
    fi
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    # Only run detection if hooks are enabled
    if [ "${CLAUDE_HOOKS_ENABLED:-false}" != "true" ]; then
        exit 0
    fi
    
    # Detect post-compaction state
    if detect_compaction "$transcript_path"; then
        echo "🔍 POST-COMPACTION DETECTION: Compaction markers found in transcript"
        enforce_session_recovery
        exit 2  # Block with feedback to Claude
    else
        # No compaction detected - allow normal operation
        exit 0
    fi
}

# Execute main function
main "$@"