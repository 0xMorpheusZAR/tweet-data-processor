"""
Miles Deutscher AI - Batch Testing
Tests multiple inputs automatically
"""

import sys
sys.path.append('.')
from test_miles_ai import MilesAITester

def run_batch_tests():
    """Run batch tests with various inputs"""
    
    print("""
    ========================================================
         Miles Deutscher AI - Batch Testing Results       
    ========================================================
    """)
    
    tester = MilesAITester()
    
    # Test cases covering different styles
    test_cases = [
        # Market Analysis
        ("btc looking bullish", "Market Bullish"),
        ("ethereum bear market", "Market Bearish"),
        ("SOL price action", "Market Neutral"),
        
        # Questions
        ("is this the top?", "Question"),
        ("thoughts on defi summer?", "Question"),
        ("when moon?", "Question"),
        
        # Philosophical
        ("everyone wants to be rich", "Philosophical"),
        ("best time to build", "Philosophical"),
        ("worst time to wait", "Philosophical"),
        
        # Quick Takes
        ("gm", "Quick Take"),
        ("wagmi", "Quick Take"),
        ("cope harder", "Quick Take"),
        
        # Complex Inputs
        ("bitcoin halving approaching what should I do", "Complex"),
        ("layer 2 scaling solutions", "Technical"),
        ("nft market dead or sleeping", "Analysis")
    ]
    
    for input_text, category in test_cases:
        print(f"\n{'='*60}")
        print(f"Category: {category}")
        print(f"Input: '{input_text}'")
        print("-"*40)
        
        # Generate tweet
        tweet = tester.generate_miles_tweet(input_text)
        print("Output:")
        print(tweet)
        
        # Show metrics
        print(f"\nMetrics:")
        print(f"  - Length: {len(tweet)} chars (Twitter limit: 280)")
        print(f"  - Has ticker: {'Yes' if '$' in tweet else 'No'}")
        print(f"  - Line breaks: {tweet.count(chr(10))}")
        print(f"  - Style match: {'YES' if len(tweet) <= 280 else 'NO'}")
    
    print(f"\n{'='*60}")
    print("Testing complete!")
    print(f"Total test cases: {len(test_cases)}")
    print(f"All outputs within Twitter limit: {all(len(tester.generate_miles_tweet(tc[0])) <= 280 for tc in test_cases)}")

if __name__ == "__main__":
    run_batch_tests()