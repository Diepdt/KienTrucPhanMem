#!/bin/bash

# Master Seed Script - Run all seed operations
# Usage: bash run_all_seeds.sh

set -e

echo "╔════════════════════════════════════════════╗"
echo "║     🌱 Seeding All Data Into Database     ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_ROOT="$( dirname "$SCRIPT_DIR" )"

echo -e "${BLUE}Workspace Root: ${WORKSPACE_ROOT}${NC}"
echo ""

# Function to run a seed script
run_seed() {
    local script_name=$1
    local service_name=$2
    
    echo -e "${BLUE}→ Running ${script_name}...${NC}"
    
    if [ -f "${SCRIPT_DIR}/${script_name}" ]; then
        cd "${WORKSPACE_ROOT}"
        python "${SCRIPT_DIR}/${script_name}"
        echo -e "${GREEN}✓ ${script_name} complete${NC}"
    else
        echo -e "${YELLOW}⚠ ${script_name} not found${NC}"
    fi
    echo ""
}

# Run all seeds
run_seed "seed_staff.py" "staff-service"
run_seed "seed_manager.py" "manager-service"
run_seed "seed_customer.py" "customer-service"
run_seed "seed_categories.py" "catalog-service"

echo "╔════════════════════════════════════════════╗"
echo "║      ✓ All Seeds Completed Successfully    ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Created Accounts:"
echo "  • staff@gmail.com (Staff) / 12345678"
echo "  • manager@gmail.com (Manager) / 12345678"
echo "  • customer@gmail.com (Customer) / 12345678"
echo ""
echo "Created Categories:"
echo "  • Book: 4 categories"
echo "  • Cloth: 3 categories"
echo "  • Laptop: 4 categories"
echo "  • Mobile: 4 categories"
echo ""
echo "Next steps:"
echo "  1. Visit http://localhost:8000/admin/ to login"
echo "  2. Use any of the created accounts to test"
echo "  3. Check categories in the admin panel"
