#!/bin/bash

# ============================================================================
# Azure Event Hubs Setup - Install All Dependencies
# ============================================================================
# This script installs:
# - Azure CLI
# - Python 3.9+
# - Python Azure libraries
# - Git (if needed)
# ============================================================================

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        DISTRO=$(lsb_release -si 2>/dev/null || echo "Unknown")
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    echo $OS
}

# ============================================================================
# 1. Update System Package Manager
# ============================================================================
install_dependencies() {
    print_header "Step 1: Updating System Package Manager"
    
    OS=$(detect_os)
    
    if [ "$OS" = "linux" ]; then
        print_warning "Detected Linux (Ubuntu/Debian)"
        sudo apt-get update
        sudo apt-get install -y curl wget gnupg lsb-release ca-certificates
        print_success "Linux packages updated"
        
    elif [ "$OS" = "macos" ]; then
        print_warning "Detected macOS"
        
        # Check if Homebrew is installed
        if ! command -v brew &> /dev/null; then
            print_warning "Homebrew not found. Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            print_success "Homebrew installed"
        else
            print_success "Homebrew already installed"
        fi
        
        brew update
        print_success "macOS packages updated"
        
    else
        print_error "Unsupported OS: $OS"
        print_warning "Please install dependencies manually for your OS"
        exit 1
    fi
}

# ============================================================================
# 2. Install Python 3.9+
# ============================================================================
install_python() {
    print_header "Step 2: Installing Python 3.9+"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        print_success "Python 3 already installed: $PYTHON_VERSION"
        
        # Check if version is 3.9+
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 9 ]; then
            print_success "Python version meets requirements (3.9+)"
        else
            print_warning "Python version is older than 3.9, upgrading..."
            OS=$(detect_os)
            
            if [ "$OS" = "linux" ]; then
                sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
                sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
            elif [ "$OS" = "macos" ]; then
                brew install python@3.11
            fi
            print_success "Python upgraded"
        fi
    else
        print_warning "Python 3 not found. Installing..."
        
        OS=$(detect_os)
        
        if [ "$OS" = "linux" ]; then
            sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
        elif [ "$OS" = "macos" ]; then
            brew install python@3.11
        fi
        
        print_success "Python 3.11 installed"
    fi
    
    # Install pip
    if ! command -v pip3 &> /dev/null; then
        print_warning "pip3 not found. Installing..."
        python3 -m ensurepip --upgrade
    fi
    
    print_success "pip3 is ready"
    pip3 --version
}

# ============================================================================
# 3. Install Azure CLI
# ============================================================================
install_azure_cli() {
    print_header "Step 3: Installing Azure CLI"
    
    if command -v az &> /dev/null; then
        AZ_VERSION=$(az version --query '["azure-cli"]' -o tsv 2>/dev/null || echo "unknown")
        print_success "Azure CLI already installed: $AZ_VERSION"
    else
        print_warning "Azure CLI not found. Installing..."
        
        OS=$(detect_os)
        
        if [ "$OS" = "linux" ]; then
            # Install Azure CLI on Linux
            curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
            
        elif [ "$OS" = "macos" ]; then
            # Install Azure CLI on macOS
            brew install azure-cli
        fi
        
        print_success "Azure CLI installed"
    fi
    
    # Verify installation
    az version
}

# ============================================================================
# 4. Install Python Virtual Environment
# ============================================================================
setup_virtual_env() {
    print_header "Step 4: Setting Up Python Virtual Environment"
    
    VENV_DIR="azure-eventhub-venv"
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at $VENV_DIR"
        read -p "Do you want to recreate it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
            python3 -m venv "$VENV_DIR"
            print_success "Virtual environment recreated"
        fi
    else
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created at $VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
}

# ============================================================================
# 5. Install Python Azure Libraries
# ============================================================================
install_python_azure_libs() {
    print_header "Step 5: Installing Python Azure Libraries"
    
    # Upgrade pip
    pip3 install --upgrade pip setuptools wheel
    print_success "pip, setuptools, and wheel upgraded"
    
    # Create requirements file
    cat > azure_requirements.txt << 'EOF'
# Azure SDK for Event Hubs
azure-eventhub==5.11.6

# Azure CLI libraries
azure-cli==2.56.0
azure-cli-core==2.56.0

# Additional utilities
python-dotenv==1.0.0
requests==2.31.0
jsonschema==4.21.1

# For development/testing
pytest==7.4.4
pytest-asyncio==0.23.2
EOF
    
    print_warning "Installing Python packages (this may take a minute)..."
    pip3 install -r azure_requirements.txt
    
    print_success "All Python Azure libraries installed"
}

# ============================================================================
# 6. Install Git (Optional but recommended)
# ============================================================================
install_git() {
    print_header "Step 6: Installing Git (Optional)"
    
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_success "Git already installed: $GIT_VERSION"
    else
        print_warning "Git not found. Installing..."
        
        OS=$(detect_os)
        
        if [ "$OS" = "linux" ]; then
            sudo apt-get install -y git
        elif [ "$OS" = "macos" ]; then
            brew install git
        fi
        
        print_success "Git installed"
    fi
}

