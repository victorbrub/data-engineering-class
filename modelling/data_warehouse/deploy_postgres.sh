#!/bin/bash
# Azure PostgreSQL Flexible Server Deployment Script (Bash)
# This script creates an Azure PostgreSQL Flexible Server instance
# optimized for students and data warehouse scenarios

# Note: Not using 'set -e' because we want to handle errors explicitly
# Track if resource group was created
RG_CREATED=false
DEPLOYMENT_SUCCESS=false

# Configuration Variables - Update these as needed
SUBSCRIPTION_ID="${AZURE_SUBSCRIPTION_ID:-}"  # Your Azure subscription ID
RESOURCE_GROUP="${RESOURCE_GROUP:-pg-datawarehouse-rg}"
# Regions available for Azure for Students subscriptions
STUDENT_REGIONS=("spaincentral" "germanywestcentral" "switzerlandnorth" "francecentral" "swedencentral")
LOCATION="${LOCATION:-}"  # If set, will only try this location
SERVER_NAME="${SERVER_NAME:-pg-datawarehouse-$RANDOM}"  # Must be globally unique
ADMIN_USER="${ADMIN_USER:-pgadmin}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-}"  # Will prompt if not set
DATABASE_NAME="${DATABASE_NAME:-datawarehouse}"
SKU_NAME="${SKU_NAME:-Standard_B1ms}"  # Burstable tier for students
STORAGE_SIZE="${STORAGE_SIZE:-32}"  # GB (minimum 32)
BACKUP_RETENTION="${BACKUP_RETENTION:-7}"  # Days
POSTGRES_VERSION="${POSTGRES_VERSION:-15}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Azure PostgreSQL Flexible Server Deployment ===${NC}"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed.${NC}"
    echo "Please install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login check
echo -e "${YELLOW}Checking Azure login status...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Not logged in. Initiating login...${NC}"
    az login
fi

# Set subscription if provided
if [ -n "$SUBSCRIPTION_ID" ]; then
    echo -e "${YELLOW}Setting subscription to: $SUBSCRIPTION_ID${NC}"
    az account set --subscription "$SUBSCRIPTION_ID"
fi

# Display current subscription
CURRENT_SUB=$(az account show --query name -o tsv)
echo -e "${GREEN}Using subscription: $CURRENT_SUB${NC}"
echo ""

# Register Microsoft.DBforPostgreSQL resource provider
echo -e "${YELLOW}Registering Microsoft.DBforPostgreSQL resource provider...${NC}"
az provider register --namespace Microsoft.DBforPostgreSQL --wait
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Resource provider registered successfully${NC}"
else
    echo -e "${YELLOW}Note: Resource provider registration may take a few minutes to complete${NC}"
fi
echo ""

