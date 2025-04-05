#!/bin/bash

# filepath: /Users/joseibay/Documents/SupplyChainManagement/test_with_docker.sh

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
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ | grep 200 > /dev/null
if [ $? -eq 0 ]; then
    echo "Root endpoint test passed!"
else
    echo "Root endpoint test failed!"
    docker logs supplychain-dev
    docker stop supplychain-dev
    docker rm supplychain-dev
    exit 1
fi

# Test another endpoint (e.g., /customers/)
echo "Testing the /customers/ endpoint..."
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8080/customers/ \
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
    }' | grep 201 > /dev/null
if [ $? -eq 0 ]; then
    echo "/customers/ endpoint test passed!"
else
    echo "/customers/ endpoint test failed!"
    docker logs supplychain-dev
    docker stop supplychain-dev
    docker rm supplychain-dev
    exit 1
fi

# Stop and remove the container
echo "Stopping and removing the application container..."
docker stop supplychain-dev
docker rm supplychain-dev

echo "All tests passed!"


curl -v -X POST http://localhost:8080/customers/ \
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
    }'