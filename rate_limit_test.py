#!/usr/bin/env python
"""
Test rate limit handling improvements for MindsDB Agent
"""
import sys

# Read the current file
with open('mindsdb_agent.py', 'r') as f:
    content = f.read()

# Show current rate limit config
print("Current rate limit configuration:")
print("="*60)
lines = content.split('\n')
for i, line in enumerate(lines[167:191], start=168):
    print(f"{i}: {line}")
print("="*60)

# Calculate wait times for current and proposed configs
print("\nCurrent backoff: max_retries=3, wait_time=(2**retry)*2")
print("Wait times: 2s, 4s, 8s (total: 14s)")

print("\nProposed backoff: max_retries=5, wait_time=(2**retry)*3")
print("Wait times: 3s, 6s, 12s, 24s, 48s (total: 93s)")
