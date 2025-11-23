#!/bin/bash
# Session Start Enforcer Hook
# Enforces CRITICAL RULES at conversation start
# Project Standards Enforcement

set -euo pipefail

# Find and set PROJECT_ROOT by looking for .claude/settings.local.json
PROJECT_ROOT=$(pwd)
while [[ "$PROJECT_ROOT" != "/" && ! -f "$PROJECT_ROOT/.claude/settings.local.json" ]]; do
    PROJECT_ROOT=$(dirname "$PROJECT_ROOT")
done

if [[ ! -f "$PROJECT_ROOT/.claude/settings.local.json" ]]; then
    echo "❌ ERROR: Could not find .claude/settings.local.json - not in a project-standards project?"
    exit 1
fi

export PROJECT_ROOT
echo "📁 PROJECT_ROOT set to: $PROJECT_ROOT"

# Source configuration from project root
if [ -f "$PROJECT_ROOT/.claude-hooks-config.sh" ]; then
    source "$PROJECT_ROOT/.claude-hooks-config.sh"
fi

# =============================================================================
# CRITICAL SESSION START ENFORCEMENT
# =============================================================================

echo "🚨 SESSION START VALIDATION: Checking compliance with CRITICAL RULES..."

# Check if hooks are enabled
if [ "${CLAUDE_HOOKS_ENABLED:-false}" != "true" ]; then
    echo "✅ Hooks disabled - allowing operation"
    exit 0
fi

# =============================================================================
# STEP 1: CHECK .current-session FIRST
# =============================================================================

check_current_session() {
    echo "📋 STEP 1: Checking .current-session file..."
    
    if [ ! -f "${CURRENT_SESSION_FILE:-.current-session}" ]; then
        echo "❌ No .current-session file found"
        return 1
    fi
    
    # Get session file name
    local session_file
    session_file=$(cat "${CURRENT_SESSION_FILE:-.current-session}" | head -1 | xargs)
    
    if [ -z "$session_file" ]; then
        echo "❌ .current-session file is empty"
        return 1
    fi
    
    # Check if session file exists
    local session_path="${SESSION_DOCS_PATH:-docs/sessions}/${session_file}"
    if [ ! -f "$session_path" ]; then
        echo "❌ Session file not found: $session_path"
        return 1
    fi
    
    # Check if session is completed
    if grep -q "Session Status.*Completed\|Status.*Completed" "$session_path" 2>/dev/null; then
        echo "✅ Found completed session: $session_file"
        echo "🔄 Session is marked as completed - need new session"
        return 1
    fi
    
    echo "✅ Found active session: $session_file"
    
    # Display session context
    echo ""
    echo "📖 CURRENT SESSION CONTEXT:"
    echo "============================================"
    echo "📁 Session File: $session_file"
    
    # Extract key session information
    if grep -q "## Session Objectives" "$session_path" 2>/dev/null; then
        echo ""
        echo "🎯 SESSION OBJECTIVES:"
        sed -n '/## Session Objectives/,/^## /p' "$session_path" | head -20 | grep -E "^- \[.\]|^[0-9]+\." | head -5
    fi
    
    if grep -q "## Progress Log\|## Key Achievements" "$session_path" 2>/dev/null; then
        echo ""
        echo "📈 RECENT PROGRESS:"
        # Show last few progress entries
        grep -E "^### [0-9]{2}:[0-9]{2}|^### Progress Update|^## Key Achievements" "$session_path" | tail -3
    fi
    
    # Check for outstanding items
    if grep -q "## Next Session Priorities\|## Outstanding" "$session_path" 2>/dev/null; then
        echo ""
        echo "🔮 NEXT PRIORITIES:"
        sed -n '/## Next Session Priorities/,/^## /p' "$session_path" | grep -E "^- \[ \]" | head -3
    fi
    
    echo "============================================"
    echo ""
    
    return 0
}