# ============================================================================
# 7. Verify All Installations
# ============================================================================
verify_installation() {
    print_header "Step 7: Verifying All Installations"
    
    echo -e "\n${BLUE}Checking installed tools:${NC}\n"
    
    # Python
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✓ Python 3:${NC} $(python3 --version)"
    else
        echo -e "${RED}✗ Python 3: NOT FOUND${NC}"
    fi
    
    # pip
    if command -v pip3 &> /dev/null; then
        echo -e "${GREEN}✓ pip3:${NC} $(pip3 --version)"
    else
        echo -e "${RED}✗ pip3: NOT FOUND${NC}"
    fi
    
    # Azure CLI
    if command -v az &> /dev/null; then
        echo -e "${GREEN}✓ Azure CLI:${NC} $(az --version | head -1)"
    else
        echo -e "${RED}✗ Azure CLI: NOT FOUND${NC}"
    fi
    
    # Git
    if command -v git &> /dev/null; then
        echo -e "${GREEN}✓ Git:${NC} $(git --version)"
    else
        echo -e "${YELLOW}⚠ Git: NOT FOUND (optional)${NC}"
    fi
    
    # Azure Python SDK
    if python3 -c "import azure.eventhub" 2>/dev/null; then
        echo -e "${GREEN}✓ azure-eventhub:${NC} SDK available"
    else
        echo -e "${RED}✗ azure-eventhub: NOT FOUND${NC}"
    fi
    
    # Python-dotenv
    if python3 -c "import dotenv" 2>/dev/null; then
        echo -e "${GREEN}✓ python-dotenv:${NC} SDK available"
    else
        echo -e "${RED}✗ python-dotenv: NOT FOUND${NC}"
    fi
}

# ============================================================================
# 8. Azure CLI Login
# ============================================================================
azure_login() {
    print_header "Step 8: Logging into Azure"
    
    read -p "Do you want to login to Azure now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        az login
        print_success "Azure login successful"
    else
        print_warning "Skipping Azure login. You can login later with: az login"
    fi
}

# ============================================================================
# 9. Create Helper Scripts
# ============================================================================
create_helper_scripts() {
    print_header "Step 9: Creating Helper Scripts"
    
    # Create activate script
    cat > activate_venv.sh << 'EOF'
#!/bin/bash
source azure-eventhub-venv/bin/activate
echo "Virtual environment activated!"
echo "To deactivate, run: deactivate"
EOF
    
    chmod +x activate_venv.sh
    print_success "Created activate_venv.sh"
    
    # Create requirements template
    cat > .env.example << 'EOF'
# Azure Event Hubs Configuration
SOURCE_CONNECTION_STRING=Endpoint=sb://YOUR_NAMESPACE.servicebus.windows.net/;SharedAccessKeyName=StudentReadPolicy;SharedAccessKey=YOUR_KEY
DEST_CONNECTION_STRING=Endpoint=sb://YOUR_NAMESPACE.servicebus.windows.net/;SharedAccessKeyName=StudentWritePolicy;SharedAccessKey=YOUR_KEY
EOF
    
    print_success "Created .env.example template"
}

# ============================================================================
# 10. Display Summary
# ============================================================================
display_summary() {
    print_header "Installation Summary"
    
    cat << 'EOF'

✓ All dependencies installed successfully!

Next Steps:
─────────────────────────────────────────────────────────────────

1. Activate Virtual Environment:
   source activate_venv.sh
   OR
   source azure-eventhub-venv/bin/activate

2. Configure Azure Credentials:
   az login

3. Set Up Environment Variables:
   cp .env.example .env
   # Edit .env with your Azure Event Hub connection strings

4. Verify Azure Setup:
   az account show

5. Run Infrastructure Setup:
   ./setup_infrastructure.sh

6. Populate Sample Data (teacher only):
   python populate_events.py

7. Run Student Code:
   python student_solution.py

─────────────────────────────────────────────────────────────────

Useful Commands:
─────────────────────────────────────────────────────────────────
az login                          # Login to Azure
az account show                   # Show current account
az eventhubs namespace list       # List all Event Hub namespaces
az group list                     # List all resource groups
deactivate                        # Exit virtual environment

Documentation:
─────────────────────────────────────────────────────────────────
Azure CLI: https://docs.microsoft.com/cli/azure
Azure SDK: https://github.com/Azure/azure-sdk-for-python
Event Hubs: https://learn.microsoft.com/en-us/azure/event-hubs/

EOF
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    print_header "Azure Event Hubs - Complete Setup"
    
    echo "OS Detected: $(detect_os)"
    echo ""
    
    # Run all installation steps
    install_dependencies
    install_python
    install_azure_cli
    setup_virtual_env
    install_python_azure_libs
    install_git
    create_helper_scripts
    verify_installation
    azure_login
    display_summary
    
    print_success "Setup completed successfully!"
}

# Run main function
main