#!/bin/bash

# filepath: /Users/joseibay/Documents/SupplyChainManagement/run_docker_tests.sh

# Exit immediately if a command exits with a non-zero status
set -e

# Function to clean up the Docker container
cleanup() {
    echo "Stopping and removing the application container..."
    docker stop supplychain-app || true
    docker rm supplychain-app || true
}

# Trap to ensure cleanup runs on script exit
trap cleanup EXIT

# Build the Docker image
echo "Building the Docker image..."
docker build -t supplychain-dev .

# Run the application container in detached mode
echo "Starting the application container..."
docker run -d --name supplychain-app -p 8080:8080 supplychain-dev

# Wait for the application to start
echo "Waiting for the application to start..."
sleep 5

# Test the root endpoint
echo "Testing the root endpoint..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ | grep 200 > /dev/null; then
    echo "Root endpoint test passed!"
else
    echo "Root endpoint test failed!"
    docker logs supplychain-app
    exit 1
fi

# Test the /customers/ endpoint
echo "Testing the /customers/ endpoint..."
if curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8080/customers/ \
    -H "Content-Type: application/json" \
    -d '{
        "company_name": "Test Company",
        "customer_type": "manufacturer",
        "tax_id": "TX123456999",
        "registration_date": "2025-03-31T12:00:00",
        "contact_email": "test@company.com",
        "contact_phone": "+1234567890",
        "address": "123 Test St",
        "credit_score": 800,
        "approved_credit_limit": 500000.0
    }' | grep 201 > /dev/null; then
    echo "/customers/ endpoint test passed!"
else
    echo "/customers/ endpoint test failed!"
    docker logs supplychain-app
    exit 1
fi

# Additional tests can be added here...

echo "All tests passed!"