"""
Miles Deutscher AI - Simple Testing Script
Test input/output dynamics without web server
"""
import json
import random
import re
class MilesAITester:
    def __init__(self):
        self.load_patterns()
    def load_patterns(self):
        """Load Miles's tweet patterns from training data"""
        self.tweets = []
        try:
            with open('data.jsonl', 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line)
                    self.tweets.append(data['completion'].strip())
            print(f"Loaded {len(self.tweets)} training examples")
        except:
            print("No training data found, using default patterns")
    def generate_miles_tweet(self, user_input):
        """Generate Miles-style tweet from input"""
        input_lower = user_input.lower()
        # Detect intent
        if any(word in input_lower for word in ['bull', 'pump', 'moon']):
            return self.generate_bullish_tweet(user_input)
        elif any(word in input_lower for word in ['bear', 'dump', 'crash']):
            return self.generate_bearish_tweet(user_input)
        elif '?' in user_input:
            return self.generate_question_response(user_input)
        elif any(word in input_lower for word in ['best', 'worst', 'everyone']):
            return self.generate_philosophical_tweet(user_input)
        else:
            return self.generate_general_tweet(user_input)
    def generate_bullish_tweet(self, input_text):
        """Generate bullish market tweet"""
        ticker = self.extract_ticker(input_text) or "BTC"
        templates = [
            f"${ticker} looking absolutely fire right now.\n\nClean break above resistance with volume.\n\nUp only ",
            f"Ser, ${ticker} is about to melt faces.\n\nAccumulation phase complete.\n\nNGMI if you're not paying attention. ",
            f"${ticker} chart telling a beautiful story.\n\nHigher lows, higher highs.\n\nBullish. ",
            f"\n\n${ticker} absolutely sending it.\n\nUp only sers."
        ]
        return random.choice(templates)
    def generate_bearish_tweet(self, input_text):
        """Generate bearish market tweet"""
        ticker = self.extract_ticker(input_text) or "BTC"
        templates = [
            f"${ticker} showing major weakness here.\n\nSupport broken, no buyers in sight.\n\nProtect your capital. ",
            f"Warning: ${ticker} about to get rekt.\n\nMomentum fading fast.\n\nThis is not the dip to buy. ",
            f"${ticker} chart looking absolutely cooked.\n\nBears in full control.\n\nDon't catch falling knives. ",
            f"\n\n${ticker} support gone.\n\nDown we go."
        ]
        return random.choice(templates)
    def generate_question_response(self, input_text):
        """Generate response to question"""
        templates = [
            f"{input_text}\n\nThe answer is always liquidity.",
            f"{input_text}\n\nAnon, you already know the answer.",
            f"{input_text}\n\nYes. Next question."
        ]
        return random.choice(templates)
    def generate_philosophical_tweet(self, input_text):
        """Generate philosophical tweet"""
        templates = [
            f"This is the best time in history to {self.extract_action(input_text)}.\n\nIt's also the worst time to wait.\n\nThe choice is yours.",
            f"Everyone wants to {self.extract_action(input_text)}.\n\nNobody wants to put in the work.\n\nBe nobody.",
            f"The market rewards those who {self.extract_action(input_text)}.\n\nIt punishes those who hesitate.\n\nPosition yourself accordingly."
        ]
        return random.choice(templates)
    def generate_general_tweet(self, input_text):
        """Generate general tweet - using Option 5 baseline"""
        # Extract key concept from input
        key_concept = input_text.strip().lower()
        # Baseline template (Option 5 structure)
        if len(input_text) > 30:  # Longer inputs get baseline treatment
            # Identify what the "noise" is
            noise_options = [
                f"The {input_text.split()[0]} debate",
                f"All this talk about {key_concept[:20]}",
                f"The {key_concept[:15]} narrative",
                "What everyone's missing"
            ]
            templates = [
                f"{random.choice(noise_options)} is just noise.\n\nWhat matters: understanding the deeper dynamics at play.\n\nUntil then? We're all just speculating.",
                f"The obvious take on {key_concept[:20]} is just noise.\n\nWhat matters: positioning before the crowd catches on.\n\nFor now? We trade the range.",
                f"Everyone focused on {key_concept[:20]} is missing the point.\n\nWhat counts: the second-order effects nobody's pricing in.\n\nMeanwhile? Smart money is accumulating."
            ]
        else:  # Short inputs get simple treatment
            templates = [
                f"{input_text}\n\nBased.",
                f"{input_text}\n\nFew understand this.",
                f"Unpopular opinion: {input_text}\n\nBut I said what I said."
            ]
        return random.choice(templates)
    def extract_ticker(self, text):
        """Extract ticker symbol from text"""
        tickers = re.findall(r'\$?([A-Z]{2,5})', text.upper())
        return tickers[0] if tickers else None
    def extract_action(self, text):
        """Extract action phrase from text"""
        # Simple extraction - take main verb phrase
        words = text.lower().split()
        if 'to' in words:
            idx = words.index('to')
            if idx < len(words) - 1:
                return ' '.join(words[idx+1:])
        return "build in this market"
def run_interactive_test():
    """Run interactive testing session"""
    print("""
    ========================================================
         Miles Deutscher AI - Interactive Test Mode
      Type any input to generate Miles-style tweets
      Commands: 'quit' to exit, 'examples' for ideas
    ========================================================
    """)
    tester = MilesAITester()
    examples = [
        "btc looking bullish",
        "is this the bear market",
        "thoughts on ethereum",
        "everyone wants to get rich",
        "defi summer vibes",
        "gm"
    ]
    while True:
        print("\n" + "="*60)
        user_input = input("Enter text (or 'quit'/'examples'): ").strip()
        if user_input.lower() == 'quit':
            print("\nThanks for testing! WAGMI")
            break
        if user_input.lower() == 'examples':
            print("\nExample inputs:")
            for ex in examples:
                print(f"   - {ex}")
            continue
        if not user_input:
            continue
        # Generate tweet
        tweet = tester.generate_miles_tweet(user_input)
        print(f"\nGenerated Tweet:")
        print("-" * 40)
        print(tweet)
        print("-" * 40)
        # Show metrics
        print(f"\nMetrics:")
        print(f"   Length: {len(tweet)} characters")
        print(f"   Has ticker: {'Yes' if '$' in tweet else 'No'}")
        print(f"   Has emoji: {'Yes' if any(ord(c) > 127 for c in tweet) else 'No'}")
        print(f"   Line breaks: {tweet.count(chr(10))}")
if __name__ == "__main__":
    run_interactive_test()