#!/bin/bash
# Helper script to detect requirements across all projects

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DETECT_SCRIPT="${SCRIPT_DIR}/detect_requirements.py"

# Find the repository root (parent of parent of this script's directory)
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Requirements Detection Tool${NC}"
echo -e "${BLUE}==============================${NC}\n"

# Function to detect requirements for a project
detect_project_requirements() {
    local project_dir=$1
    local project_name=$2
    
    echo -e "${YELLOW}📦 Processing: ${project_name}${NC}"
    echo "   Path: ${project_dir}"
    
    if [ -d "${project_dir}" ]; then
        cd "${project_dir}"
        python3 "${DETECT_SCRIPT}" --no-versions
        echo ""
    else
        echo -e "   ⚠️  Directory not found, skipping"
        echo ""
    fi
}

# Main function
main() {
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        cat << EOF
Usage: ./update_all_requirements.sh [OPTIONS]

Detect and update requirements.txt for all projects in the workspace.

OPTIONS:
    -h, --help          Show this help message
    --project <path>    Update only specific project directory
    --with-versions     Include version pinning

EXAMPLES:
    # Update all projects without versions
    ./update_all_requirements.sh
    
    # Update specific project
    ./update_all_requirements.sh --project modelling/data_warehouse
    
    # Update with version pinning
    ./update_all_requirements.sh --with-versions

EOF
        exit 0
    fi
    
    local version_flag="--no-versions"
    local specific_project=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --with-versions)
                version_flag=""
                shift
                ;;
            --project)
                specific_project="$2"
                shift 2
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # If specific project is provided
    if [ -n "${specific_project}" ]; then
        project_path="${REPO_ROOT}/${specific_project}"
        detect_project_requirements "${project_path}" "$(basename ${specific_project})"
        exit 0
    fi
    
    # Projects to process (relative to repository root)
    declare -A projects=(
        ["Data Warehouse"]="modelling/data_warehouse"
        ["ETL Star Schema"]="modelling/python-etlfact-dim"
        ["Data Quality Lab"]="pre-post_processing/cleaning_data_lab"
        ["Fundamentals Ex1"]="fundamentals/exercise1"
        ["Tab Processor"]="fundamentals/exercise2/tab_processor"
    )
    
    # Process each project
    for project_name in "${!projects[@]}"; do
        project_path="${REPO_ROOT}/${projects[$project_name]}"
        detect_project_requirements "${project_path}" "${project_name}"
    done
    
    echo -e "${GREEN}✅ All projects processed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review the generated requirements.txt files"
    echo "  2. Install packages: pip install -r requirements.txt"
    echo "  3. Test your applications"
}

# Run main function
main "$@"
