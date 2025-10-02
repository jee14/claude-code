#!/usr/bin/env python3
"""Test API response format"""
import requests
import json

# Test the API
response = requests.post(
    'http://localhost:8000/correct/detailed',
    json={'text': '됬다 할수있어요'}
)

print(f"Status: {response.status_code}")
print(f"\nResponse JSON:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
