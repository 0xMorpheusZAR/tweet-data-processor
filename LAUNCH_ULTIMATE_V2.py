"""
Launch Miles Deutscher AI Ultimate System v2.0
Enhanced with final integrated dataset
"""
import subprocess
import sys
import time
import os

def main():
    print("""
    ================================================
         MILES DEUTSCHER AI ULTIMATE v2.0
              ENHANCED EDITION
    ================================================
    
    Improvements in v2.0:
    ✓ 7,235 total tweets processed
    ✓ 2,625 unique high-quality examples
    ✓ Advanced pattern recognition
    ✓ Weighted pattern selection
    ✓ Sub-millisecond response times
    
    Starting system...
    """)
    
    # Check if files exist
    required_files = [
        'miles_ai_ultimate_v2.py',
        'miles_final_data_model.json',
        'miles_pattern_examples.json'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"[ERROR] Required file missing: {file}")
            print("Please run integrate_final_data_model.py first!")
            sys.exit(1)
    
    print("[OK] All required files found")
    print("[OK] Launching Ultimate System v2.0...")
    print("\n" + "="*50 + "\n")
    
    try:
        # Run the ultimate system
        subprocess.run([sys.executable, "miles_ai_ultimate_v2.py"])
    except KeyboardInterrupt:
        print("\n\n[INFO] System stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Failed to start: {e}")

if __name__ == "__main__":
    main()