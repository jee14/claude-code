#!/usr/bin/env python3
"""Test script for Korean correction functionality"""
from correction_rules import quick_correct, detailed_correct

# Test cases
test_cases = [
    "됬다",  # Should be 됐다
    "할수있어요",  # Should be 할 수 있어요
    "안녕하세요할수있습니다",  # Should fix spacing
    "어떻해",  # Should be 어떡해
]

print("=" * 60)
print("Testing Korean Text Correction")
print("=" * 60)

for test in test_cases:
    print(f"\nOriginal: {test}")
    corrected = quick_correct(test)
    print(f"Corrected: {corrected}")
    print(f"Changed: {test != corrected}")

print("\n" + "=" * 60)
print("Detailed Test")
print("=" * 60)

detailed = detailed_correct("됬다 할수있어요")
print(f"\nOriginal: {detailed['original']}")
print(f"Corrected: {detailed['corrected']}")
print(f"Number of corrections: {detailed['statistics']['num_corrections']}")
print(f"Corrections made: {detailed['corrections']}")
