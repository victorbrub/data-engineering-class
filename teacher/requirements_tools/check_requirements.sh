#!/bin/bash
# check_requirements.sh - Verify requirements before installation
# This script can be sourced or executed

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Find the requirements_tools directory
find_tools_dir() {
    local current_dir="$PWD"
    while [ "$current_dir" != "/" ]; do
        if [ -f "$current_dir/teacher/requirements_tools/detect_requirements.py" ]; then
            echo "$current_dir/teacher/requirements_tools"
            return 0
        fi
        current_dir="$(dirname "$current_dir")"
    done
    
    # Fallback: check if we're in the tools directory itself
    if [ -f "$PWD/detect_requirements.py" ]; then
        echo "$PWD"
        return 0
    fi
    
    echo ""
    return 1
}

# Main function to check requirements
check_and_update_requirements() {
    local project_dir="${1:-.}"
    local auto_update="${2:-false}"
    
    echo -e "${BLUE}🔍 Checking Python requirements...${NC}"
    
    # Find tools directory with detect_requirements.py
    TOOLS_DIR=$(find_tools_dir)
    
    if [ -z "$TOOLS_DIR" ]; then
        echo -e "${YELLOW}⚠️  detect_requirements.py not found${NC}"
        echo "   Skipping requirements detection"
        return 0
    fi
    
    DETECT_SCRIPT="${TOOLS_DIR}/detect_requirements.py"
    
    # Check if requirements.txt exists
    if [ -f "$project_dir/requirements.txt" ]; then
        echo -e "${GREEN}✓${NC} Found existing requirements.txt"
        
        # Backup existing file
        cp "$project_dir/requirements.txt" "$project_dir/requirements.txt.backup"
        echo -e "${BLUE}ℹ${NC}  Backed up to requirements.txt.backup"
    else
        echo -e "${YELLOW}⚠${NC}  No requirements.txt found"
    fi
    
    # Generate new requirements
    echo -e "${BLUE}🔧${NC} Detecting requirements from Python files..."
    
    TEMP_REQS=$(mktemp)
    python3 "$DETECT_SCRIPT" "$project_dir" -o "$TEMP_REQS" --no-versions 2>&1
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error detecting requirements${NC}"
        rm -f "$TEMP_REQS"
        return 1
    fi
    
    # Compare with existing requirements.txt
    if [ -f "$project_dir/requirements.txt.backup" ]; then
        echo ""
        echo -e "${BLUE}📊 Comparing with existing requirements...${NC}"
        
        # Extract package names (ignore comments and versions)
        OLD_PACKAGES=$(grep -v '^#' "$project_dir/requirements.txt.backup" | grep -v '^$' | sed 's/==.*//' | sed 's/>=.*//' | sort)
        NEW_PACKAGES=$(grep -v '^#' "$TEMP_REQS" | grep -v '^$' | sed 's/==.*//' | sed 's/>=.*//' | sort)
        
        # Find new packages
        NEW_ONLY=$(comm -13 <(echo "$OLD_PACKAGES") <(echo "$NEW_PACKAGES"))
        # Find removed packages
        REMOVED=$(comm -23 <(echo "$OLD_PACKAGES") <(echo "$NEW_PACKAGES"))
        
        if [ -n "$NEW_ONLY" ]; then
            echo -e "${GREEN}➕ New packages detected:${NC}"
            echo "$NEW_ONLY" | while read pkg; do echo "   - $pkg"; done
        fi
        
        if [ -n "$REMOVED" ]; then
            echo -e "${YELLOW}➖ Packages no longer detected:${NC}"
            echo "$REMOVED" | while read pkg; do echo "   - $pkg"; done
        fi
        
        if [ -z "$NEW_ONLY" ] && [ -z "$REMOVED" ]; then
            echo -e "${GREEN}✓${NC} No changes detected"
        fi
    fi
    
    # Update or prompt
    if [ "$auto_update" = "true" ]; then
        mv "$TEMP_REQS" "$project_dir/requirements.txt"
        echo -e "\n${GREEN}✅ requirements.txt updated${NC}"
    else
        echo ""
        echo -e "${YELLOW}❓ Would you like to update requirements.txt? [y/N]${NC}"
        read -r response
        
        if [[ "$response" =~ ^[Yy]$ ]]; then
            mv "$TEMP_REQS" "$project_dir/requirements.txt"
            echo -e "${GREEN}✅ requirements.txt updated${NC}"
        else
            rm -f "$TEMP_REQS"
            # Restore backup
            if [ -f "$project_dir/requirements.txt.backup" ]; then
                mv "$project_dir/requirements.txt.backup" "$project_dir/requirements.txt"
            fi
            echo -e "${BLUE}ℹ${NC}  Keeping existing requirements.txt"
        fi
    fi
    
    # Clean up backup
    rm -f "$project_dir/requirements.txt.backup"
    
    echo ""
    return 0
}

# If executed directly (not sourced)
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    PROJECT_DIR="${1:-.}"
    AUTO_UPDATE="${2:-false}"
    
    if [ "$PROJECT_DIR" = "--help" ] || [ "$PROJECT_DIR" = "-h" ]; then
        cat << EOF
Usage: ./check_requirements.sh [PROJECT_DIR] [AUTO_UPDATE]

Check and optionally update requirements.txt for a Python project.

ARGUMENTS:
    PROJECT_DIR     Directory to check (default: current directory)
    AUTO_UPDATE     'true' to update without prompting (default: false)

EXAMPLES:
    # Check current directory (interactive)
    ./check_requirements.sh
    
    # Check specific directory
    ./check_requirements.sh modelling/data_warehouse
    
    # Auto-update without prompting
    ./check_requirements.sh . true

INTEGRATION:
    # In your setup.sh script:
    source ./check_requirements.sh
    check_and_update_requirements "." true

EOF
        exit 0
    fi
    
    check_and_update_requirements "$PROJECT_DIR" "$AUTO_UPDATE"
fi
