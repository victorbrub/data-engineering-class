# Azure PostgreSQL Flexible Server Deployment Script (PowerShell)
# This script creates an Azure PostgreSQL Flexible Server instance
# optimized for students and data warehouse scenarios

# Track if resource group was created
$script:RG_CREATED = $false

# Configuration Variables - Update these as needed
$subscriptionId = $env:AZURE_SUBSCRIPTION_ID  # Your Azure subscription ID
$resourceGroup = if ($env:RESOURCE_GROUP) { $env:RESOURCE_GROUP } else { "pg-datawarehouse-rg" }
# Regions available for Azure for Students subscriptions
$studentRegions = @("spaincentral", "germanywestcentral", "switzerlandnorth", "francecentral", "swedencentral")
$location = if ($env:LOCATION) { $env:LOCATION } else { "" }  # If set, will only try this location
$serverName = if ($env:SERVER_NAME) { $env:SERVER_NAME } else { "pg-datawarehouse-$(Get-Random -Maximum 99999)" }
$adminUser = if ($env:ADMIN_USER) { $env:ADMIN_USER } else { "pgadmin" }
$databaseName = if ($env:DATABASE_NAME) { $env:DATABASE_NAME } else { "datawarehouse" }
$skuName = if ($env:SKU_NAME) { $env:SKU_NAME } else { "Standard_B1ms" }
$storageSize = if ($env:STORAGE_SIZE) { $env:STORAGE_SIZE } else { 32 }
$backupRetention = if ($env:BACKUP_RETENTION) { $env:BACKUP_RETENTION } else { 7 }
$postgresVersion = if ($env:POSTGRES_VERSION) { $env:POSTGRES_VERSION } else { "15" }

# Error handling - cleanup on failure
$ErrorActionPreference = "Stop"
trap {
    if ($script:RG_CREATED) {
        Write-Host "Deployment failed. Cleaning up resources..." -ForegroundColor Red
        Write-Host "Deleting resource group: $resourceGroup" -ForegroundColor Yellow
        az group delete --name $resourceGroup --yes --no-wait
        Write-Host "Cleanup initiated. Resources will be deleted in the background." -ForegroundColor Yellow
    }
    break
}

Write-Host "=== Azure PostgreSQL Flexible Server Deployment ===" -ForegroundColor Green
Write-Host ""

# Check if Azure CLI is installed
try {
    az version | Out-Null
} catch {
    Write-Host "Error: Azure CLI is not installed." -ForegroundColor Red
    Write-Host "Please install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
}

# Login check
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
try {
    az account show | Out-Null
} catch {
    Write-Host "Not logged in. Initiating login..." -ForegroundColor Yellow
    az login
}

# Set subscription if provided
if ($subscriptionId) {
    Write-Host "Setting subscription to: $subscriptionId" -ForegroundColor Yellow
    az account set --subscription $subscriptionId
}

# Display current subscription
$currentSub = az account show --query name -o tsv
Write-Host "Using subscription: $currentSub" -ForegroundColor Green
Write-Host ""

# Register Microsoft.DBforPostgreSQL resource provider
Write-Host "Registering Microsoft.DBforPostgreSQL resource provider..." -ForegroundColor Yellow
az provider register --namespace Microsoft.DBforPostgreSQL --wait
if ($LASTEXITCODE -eq 0) {
    Write-Host "Resource provider registered successfully" -ForegroundColor Green
} else {
    Write-Host "Note: Resource provider registration may take a few minutes to complete" -ForegroundColor Yellow
}
Write-Host ""

# Prompt for admin password if not set
if (-not $env:ADMIN_PASSWORD) {
    $securePassword = Read-Host "Enter PostgreSQL admin password (min 8 characters, must contain uppercase, lowercase, numbers)" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    $adminPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
    
    if ($adminPassword.Length -lt 8) {
        Write-Host "Password must be at least 8 characters long" -ForegroundColor Red
        exit 1
    }
} else {
    $adminPassword = $env:ADMIN_PASSWORD
}

