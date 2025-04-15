#!/bin/bash

# API Health Check Script for Eventia Backend
# This script checks if all API endpoints are responding correctly

API_BASE="http://localhost:3004/api"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to check an endpoint
check_endpoint() {
  local endpoint=$1
  local method=${2:-GET}
  local data=$3
  local name=$4
  
  echo -e "${YELLOW}Checking ${name}... ${NC}"
  
  if [ "$method" == "GET" ]; then
    response=$(curl -s -o response.json -w "%{http_code}" -X ${method} ${API_BASE}${endpoint})
  else
    response=$(curl -s -o response.json -w "%{http_code}" -X ${method} -H "Content-Type: application/json" -d "${data}" ${API_BASE}${endpoint})
  fi
  
  if [[ $response -ge 200 && $response -lt 300 ]]; then
    echo -e "${GREEN}✓ ${name} is working (${response})${NC}"
    echo "Response preview:"
    head -n 5 response.json | cat
    echo "..."
  else
    echo -e "${RED}✗ ${name} failed with status ${response}${NC}"
    cat response.json
  fi
  echo ""
}

echo "========================================="
echo "Eventia Backend API Health Check"
echo "API Base URL: ${API_BASE}"
echo "========================================="
echo ""

# Check base endpoints
check_endpoint "/health" "GET" "" "Health Check"
check_endpoint "/config/public" "GET" "" "Public Config"
check_endpoint "/events" "GET" "" "List Events"

# Check an individual event (assumes at least one event exists)
event_id=$(curl -s ${API_BASE}/events | jq -r '.[0].id')
if [ -n "$event_id" ] && [ "$event_id" != "null" ]; then
  check_endpoint "/events/${event_id}" "GET" "" "Single Event Details"
fi

# Check payment settings
check_endpoint "/payment-settings" "GET" "" "Payment Settings"

# Clean up
rm -f response.json

echo "========================================="
echo "Health check completed"
echo "=========================================" 