"""
Deploy and Test Miles Deutscher AI System
Ensures everything is working before launching
"""

import os
import sys
import json
import subprocess
import time
import urllib.request
import socket

def check_port_available(port=8000):
    """Check if port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def check_file_exists(filename):
    """Check if required file exists"""
    return os.path.exists(filename)

def check_api_credentials():
    """Check if API credentials are set"""
    # Check .env file
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            return 'TWITTER_BEARER_TOKEN' in content
    
    # Check environment variable
    return os.getenv('TWITTER_BEARER_TOKEN') is not None

def test_twitter_api():
    """Test Twitter API connection"""
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN', 
        'AAAAAAAAAAAAAAAAAAAAAJi13QEAAAAAghVwuLws1YdchbwCAkUjqqwu6oc%3DeImrILD6DNOvuOdZiH42oFM3Ww7zTLYaiz1onypLp8XNzCskQ7')
    
    url = "https://api.twitter.com/2/users/by/username/milesdeutscher"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {bearer_token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return 'data' in data
    except:
        return False

def run_deployment_checks():
    """Run all deployment checks"""
    print("🔍 Running deployment checks...")
    print("=" * 60)
    
    checks = {
        "Python version": sys.version.split()[0],
        "Working directory": os.getcwd(),
        "Port 8000 available": check_port_available(),
        "data.jsonl exists": check_file_exists('data.jsonl'),
        "API credentials": check_api_credentials(),
        "Main system file": check_file_exists('miles_ai_complete_system.py'),
    }
    
    all_good = True
    
    for check, result in checks.items():
        if isinstance(result, bool):
            status = "✅ PASS" if result else "❌ FAIL"
            if not result:
                all_good = False
        else:
            status = f"ℹ️  {result}"
        
        print(f"{check:.<30} {status}")
    
    # Test API connection
    print("\n🌐 Testing Twitter API connection...")
    api_test = test_twitter_api()
    print(f"API Connection:................ {'✅ PASS' if api_test else '⚠️  FAIL (will use offline mode)'}")
    
    print("=" * 60)
    
    return all_good

def create_test_data():
    """Create test data if none exists"""
    if not os.path.exists('data.jsonl'):
        print("\n📝 Creating sample training data...")
        
        sample_data = [
            {
                "prompt": "Write a tweet in the style of Miles Deutscher:",
                "completion": " The overhang is just noise.\n\nWhat matters: macro liquidity meeting a narrative so powerful it makes bagholders capitulate.\n\nUntil then? We're all just trading chop."
            },
            {
                "prompt": "Write a tweet in the style of Miles Deutscher:",
                "completion": " Real talk: Your bags aren't pumping because we need BOTH macro tailwind AND a fresh narrative.\n\nOne without the other = underwhelming pumps and cope posting.\n\nMath ain't mathing without both."
            },
            {
                "prompt": "Write a tweet in the style of Miles Deutscher:",
                "completion": " Everyone's waiting for alt season like it's Christmas morning.\n\nNews flash: Santa needs two things - macro liquidity and a narrative bigger than your bags.\n\nNo gifts without both."
            }
        ]
        
        with open('data.jsonl', 'w', encoding='utf-8') as f:
            for item in sample_data:
                f.write(json.dumps(item) + '\n')
        
        print("✅ Created sample data.jsonl with 3 examples")

def launch_system():
    """Launch the complete system"""
    print("\n🚀 Launching Miles Deutscher AI Complete System...")
    print("=" * 60)
    
    # Set environment variable for bearer token if not set
    if not os.getenv('TWITTER_BEARER_TOKEN'):
        os.environ['TWITTER_BEARER_TOKEN'] = 'AAAAAAAAAAAAAAAAAAAAAJi13QEAAAAAghVwuLws1YdchbwCAkUjqqwu6oc%3DeImrILD6DNOvuOdZiH42oFM3Ww7zTLYaiz1onypLp8XNzCskQ7'
    
    print("\n📡 Starting server on http://localhost:8000")
    print("\n⏳ Please wait a few seconds for the server to start...")
    print("\n📋 Once started, you can:")
    print("   1. Open http://localhost:8000 in your browser")
    print("   2. Enter any text to generate Miles-style tweets")
    print("   3. Watch real-time updates in the progress log")
    print("   4. Monitor system status and metrics")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("\n" + "=" * 60)
    
    # Launch the system
    try:
        subprocess.run([sys.executable, 'miles_ai_complete_system.py'])
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped successfully")

def main():
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║     Miles Deutscher AI - Deployment & Testing        ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run deployment checks
    if not run_deployment_checks():
        print("\n⚠️  Some checks failed, but continuing anyway...")
    
    # Create test data if needed
    create_test_data()
    
    # Prompt to continue
    print("\n" + "=" * 60)
    response = input("\n🎯 Ready to launch the system? (y/n): ")
    
    if response.lower() == 'y':
        launch_system()
    else:
        print("\n❌ Deployment cancelled")
        print("\nTo manually start the system later, run:")
        print("   python miles_ai_complete_system.py")

if __name__ == "__main__":
    main()