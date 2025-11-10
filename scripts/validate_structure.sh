#!/bin/bash
#
# Complete Project Structure Validation Workflow
# EduAutismo IA - MVP
#
# This script performs a comprehensive validation of the project structure
# and provides detailed feedback and recommendations.
#
# Usage:
#   ./scripts/validate_structure.sh [--fix] [--priority N]
#
# Options:
#   --fix          Automatically create missing files (Priority 1 by default)
#   --priority N   Set priority level for creation (1=Critical, 2=Important, 3=All)
#   --help         Show this help message

set -e  # Exit on error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Default values
FIX_MODE=false
PRIORITY=1

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX_MODE=true
            shift
            ;;
        --priority)
            PRIORITY="$2"
            shift 2
            ;;
        --help|-h)
            echo "Complete Project Structure Validation Workflow"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --fix          Automatically create missing files"
            echo "  --priority N   Priority level (1=Critical, 2=Important, 3=All)"
            echo "  --help, -h     Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Just validate"
            echo "  $0 --fix              # Create critical files"
            echo "  $0 --fix --priority 2 # Create critical + important files"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Print header
echo -e "${BOLD}${BLUE}=====================================================================${NC}"
echo -e "${BOLD}${BLUE}EduAutismo IA - Complete Structure Validation${NC}"
echo -e "${BOLD}${BLUE}=====================================================================${NC}"
echo ""
echo -e "${CYAN}Date:${NC} $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "${CYAN}Mode:${NC} $(if [ "$FIX_MODE" = true ]; then echo "Fix (Priority $PRIORITY)"; else echo "Report Only"; fi)"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 is not installed${NC}"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

echo -e "${BOLD}📋 Step 1: Checking Python Version${NC}"
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION"
echo ""

# Check project structure
echo -e "${BOLD}🔍 Step 2: Validating Project Structure${NC}"
echo ""

if [ "$FIX_MODE" = true ]; then
    python3 scripts/check_structure.py --create-missing --priority "$PRIORITY"
else
    python3 scripts/check_structure.py --report-only
fi

STRUCTURE_EXIT_CODE=$?

echo ""
echo -e "${BOLD}📦 Step 3: Verifying Python Package Structure${NC}"

# Check for __init__.py files
MISSING_INIT=0
echo -n "Checking Python packages... "

# Find all directories in backend/app that should be packages
while IFS= read -r dir; do
    if [ ! -f "$dir/__init__.py" ]; then
        if [ $MISSING_INIT -eq 0 ]; then
            echo ""
            echo -e "${YELLOW}⚠ Missing __init__.py files:${NC}"
        fi
        echo -e "  ${YELLOW}•${NC} $dir/"
        ((MISSING_INIT++))
    fi
done < <(find backend/app -type d -not -path "*/venv/*" -not -path "*/__pycache__/*" 2>/dev/null || true)

if [ $MISSING_INIT -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
fi

echo ""

# Verify critical files exist
echo -e "${BOLD}📄 Step 4: Checking Critical Files${NC}"

CRITICAL_FILES=(
    "backend/app/main.py"
    "backend/app/config.py"
    "backend/app/core/database.py"
    "backend/requirements.txt"
    "frontend/package.json"
    "frontend/vite.config.js"
)

MISSING_CRITICAL=0
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file ${YELLOW}(missing)${NC}"
        ((MISSING_CRITICAL++))
    fi
done

echo ""

# Check Python syntax if not in fix mode
if [ "$FIX_MODE" = false ]; then
    echo -e "${BOLD}🐍 Step 5: Validating Python Syntax${NC}"

    SYNTAX_ERRORS=0
    while IFS= read -r pyfile; do
        if ! python3 -m py_compile "$pyfile" 2>/dev/null; then
            if [ $SYNTAX_ERRORS -eq 0 ]; then
                echo -e "${RED}Syntax errors found:${NC}"
            fi
            echo -e "  ${RED}✗${NC} $pyfile"
            ((SYNTAX_ERRORS++))
        fi
    done < <(find backend/app -name "*.py" -not -path "*/venv/*" 2>/dev/null || true)

    if [ $SYNTAX_ERRORS -eq 0 ]; then
        echo -e "${GREEN}✓${NC} No syntax errors found"
    else
        echo -e "${YELLOW}⚠${NC} Found $SYNTAX_ERRORS file(s) with syntax errors"
    fi
    echo ""
fi

# Summary and recommendations
echo -e "${BOLD}${BLUE}=====================================================================${NC}"
echo -e "${BOLD}Summary & Recommendations${NC}"
echo -e "${BOLD}${BLUE}=====================================================================${NC}"
echo ""

if [ $STRUCTURE_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Excellent!${NC} Project structure is complete and well-formed."
    echo ""
    echo -e "${BOLD}Next Steps:${NC}"
    echo -e "  1. Review the generated files and add your business logic"
    echo -e "  2. Configure database connection in backend/app/config.py"
    echo -e "  3. Set up environment variables (.env file)"
    echo -e "  4. Install dependencies:"
    echo -e "     ${CYAN}cd backend && pip install -r requirements.txt${NC}"
    echo -e "     ${CYAN}cd frontend && npm install${NC}"
    echo -e "  5. Run tests:"
    echo -e "     ${CYAN}pytest backend/tests/${NC}"

elif [ $STRUCTURE_EXIT_CODE -eq 1 ]; then
    echo -e "${YELLOW}⚠ Good${NC} but some components are missing."
    echo ""

    if [ "$FIX_MODE" = false ]; then
        echo -e "${BOLD}Recommended Actions:${NC}"
        echo -e "  ${CYAN}# Create all critical files${NC}"
        echo -e "  ./scripts/validate_structure.sh --fix --priority 1"
        echo ""
        echo -e "  ${CYAN}# Create critical + important files${NC}"
        echo -e "  ./scripts/validate_structure.sh --fix --priority 2"
    else
        echo -e "${BOLD}Files Created Successfully!${NC}"
        echo -e "Run this script again without --fix to verify"
    fi

else
    echo -e "${RED}❌ Issues Detected${NC} - Major structural problems found."
    echo ""
    echo -e "${BOLD}Required Actions:${NC}"
    echo -e "  1. Fix critical structure issues"
    echo -e "  2. Run: ${CYAN}./scripts/validate_structure.sh --fix --priority 1${NC}"
    echo -e "  3. Review and configure created files"
fi

echo ""

# Git status if it's a git repository
if [ -d ".git" ]; then
    echo -e "${BOLD}📊 Git Status:${NC}"
    UNTRACKED=$(git ls-files --others --exclude-standard | wc -l)
    MODIFIED=$(git ls-files --modified | wc -l)

    if [ $UNTRACKED -gt 0 ] || [ $MODIFIED -gt 0 ]; then
        echo -e "  ${YELLOW}Untracked files:${NC} $UNTRACKED"
        echo -e "  ${YELLOW}Modified files:${NC} $MODIFIED"
        echo ""
        echo -e "  ${CYAN}Tip:${NC} Review changes with 'git status' before committing"
    else
        echo -e "  ${GREEN}✓${NC} Working directory clean"
    fi
    echo ""
fi

# Performance metrics
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Validation completed at $(date '+%H:%M:%S')${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Exit with the same code as structure validation
exit $STRUCTURE_EXIT_CODE
