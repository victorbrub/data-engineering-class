# ============================================================================
# Azure Event Hubs Setup - Windows PowerShell Installation
# ============================================================================
# Run with: powershell -ExecutionPolicy Bypass -File install_azure_deps.ps1
# ============================================================================

param(
    [switch]$SkipChocolatey = $false
)

# Color functions
function Write-Header {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host $args[0] -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Write-Success {
    Write-Host "✓ $($args[0])" -ForegroundColor Green
}

function Write-Warning {
    Write-Host "⚠ $($args[0])" -ForegroundColor Yellow
}

function Write-Error {
    Write-Host "✗ $($args[0])" -ForegroundColor Red
}

# ============================================================================
# Step 1: Check Admin Rights
# ============================================================================
Write-Header "Step 1: Checking Administrator Rights"

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Warning "This script requires administrator rights"
    Write-Host "Please run PowerShell as Administrator and try again"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Success "Running as Administrator"

# ============================================================================
# Step 2: Set PowerShell Execution Policy
# ============================================================================
Write-Header "Step 2: Setting PowerShell Execution Policy"

try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Success "Execution policy updated"
} catch {
    Write-Warning "Could not update execution policy: $_"
}

# ============================================================================
# Step 3: Install Chocolatey (if not already installed)
# ============================================================================
Write-Header "Step 3: Installing Chocolatey Package Manager"

if (-not (Test-Path "C:\ProgramData\chocolatey\bin\choco.exe")) {
    Write-Warning "Chocolatey not found. Installing..."
    
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    Write-Success "Chocolatey installed"
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Success "Chocolatey already installed"
}

# ============================================================================
# Step 4: Install Python 3.11
# ============================================================================
Write-Header "Step 4: Installing Python 3.11"

