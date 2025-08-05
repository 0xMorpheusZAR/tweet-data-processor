import urllib.request
import json
import time

print("\nTesting Miles AI System...")
time.sleep(3)  # Give server time to start

try:
    # Test status endpoint
    req = urllib.request.Request("http://localhost:8000/api/status")
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode())
    
    print(f"\n[OK] System Online")
    print(f"  - Training examples: {data['system']['training_examples']}")
    print(f"  - Model version: {data['system']['version']}")
    
    # Test generation
    test_input = {"input": "bitcoin halving impact on alts"}
    req = urllib.request.Request(
        "http://localhost:8000/api/generate",
        data=json.dumps(test_input).encode(),
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req, timeout=5) as response:
        result = json.loads(response.read().decode())
    
    print(f"\n[OK] Generation Test Passed")
    print(f"  Generated: {result['output'][:60]}...")
    print(f"  Confidence: {result['confidence']}")
    
except Exception as e:
    print(f"\n[ERROR] System test failed: {e}")
