#!/usr/bin/env python
"""
Test Anthropic API Access
Run this to check if your API key is working
"""
import os
import sys
from pathlib import Path

# Load .env file from parent directory
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Check if anthropic is installed
try:
    from anthropic import Anthropic
except ImportError:
    print('ERROR: anthropic package not installed')
    print('Need to run: pip install anthropic')
    sys.exit(1)

# Check for API key in environment
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print('ERROR: ANTHROPIC_API_KEY not found in environment')
    print('Need to add it to .env file')
    sys.exit(1)

print(f'Found API key: {api_key[:20]}...')

# Try API call
try:
    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model='claude-sonnet-4-5-20250929',
        max_tokens=100,
        messages=[{'role': 'user', 'content': 'Hello'}]
    )
    print('SUCCESS: API access working!')
    print(f'Response: {response.content[0].text}')
    print(f'Usage - Input tokens: {response.usage.input_tokens}, Output tokens: {response.usage.output_tokens}')
except Exception as e:
    print(f'ERROR: API call failed: {e}')
    sys.exit(1)