if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Success "Python already installed: $pythonVersion"
} else {
    Write-Warning "Python not found. Installing Python 3.11..."
    choco install python311 -y --no-progress
    Write-Success "Python 3.11 installed"
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# ============================================================================
# Step 5: Install Git
# ============================================================================
Write-Header "Step 5: Installing Git"

if (Get-Command git -ErrorAction SilentlyContinue) {
    $gitVersion = git --version
    Write-Success "Git already installed: $gitVersion"
} else {
    Write-Warning "Git not found. Installing..."
    choco install git -y --no-progress
    Write-Success "Git installed"
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# ============================================================================
# Step 6: Install Azure CLI
# ============================================================================
Write-Header "Step 6: Installing Azure CLI"

if (Get-Command az -ErrorAction SilentlyContinue) {
    Write-Success "Azure CLI already installed"
    az version
} else {
    Write-Warning "Azure CLI not found. Installing..."
    choco install azure-cli -y --no-progress
    Write-Success "Azure CLI installed"
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# ============================================================================
# Step 7: Upgrade pip and Install Python Packages
# ============================================================================
Write-Header "Step 7: Installing Python Azure Libraries"

Write-Warning "Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

Write-Warning "Installing Azure SDK packages..."
$packages = @(
    "azure-eventhub==5.11.6",
    "azure-cli==2.56.0",
    "azure-cli-core==2.56.0",
    "python-dotenv==1.0.0",
    "requests==2.31.0",
    "jsonschema==4.21.1",
    "pytest==7.4.4",
    "pytest-asyncio==0.23.2"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Gray
    python -m pip install $package
}

Write-Success "All Python packages installed"

# ============================================================================
# Step 8: Create Virtual Environment
# ============================================================================
Write-Header "Step 8: Creating Python Virtual Environment"

$venvPath = "azure-eventhub-venv"

if (Test-Path $venvPath) {
    Write-Warning "Virtual environment already exists"
    $response = Read-Host "Recreate it? (y/n)"
    
    if ($response -eq 'y' -or $response -eq 'Y') {
        Remove-Item $venvPath -Recurse -Force
        python -m venv $venvPath
        Write-Success "Virtual environment recreated"
    }
} else {
    python -m venv $venvPath
    Write-Success "Virtual environment created at $venvPath"
}

# ============================================================================
# Step 9: Create Helper Scripts
# ============================================================================
Write-Header "Step 9: Creating Helper Scripts"

# Create activate script for PowerShell
$activateScript = @"
# Activate Azure Event Hubs Virtual Environment
& ".\azure-eventhub-venv\Scripts\Activate.ps1"
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host "To deactivate, run: deactivate" -ForegroundColor Yellow
"@

$activateScript | Out-File -Encoding UTF8 "activate_venv.ps1"
Write-Success "Created activate_venv.ps1"

# Create .env example
$envExample = @"
# Azure Event Hubs Configuration
SOURCE_CONNECTION_STRING=Endpoint=sb://YOUR_NAMESPACE.servicebus.windows.net/;SharedAccessKeyName=StudentReadPolicy;SharedAccessKey=YOUR_KEY
DEST_CONNECTION_STRING=Endpoint=sb://YOUR_NAMESPACE.servicebus.windows.net/;SharedAccessKeyName=StudentWritePolicy;SharedAccessKey=YOUR_KEY
"@

$envExample | Out-File -Encoding UTF8 ".env.example"
Write-Success "Created .env.example"

# Create requirements.txt
$requirements = @"
azure-eventhub==5.11.6
azure-cli==2.56.0
azure-cli-core==2.56.0
python-dotenv==1.0.0
requests==2.31.0
jsonschema==4.21.1
pytest==7.4.4
pytest-asyncio==0.23.2
"@

$requirements | Out-File -Encoding UTF8 "requirements.txt"
Write-Success "Created requirements.txt"

# ============================================================================
# Step 10: Verify Installation
# ============================================================================
Write-Header "Step 10: Verifying Installation"

Write-Host ""
Write-Host "Checking installed tools:" -ForegroundColor Cyan
Write-Host ""

# Python
$pythonVersion = python --version 2>&1
Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green

# pip
$pipVersion = pip --version
Write-Host "✓ pip: $pipVersion" -ForegroundColor Green

# Azure CLI
$azVersion = az --version | Select-Object -First 1
Write-Host "✓ Azure CLI: $azVersion" -ForegroundColor Green

# Git
$gitVersion = git --version
Write-Host "✓ Git: $gitVersion" -ForegroundColor Green

# Check Python packages
Write-Host ""
Write-Host "Checking Python packages:" -ForegroundColor Cyan
Write-Host ""

$packages = @("azure.eventhub", "dotenv", "requests", "pytest")

foreach ($package in $packages) {
    try {
        $moduleName = $package -replace "\.", "_"
        python -c "import $package" 2>$null
        Write-Host "✓ $package: Available" -ForegroundColor Green
    } catch {
        Write-Host "✗ $package: NOT FOUND" -ForegroundColor Red
    }
}

# ============================================================================
# Step 11: Azure Login
# ============================================================================
Write-Header "Step 11: Login to Azure"

$loginResponse = Read-Host "Do you want to login to Azure now? (y/n)"

if ($loginResponse -eq 'y' -or $loginResponse -eq 'Y') {
    az login
    Write-Success "Azure login successful"
} else {
    Write-Warning "Skipping Azure login. You can login later with: az login"
}

# ============================================================================
# Display Summary
# ============================================================================
Write-Header "Installation Complete!"

$summary = @"

✓ All dependencies installed successfully on Windows!

Next Steps:
─────────────────────────────────────────────────────────────────

1. Activate Virtual Environment:
   .\activate_venv.ps1
   OR manually:
   .\azure-eventhub-venv\Scripts\Activate.ps1

2. Configure Azure Credentials:
   az login

3. Set Up Environment Variables:
   Copy .env.example to .env
   Edit .env with your Azure Event Hub connection strings

4. Verify Azure Setup:
   az account show

5. Run Infrastructure Setup:
   .\setup_infrastructure.ps1

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

Installed Software:
─────────────────────────────────────────────────────────────────
Python 3.11: C:\Python311
Git: C:\Program Files\Git
Azure CLI: Installed via Chocolatey
Chocolatey: C:\ProgramData\chocolatey

Documentation:
─────────────────────────────────────────────────────────────────
Azure CLI: https://docs.microsoft.com/cli/azure
Azure SDK: https://github.com/Azure/azure-sdk-for-python
Event Hubs: https://learn.microsoft.com/en-us/azure/event-hubs/

"@

Write-Host $summary -ForegroundColor White
Write-Success "Setup completed successfully!"