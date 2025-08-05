"""
Test client for Miles AI system
"""

import urllib.request
import urllib.parse
import json

def test_server():
    """Test if server is running"""
    
    base_url = "http://localhost:8000"
    
    print("Testing Miles Deutscher AI System...")
    print("=" * 60)
    
    # Test 1: Check status
    try:
        response = urllib.request.urlopen(f"{base_url}/api/status")
        status = json.loads(response.read().decode())
        
        print("\nSystem Status:")
        print(f"  Training examples: {status['training_examples']}")
        print(f"  Latest tweets: {status['latest_tweets']}")
        print(f"  Last update: {status['last_update']}")
        print(f"  Currently updating: {status['is_updating']}")
        
        if status['style_patterns']:
            print(f"\nStyle Analysis:")
            print(f"  Average length: {status['style_patterns']['avg_length']:.0f} chars")
            print(f"  Structures: {status['style_patterns']['structures']}")
        
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return
    
    # Test 2: Generate tweets
    print("\n" + "=" * 60)
    print("\nTesting Tweet Generation:")
    
    test_inputs = [
        "bitcoin halving coming soon",
        "is this the bear market?",
        "everyone wants lambos",
        "gm"
    ]
    
    for test_input in test_inputs:
        try:
            # Prepare request
            data = json.dumps({"input": test_input}).encode()
            req = urllib.request.Request(
                f"{base_url}/api/generate",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Get response
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            
            print(f"\nInput: '{test_input}'")
            print(f"Output: {result['output']}")
            print(f"Length: {result['length']} chars | Structure: {result['structure']}")
            
        except Exception as e:
            print(f"Error generating tweet: {e}")
    
    print("\n" + "=" * 60)
    print("\nServer is running! Open http://localhost:8000 in your browser")

if __name__ == "__main__":
    test_server()