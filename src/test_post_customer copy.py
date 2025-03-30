import json
import requests
from pathlib import Path
import os
import sys

def post_customers():
    # Read customer data
    myfile = Path(__file__).parent / 'customer.json'
    with open(myfile, 'r') as f:
        mylist = json.load(f)
        assert isinstance(mylist, list), "mylist should be a list"

    # API endpoint configuration
    url = "http://0.0.0.0:8000/customers/batch"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    # Send POST request
    try:
        response = requests.post(url, headers=headers, json=mylist)
        response.raise_for_status()  # Raise exception for non-200 status codes
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    post_customers()