# Prompt for admin password if not set
if [ -z "$ADMIN_PASSWORD" ]; then
    echo -e "${YELLOW}Enter PostgreSQL admin password (min 8 characters, must contain uppercase, lowercase, numbers):${NC}"
    read -s ADMIN_PASSWORD
    echo ""
    if [ ${#ADMIN_PASSWORD} -lt 8 ]; then
        echo -e "${RED}Password must be at least 8 characters long${NC}"
        exit 1
    fi
fi

# Determine regions to try
if [ -n "$LOCATION" ]; then
    REGIONS_TO_TRY=("$LOCATION")
    echo -e "${YELLOW}Using specified location: $LOCATION${NC}"
else
    REGIONS_TO_TRY=("${STUDENT_REGIONS[@]}")
    echo -e "${YELLOW}Will try common student regions until deployment succeeds${NC}"
fi
echo ""

# Try deploying in each region until successful
DEPLOYMENT_SUCCESS=false
for REGION in "${REGIONS_TO_TRY[@]}"; do
    echo -e "${YELLOW}Attempting deployment in region: $REGION${NC}"
    
    # Create Resource Group
    echo -e "${YELLOW}Creating resource group: $RESOURCE_GROUP in $REGION...${NC}"
    if az group create \
        --name "$RESOURCE_GROUP" \
        --location "$REGION" \
        --tags Environment=Development Project=DataWarehouse > /dev/null 2>&1; then
        
        RG_CREATED=true
        echo -e "${GREEN}Resource group created${NC}"
        
        # Create PostgreSQL Flexible Server
        echo -e "${YELLOW}Creating PostgreSQL Flexible Server: $SERVER_NAME...${NC}"
        echo "This may take 5-10 minutes..."
        
        # Capture output and error
        CREATE_OUTPUT=$(az postgres flexible-server create \
            --resource-group "$RESOURCE_GROUP" \
            --name "$SERVER_NAME" \
            --location "$REGION" \
            --admin-user "$ADMIN_USER" \
            --admin-password "$ADMIN_PASSWORD" \
            --sku-name "$SKU_NAME" \
            --tier Burstable \
            --storage-size "$STORAGE_SIZE" \
            --version "$POSTGRES_VERSION" \
            --backup-retention "$BACKUP_RETENTION" \
            --yes 2>&1)
        
        if [ $? -eq 0 ]; then
            DEPLOYMENT_SUCCESS=true
            LOCATION="$REGION"  # Save successful region
            echo -e "${GREEN}PostgreSQL server created successfully in $REGION${NC}"
            echo ""
            break
        else
            echo -e "${RED}Failed to create PostgreSQL server in $REGION${NC}"
            echo -e "${YELLOW}Error details:${NC}"
            echo "$CREATE_OUTPUT" | grep -i "error\|message\|code" | head -5
            echo ""
            echo -e "${YELLOW}Cleaning up and trying next region...${NC}"
            
            # Wait a moment for Azure to update
            sleep 3
            
            # Delete resource group and wait for completion
            az group delete --name "$RESOURCE_GROUP" --yes --no-wait
            
            # Wait for deletion to initiate
            sleep 5
            
            RG_CREATED=false
        fi
    else
        echo -e "${RED}Failed to create resource group in $REGION${NC}"
    fi
    echo ""
done

# Check if deployment was successful
if [ "$DEPLOYMENT_SUCCESS" = false ]; then
    echo -e "${RED}Failed to deploy PostgreSQL server in any available region.${NC}"
    echo -e "${YELLOW}Regions tried: ${REGIONS_TO_TRY[*]}${NC}"
    echo ""
    echo "Possible solutions:"
    echo "1. Check your Azure for Students subscription limits"
    echo "2. Try a different server SKU: export SKU_NAME='Standard_B2s'"
    echo "3. Verify your subscription has available quota"
    echo "4. Try deploying through Azure Portal to see detailed error messages"
    echo "5. Check if PostgreSQL Flexible Server is available in your student subscription"
    
    # Final cleanup if resource group exists
    if [ "$RG_CREATED" = true ]; then
        echo ""
        echo -e "${YELLOW}Cleaning up remaining resources...${NC}"
        az group delete --name "$RESOURCE_GROUP" --yes --no-wait
    fi
    
    exit 1
fi

echo -e "${GREEN}Deployment successful in region: $LOCATION${NC}"
echo ""

# Configure firewall to allow access from Azure services
echo -e "${YELLOW}Configuring firewall rules...${NC}"
az postgres flexible-server firewall-rule create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$SERVER_NAME" \
    --rule-name "AllowAllAzureServices" \
    --start-ip-address "0.0.0.0" \
    --end-ip-address "0.0.0.0"

# Get client IP and add firewall rule
CLIENT_IP=$(curl -s https://api.ipify.org)
if [ -n "$CLIENT_IP" ]; then
    echo -e "${YELLOW}Adding firewall rule for your IP: $CLIENT_IP...${NC}"
    az postgres flexible-server firewall-rule create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$SERVER_NAME" \
        --rule-name "ClientIP" \
        --start-ip-address "$CLIENT_IP" \
        --end-ip-address "$CLIENT_IP"
fi

echo -e "${GREEN}✓ Firewall rules configured${NC}"
echo ""

# Create database
echo -e "${YELLOW}Creating database: $DATABASE_NAME...${NC}"
az postgres flexible-server db create \
    --resource-group "$RESOURCE_GROUP" \
    --server-name "$SERVER_NAME" \
    --database-name "$DATABASE_NAME"

echo -e "${GREEN}✓ Database created${NC}"
echo ""

# Get connection information
SERVER_FQDN=$(az postgres flexible-server show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$SERVER_NAME" \
    --query "fullyQualifiedDomainName" -o tsv)

# Display deployment information
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       PostgreSQL Flexible Server Deployment Complete      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Connection Information:${NC}"
echo "  Server Name:     $SERVER_NAME"
echo "  Server FQDN:     $SERVER_FQDN"
echo "  Admin User:      $ADMIN_USER"
echo "  Database:        $DATABASE_NAME"
echo "  Port:            5432"
echo "  SSL Mode:        require"
echo ""
echo -e "${YELLOW}Connection String:${NC}"
echo "  host=$SERVER_FQDN port=5432 dbname=$DATABASE_NAME user=$ADMIN_USER password=<password> sslmode=require"
echo ""
echo -e "${YELLOW}Python Connection String:${NC}"
echo "  postgresql://$ADMIN_USER:<password>@$SERVER_FQDN:5432/$DATABASE_NAME?sslmode=require"
echo ""
echo -e "${YELLOW}Save these values in your config.yaml file!${NC}"
echo ""

# Create config file
CONFIG_FILE="./config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}Creating config.yaml template...${NC}"
    cat > "$CONFIG_FILE" << EOF
# PostgreSQL Connection Configuration
database:
  host: "$SERVER_FQDN"
  port: 5432
  database: "$DATABASE_NAME"
  user: "$ADMIN_USER"
  password: ""  # Add your password here
  sslmode: "require"

# Azure Resource Information
azure:
  resource_group: "$RESOURCE_GROUP"
  server_name: "$SERVER_NAME"
  location: "$LOCATION"

# Data upload settings
upload:
  chunk_size: 1000
  data_directory: "./data"
EOF
    echo -e "${GREEN}✓ Config file created: $CONFIG_FILE${NC}"
    echo -e "${RED}  Remember to add your password to the config file!${NC}"
fi

echo ""
echo -e "${GREEN}Deployment completed successfully!${NC}"