# =============================================================================
# STEP 2: CHECK PROJECT PLAN IF NO ACTIVE SESSION
# =============================================================================

check_project_priorities() {
    echo "📋 STEP 2: Checking project priorities..."
    
    local project_plan_file="${PROJECT_PLAN_FILE:-docs/project-plan.md}"
    
    if [ ! -f "$project_plan_file" ]; then
        echo "⚠️  No project plan found at: $project_plan_file"
        echo "💡 Consider creating a project plan to track priorities"
        return 0
    fi
    
    echo "📖 PROJECT PRIORITIES FROM: $project_plan_file"
    echo "============================================"
    
    # Extract project overview
    if grep -q "## Project Overview\|## 📋 Project Overview" "$project_plan_file" 2>/dev/null; then
        echo ""
        echo "🎯 PROJECT OVERVIEW:"
        sed -n '/## .*Project Overview/,/^## /p' "$project_plan_file" | head -10 | grep -v "^##" | head -5
    fi
    
    # Extract current phase tasks
    if grep -q "### Phase" "$project_plan_file" 2>/dev/null; then
        echo ""
        echo "🚀 CURRENT PHASE TASKS:"
        # Find uncompleted tasks in phases
        grep -A 20 "### Phase" "$project_plan_file" | grep -E "^- \[ \]" | head -5
    fi
    
    echo "============================================"
    echo ""
    
    return 0
}

# =============================================================================
# STEP 3: ENFORCE USER CONFIRMATION REQUIREMENT
# =============================================================================

enforce_user_confirmation() {
    echo "👤 STEP 3: Enforcing user confirmation requirement..."
    
    echo ""
    echo "🚨 CRITICAL REQUIREMENT: STOP AND ASK USER"
    echo "============================================"
    echo ""
    echo "📋 BEFORE PROCEEDING, YOU MUST:"
    echo "1. ✋ STOP automatic execution"
    echo "2. 🗣️  ASK user what they want to work on"
    echo "3. ⏳ WAIT for user confirmation/direction"
    echo "4. 🎯 ONLY proceed after user provides guidance"
    echo ""
    echo "❌ DO NOT assume priorities or start tasks automatically"
    echo "✅ DO ask for user direction even if priorities are clear"
    echo ""
    echo "🔒 This requirement is ENFORCED to ensure:"
    echo "   • User has opportunity to change priorities"
    echo "   • User can ask questions before work begins"
    echo "   • User can provide guidance on approach and scope"
    echo "   • Proper project direction alignment"
    echo ""
    
    return 0
}

# =============================================================================
# STEP 4: SESSION START RECOMMENDATIONS
# =============================================================================

provide_session_guidance() {
    echo "💡 STEP 4: Session start recommendations..."
    
    echo ""
    echo "🔧 IF STARTING NEW SESSION:"
    echo "============================================"
    echo "Follow the complete workflow in @CLAUDE.md:"
    echo "  See 'Session Start Requirements (ENHANCED WORKFLOW)'"
    echo ""
    echo "🔧 IF CONTINUING EXISTING SESSION:"
    echo "============================================"
    echo "Session context has been provided above."
    echo "Follow @CLAUDE.md user confirmation requirements."
    echo ""
    
    return 0
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    echo "🚀 SESSION START ENFORCER RUNNING..."
    echo ""
    
    # Step 1: Check current session first
    if check_current_session; then
        echo "✅ Active session found - displaying context"
    else
        echo "❌ No active session - checking project priorities"
        # Step 2: Check project plan if no active session
        check_project_priorities
    fi
    
    # Step 3: Always enforce user confirmation
    enforce_user_confirmation
    
    # Step 4: Provide session guidance
    provide_session_guidance
    
    echo "✅ SESSION START VALIDATION COMPLETED"
    echo "🎯 Agent must now ask user for direction before proceeding"
    echo ""
    
    return 0
}

# Execute main function
main "$@"