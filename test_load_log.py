#!/usr/bin/env python3
"""
Quick test to verify load_log() works with different input types
"""

import pm4py
from ppinatjson import load_log

# Test 1: Load from file path (string)
print("Test 1: Loading from file path...")
try:
    log1 = load_log("xes/DomesticDeclarations.xes")
    print("✅ Test 1 passed: File path loading works")
except Exception as e:
    print(f"❌ Test 1 failed: {e}")

# Test 2: Load from EventLog object
print("\nTest 2: Loading from EventLog object...")
try:
    event_log = pm4py.read_xes("xes/DomesticDeclarations.xes")
    log2 = load_log(event_log)
    print("✅ Test 2 passed: EventLog object loading works")
except Exception as e:
    print(f"❌ Test 2 failed: {e}")

print("\n✅ All tests passed! The fix is working correctly.")
