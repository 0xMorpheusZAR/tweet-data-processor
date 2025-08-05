"""
Direct launcher for Enhanced Miles AI System
"""
import os
import shutil
import json

print("""
================================================================
    LAUNCHING MILES AI ENHANCED SYSTEM v2.0
================================================================

This version includes ALL completed phases:
- Enhanced Frontend with real-time visualization
- ML-powered Backend with pattern analysis  
- 994 tweets analyzed from Miles Deutscher
- QA Testing & Performance optimizations
- Security monitoring & deployment automation
================================================================
""")

# Use enhanced training data if available
if os.path.exists('miles_1000_enhanced.jsonl') and not os.path.exists('data_enhanced_active.flag'):
    print("[UPGRADE] Activating 994 enhanced training examples...")
    shutil.copy('data.jsonl', 'data_original_backup.jsonl')
    shutil.copy('miles_1000_enhanced.jsonl', 'data.jsonl')
    # Create flag file
    with open('data_enhanced_active.flag', 'w') as f:
        f.write('Enhanced data active')
    print("[OK] Enhanced training data activated!")

# Set environment for enhanced features
os.environ['MILES_AI_MODE'] = 'ENHANCED'
os.environ['ENABLE_ADVANCED_UI'] = 'true'
os.environ['ENABLE_REALTIME_LEARNING'] = 'true'

print("\n[STARTING] Enhanced system on http://localhost:8000")
print("\nNOTE: If port 8000 is busy, the system will use port 8001")
print("\nStarting in 3 seconds...")

import time
time.sleep(3)

# Import and run the enhanced system
import miles_ai_enhanced_system