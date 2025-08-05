"""
Miles AI Godmode - Optimal Tweet Generation
Target: Maximum impact, minimum words
"""
import json
import random
from typing import Dict, List

class MilesAIGodmode:
    def __init__(self):
        self.optimal_patterns = self.load_optimal_patterns()
        self.power_words = self.load_power_words()
        self.contrasts = self.load_contrasts()
        
    def load_optimal_patterns(self):
        """Load only the highest performing patterns"""
        return {
            "perfect_3_part": {
                "template": "{dismissal}\n\n{insight}\n\n{closer}",
                "rules": {
                    "total_chars": (60, 100),
                    "line_1_words": (3, 7),
                    "line_2_words": (4, 8),
                    "line_3_words": (2, 4)
                }
            }
        }
    
    def load_power_words(self):
        """Words that consistently appear in high-engagement tweets"""
        return {
            "dismissal_starters": [
                "Everyone's", "Most people", "The crowd", "Everyone thinks",
                "Most are", "People think", "The market thinks"
            ],
            "dismissal_actions": [
                "waiting for", "focused on", "obsessed with", "chasing",
                "worried about", "predicting", "calling for", "expecting"
            ],
            "insight_starters": [
                "The best traders", "Smart money", "Winners", "The real game",
                "What matters:", "Reality:", "Truth is:"
            ],
            "insight_actions": [
                "already positioned", "accumulating quietly", "building positions",
                "taking profits", "managing risk", "thinking differently",
                "playing the long game"
            ],
            "closers": [
                "Few understand this.",
                "Few get it.",
                "Few.",
                "Most will miss it.",
                "This is the way.",
                "Simple as that."
            ]
        }
    
    def load_contrasts(self):
        """Powerful contrast pairs"""
        return [
            ("waiting", "positioned"),
            ("talking", "accumulating"),
            ("predicting", "preparing"),
            ("hoping", "executing"),
            ("panicking", "buying"),
            ("celebrating", "selling"),
            ("analyzing", "acting"),
            ("complaining", "adapting")
        ]
    
    def extract_core_concept(self, input_text: str) -> Dict:
        """Extract the core concept from input"""
        input_lower = input_text.lower()
        
        # Detect main topic
        topics = {
            "bitcoin": ["btc", "bitcoin", "sats"],
            "altcoins": ["alt", "alts", "altcoin", "altseason"],
            "entry": ["entry", "buy", "accumulate", "position"],
            "exit": ["exit", "sell", "profit", "top"],
            "market": ["market", "cycle", "trend", "structure"],
            "mindset": ["mindset", "psychology", "emotion", "fear", "greed"],
            "timing": ["time", "timing", "when", "soon"],
            "strategy": ["strategy", "plan", "system", "method"]
        }
        
        detected_topic = "market"  # default
        for topic, keywords in topics.items():
            if any(keyword in input_lower for keyword in keywords):
                detected_topic = topic
                break
        
        # Detect sentiment/action
        if any(word in input_lower for word in ["crash", "dump", "fear", "bottom"]):
            sentiment = "fearful"
        elif any(word in input_lower for word in ["moon", "pump", "bullish", "top"]):
            sentiment = "greedy"
        else:
            sentiment = "neutral"
        
        return {"topic": detected_topic, "sentiment": sentiment}
    
    def generate_optimal_tweet(self, input_text: str) -> str:
        """Generate the most optimal Miles-style tweet"""
        
        # Extract concept
        concept = self.extract_core_concept(input_text)
        topic = concept["topic"]
        sentiment = concept["sentiment"]
        
        # Select appropriate contrast based on topic and sentiment
        if topic == "entry" or sentiment == "fearful":
            crowd_action = "waiting for the perfect entry"
            smart_action = "already positioned"
        elif topic == "exit" or sentiment == "greedy":
            crowd_action = "calling the top"
            smart_action = "taking profits quietly"
        elif topic == "altcoins":
            crowd_action = "chasing pumps"
            smart_action = "accumulating quality"
        elif topic == "mindset":
            crowd_action = "letting emotions lead"
            smart_action = "following their system"
        elif topic == "timing":
            crowd_action = "trying to time perfectly"
            smart_action = "scaling in patiently"
        else:
            # Generic but powerful
            contrast = random.choice(self.contrasts)
            crowd_action = f"{contrast[0]}"
            smart_action = f"{contrast[1]}"
        
        # Build the tweet
        dismissal_starter = random.choice(self.power_words["dismissal_starters"])
        
        # Ensure grammatical correctness
        if dismissal_starter in ["Everyone's", "Most are"]:
            dismissal = f"{dismissal_starter} {crowd_action}."
        elif dismissal_starter in ["The crowd", "Smart money"]:
            dismissal = f"{dismissal_starter} is {crowd_action}."
        else:
            dismissal = f"{dismissal_starter} {crowd_action}."
        
        insight_starter = random.choice(self.power_words["insight_starters"])
        if insight_starter.endswith(":"):
            insight = f"{insight_starter} {smart_action}."
        elif insight_starter in ["The best traders", "Winners"]:
            insight = f"{insight_starter} are {smart_action}."
        elif insight_starter == "Smart money":
            insight = f"{insight_starter} is {smart_action}."
        else:
            insight = f"{insight_starter} {smart_action}."
        
        closer = random.choice(self.power_words["closers"])
        
        # Assemble
        tweet = f"{dismissal}\n\n{insight}\n\n{closer}"
        
        # Optimize for brevity
        if len(tweet) > 100:
            # Use shorter versions
            if "already" in insight:
                insight = insight.replace("already ", "")
            if "quietly" in insight:
                insight = insight.replace(" quietly", "")
            tweet = f"{dismissal}\n\n{insight}\n\n{closer}"
        
        return tweet
    
    def generate_variations(self, input_text: str, count: int = 3) -> List[str]:
        """Generate multiple optimal variations"""
        variations = []
        for _ in range(count):
            tweet = self.generate_optimal_tweet(input_text)
            if tweet not in variations:
                variations.append(tweet)
        return variations

# Example usage
def demonstrate_godmode():
    godmode = MilesAIGodmode()
    
    test_inputs = [
        "bitcoin price prediction",
        "altcoin season timing",
        "market crash fears",
        "trading strategy",
        "when to take profits"
    ]
    
    print("=== Miles AI Godmode Demonstrations ===\n")
    
    for input_text in test_inputs:
        print(f"Input: '{input_text}'")
        print("Output:")
        tweet = godmode.generate_optimal_tweet(input_text)
        print(tweet)
        print(f"[Length: {len(tweet)} chars]")
        print("-" * 40 + "\n")

if __name__ == "__main__":
    demonstrate_godmode()