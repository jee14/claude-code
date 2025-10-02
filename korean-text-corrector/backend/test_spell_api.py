#!/usr/bin/env python3
"""Test Pusan University spell checker API"""
import requests
from bs4 import BeautifulSoup

# Test text with obvious errors
test_text = "안녕하세요? 됬는지 확인해볼게욬ㅋ"

print(f"Testing with: {test_text}\n")

# Call API
response = requests.post(
    "http://speller.cs.pusan.ac.kr/results",
    data={'text1': test_text},
    timeout=10
)

print(f"Status: {response.status_code}")
print(f"\nResponse HTML (first 1000 chars):")
print(response.text[:1000])
print("\n" + "="*60)

# Parse HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Look for common error markers
print("\nLooking for error markers:")
print(f"- Elements with class 'error': {len(soup.find_all('span', {'class': 'error'}))}")
print(f"- Elements with class 'green': {len(soup.find_all('span', {'class': 'green'}))}")
print(f"- All span elements: {len(soup.find_all('span'))}")

# Print all span elements
print("\nAll span elements:")
for span in soup.find_all('span')[:10]:  # First 10 only
    print(f"  - class={span.get('class')}, text={span.get_text()[:50]}")