# Create Resource Group
Write-Host "Creating resource group: $resourceGroup in $location..." -ForegroundColor Yellow
az group create `
    --name $resourceGroup `
    --location $location `
    --tags Environment=Development Project=DataWarehouse

$script:RG_CREATED = $true
Write-Host "✓ Resource group created" -ForegroundColor Green
Write-Host ""

# Create PostgreSQL Flexible Server
Write-Host "Creating PostgreSQL Flexible Server: $serverName..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes..."
az postgres flexible-server create `
    --resource-group $resourceGroup `
    --name $serverName `
    --location $location `
    --admin-user $adminUser `
    --admin-password $adminPassword `
    --sku-name $skuName `
    --tier Burstable `
    --storage-size $storageSize `
    --version $postgresVersion `
    --backup-retention $backupRetention `
    --yes

Write-Host "✓ PostgreSQL server created" -ForegroundColor Green
Write-Host ""

# Configure firewall to allow access from Azure services
Write-Host "Configuring firewall rules..." -ForegroundColor Yellow
az postgres flexible-server firewall-rule create `
    --resource-group $resourceGroup `
    --name $serverName `
    --rule-name "AllowAllAzureServices" `
    --start-ip-address "0.0.0.0" `
    --end-ip-address "0.0.0.0"

# Get client IP and add firewall rule
try {
    $clientIP = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing).Content
    if ($clientIP) {
        Write-Host "Adding firewall rule for your IP: $clientIP..." -ForegroundColor Yellow
        az postgres flexible-server firewall-rule create `
            --resource-group $resourceGroup `
            --name $serverName `
            --rule-name "ClientIP" `
            --start-ip-address $clientIP `
            --end-ip-address $clientIP
    }
} catch {
    Write-Host "Could not determine client IP automatically" -ForegroundColor Yellow
}

Write-Host "✓ Firewall rules configured" -ForegroundColor Green
Write-Host ""

# Create database
Write-Host "Creating database: $databaseName..." -ForegroundColor Yellow
az postgres flexible-server db create `
    --resource-group $resourceGroup `
    --server-name $serverName `
    --database-name $databaseName

Write-Host "✓ Database created" -ForegroundColor Green
Write-Host ""

# Get connection information
$serverFqdn = az postgres flexible-server show `
    --resource-group $resourceGroup `
    --name $serverName `
    --query "fullyQualifiedDomainName" -o tsv

# Display deployment information
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║       PostgreSQL Flexible Server Deployment Complete      ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Connection Information:" -ForegroundColor Yellow
Write-Host "  Server Name:     $serverName"
Write-Host "  Server FQDN:     $serverFqdn"
Write-Host "  Admin User:      $adminUser"
Write-Host "  Database:        $databaseName"
Write-Host "  Port:            5432"
Write-Host "  SSL Mode:        require"
Write-Host ""
Write-Host "Connection String:" -ForegroundColor Yellow
Write-Host "  host=$serverFqdn port=5432 dbname=$databaseName user=$adminUser password=<password> sslmode=require"
Write-Host ""
Write-Host "Python Connection String:" -ForegroundColor Yellow
Write-Host "  postgresql://$adminUser:<password>@$serverFqdn:5432/$databaseName?sslmode=require"
Write-Host ""
Write-Host "Save these values in your config.yaml file!" -ForegroundColor Yellow
Write-Host ""

# Create config file
$configFile = ".\config.yaml"
if (-not (Test-Path $configFile)) {
    Write-Host "Creating config.yaml template..." -ForegroundColor Yellow
    @"
# PostgreSQL Connection Configuration
database:
  host: "$serverFqdn"
  port: 5432
  database: "$databaseName"
  user: "$adminUser"
  password: ""  # Add your password here
  sslmode: "require"

# Azure Resource Information
azure:
  resource_group: "$resourceGroup"
  server_name: "$serverName"
  location: "$location"

# Data upload settings
upload:
  chunk_size: 1000
  data_directory: "./data"
"@ | Out-File -FilePath $configFile -Encoding UTF8
    Write-Host "✓ Config file created: $configFile" -ForegroundColor Green
    Write-Host "  Remember to add your password to the config file!" -ForegroundColor Red
}

Write-Host ""
Write-Host "Deployment completed successfully!" -ForegroundColor Green
