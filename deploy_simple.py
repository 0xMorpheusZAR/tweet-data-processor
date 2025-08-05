"""
Simple deployment script for Miles Deutscher AI
"""

import os
import sys
import json
import subprocess

print("\n============================================================")
print("     Miles Deutscher AI - Deployment & Testing")
print("============================================================\n")

# Check current directory
print("Current directory:", os.getcwd())

# Check if main file exists
if os.path.exists('miles_ai_complete_system.py'):
    print("Main system file: OK")
else:
    print("ERROR: miles_ai_complete_system.py not found!")
    sys.exit(1)

# Check/create data file
if not os.path.exists('data.jsonl'):
    print("\nCreating sample training data...")
    
    sample_data = [
        {
            "prompt": "Write a tweet in the style of Miles Deutscher:",
            "completion": " The overhang is just noise.\n\nWhat matters: macro liquidity meeting a narrative so powerful it makes bagholders capitulate.\n\nUntil then? We're all just trading chop."
        }
    ]
    
    with open('data.jsonl', 'w', encoding='utf-8') as f:
        for item in sample_data:
            f.write(json.dumps(item) + '\n')
    
    print("Created data.jsonl")

# Set bearer token
os.environ['TWITTER_BEARER_TOKEN'] = 'AAAAAAAAAAAAAAAAAAAAAJi13QEAAAAAghVwuLws1YdchbwCAkUjqqwu6oc%3DeImrILD6DNOvuOdZiH42oFM3Ww7zTLYaiz1onypLp8XNzCskQ7'

print("\n============================================================")
print("Starting Miles Deutscher AI System...")
print("============================================================")
print("\nServer will be available at: http://localhost:8000")
print("\nFeatures:")
print("  - Text input to Miles-style tweets")
print("  - Real-time Twitter data updates")
print("  - Continuous learning")
print("  - Progress logging")
print("\nPress Ctrl+C to stop the server")
print("\n============================================================\n")

# Launch the system
try:
    subprocess.run([sys.executable, 'miles_ai_complete_system.py'])
except KeyboardInterrupt:
    print("\n\nServer stopped.")