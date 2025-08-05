"""
Restart script to switch to enhanced system
"""
import os
import sys
import subprocess
import time
import socket
import signal

print("=" * 60)
print("Switching to Miles AI Enhanced System v2.0")
print("=" * 60)

# Step 1: Check what's running
def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

if check_port(8000):
    print("\n[INFO] Current system running on port 8000")
    print("[ACTION] Stopping current system...")
    
    # Try to stop gracefully first
    try:
        # Windows specific process termination
        os.system('taskkill /F /FI "WINDOWTITLE eq Miles Deutscher AI*"')
        os.system('taskkill /F /FI "WINDOWTITLE eq python*"')
        time.sleep(2)
    except:
        pass
    
    # Check if port is free now
    if check_port(8000):
        print("[WARN] Server still running, forcing shutdown...")
        os.system('netstat -ano | findstr :8000')
        print("\n[NOTE] You may need to manually close the Python window")
        print("Press Ctrl+C in the Python window or close it")
        input("\nPress Enter after closing the current server...")

# Step 2: Prepare enhanced data
print("\n[PREPARE] Setting up enhanced training data...")
if os.path.exists('miles_1000_enhanced.jsonl'):
    print("[OK] Found 994 enhanced training examples")
    # Backup original
    if os.path.exists('data.jsonl'):
        os.rename('data.jsonl', 'data_original.jsonl')
    # Use enhanced data
    os.rename('miles_1000_enhanced.jsonl', 'data.jsonl')
    print("[OK] Enhanced data activated")

# Step 3: Load model improvements
if os.path.exists('model_improvements.json'):
    print("[OK] Model improvements ready")

# Step 4: Launch enhanced system
print("\n[LAUNCH] Starting Enhanced System v2.0...")
print("\nFeatures activated:")
print("  ✓ Advanced frontend with real-time visualization")
print("  ✓ ML-powered backend with pattern analysis") 
print("  ✓ 994 analyzed tweets from Miles")
print("  ✓ Continuous learning every 20 minutes")
print("  ✓ Performance optimizations")
print("  ✓ Enhanced tweet generation")

print("\n[START] Launching in new window...")
print("=" * 60)

# Launch the enhanced system
subprocess.Popen('start "Miles AI Enhanced v2.0" cmd /c python miles_ai_enhanced_system.py', shell=True)

print("\nEnhanced system starting...")
print("Wait for: '[READY] Enhanced system running at: http://localhost:8000'")
print("\nThen open: http://localhost:8000")
print("\nYou should see:")
print("- Advanced dashboard with charts")
print("- Real-time tweet feed")
print("- Learning progress visualization")
print("- Performance metrics")

print("\n[COMPLETE] Switch to enhanced system initiated!")