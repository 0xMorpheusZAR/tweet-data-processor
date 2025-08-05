"""
Miles AI System Status Checker and Launcher
"""
import os
import json
import urllib.request
import urllib.error
import webbrowser

print("""
================================================================
         MILES AI SYSTEM STATUS CHECK                    
================================================================
""")

# Check what's deployed
print("\n[CHECKING] Deployment Status...")

completed_phases = {
    "Frontend (Enhanced UI)": os.path.exists('miles_ai_enhanced_system.py'),
    "Backend (ML-Powered)": os.path.exists('miles_ai_enhanced_system.py'),
    "QA Testing Suite": os.path.exists('miles_ai_qa_performance.py'),
    "Performance Optimizations": os.path.exists('optimization_config.json') or os.path.exists('model_improvements.json'),
    "1000 Tweets Analysis": os.path.exists('miles_1000_enhanced.jsonl'),
    "Security & Deployment": os.path.exists('miles_ai_production_deploy.py'),
}

print("\nCompleted Phases:")
for phase, completed in completed_phases.items():
    status = "[OK]" if completed else "[--]"
    print(f"  {status} {phase}")

# Check training data
if os.path.exists('miles_1000_enhanced.jsonl'):
    with open('miles_1000_enhanced.jsonl', 'r', encoding='utf-8') as f:
        tweet_count = len(f.readlines())
    print(f"\n[DATA] Enhanced training data: {tweet_count} tweets")
    
if os.path.exists('miles_1000_analysis.json'):
    with open('miles_1000_analysis.json', 'r') as f:
        analysis = json.load(f)
    print(f"[ANALYSIS] Optimal structure: {analysis.get('optimal_parameters', {}).get('preferred_structure', 'Unknown')}")
    print(f"[ANALYSIS] Top topics: {', '.join(list(analysis.get('top_topics', {}).keys())[:3])}")

# Check if server is running
print("\n[SERVER] Checking if system is running...")
try:
    req = urllib.request.Request('http://localhost:8000/api/status')
    with urllib.request.urlopen(req, timeout=2) as response:
        data = json.loads(response.read().decode())
    
    print(f"[ONLINE] System is running!")
    print(f"  - Training examples: {data.get('training_examples', 0)}")
    print(f"  - Mode: {'Enhanced' if data.get('training_examples', 0) > 900 else 'Basic'}")
    
    # Check which system
    if 'system' in data and 'version' in data['system']:
        print(f"  - Version: {data['system']['version']}")
    
except Exception as e:
    print(f"[OFFLINE] System not running or wrong version")

print("\n" + "="*60)
print("\nOPTIONS:")
print("1. Open enhanced preview in browser")
print("2. Launch enhanced system now") 
print("3. View deployment summary")
print("4. Run QA tests")
print("5. Exit")

choice = input("\nSelect option (1-5): ")

if choice == "1":
    print("\nOpening enhanced preview...")
    webbrowser.open('file:///' + os.path.abspath('enhanced_preview.html'))

elif choice == "2":
    print("\nLaunching enhanced system...")
    print("\nNOTE: If a system is already running, close it first!")
    print("The enhanced version has:")
    print("  - Advanced dashboard")
    print("  - Real-time visualizations")
    print("  - 994 tweet training data")
    print("  - All optimizations active")
    
    input("\nPress Enter to launch...")
    os.system('python LAUNCH_ENHANCED_NOW.py')

elif choice == "3":
    if os.path.exists('DEPLOYMENT_SUMMARY.md'):
        print("\nOpening deployment summary...")
        os.system('notepad DEPLOYMENT_SUMMARY.md')
    else:
        print("\nDeployment summary not found")

elif choice == "4":
    print("\nRunning QA tests...")
    os.system('python miles_ai_qa_performance.py')

print("\n[DONE] Status check complete!")