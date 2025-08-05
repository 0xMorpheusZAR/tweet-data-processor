"""
Miles Deutscher Twitter/X Bot - Production Ready
Input: Text typed in Twitter compose box
Output: Miles-style tweet
"""

import json
import torch
from typing import List, Dict, Tuple
import re

class MilesTwitterBot:
    """
    Production-ready bot that converts any input into Miles Deutscher tweets
    """
    
    def __init__(self, model_path: str = "./miles-twitter-ai"):
        self.model_path = model_path
        self.style_templates = self.load_style_templates()
        
    def load_style_templates(self) -> Dict:
        """Load Miles's proven tweet templates"""
        return {
            "market_analysis": [
                "{ticker} looking {sentiment}.\n\n{analysis}\n\n{conclusion}",
                "{observation}\n\n{ticker} {action}.\n\n{warning_or_target}"
            ],
            "philosophical": [
                "This is the {best_worst} time to {action}.\n\nIt's also the {opposite} time to {opposite_action}.\n\n{conclusion}",
                "{universal_truth}.\n\n{application_to_crypto}.\n\n{call_to_action}"
            ],
            "quick_take": [
                "{reaction}\n\n{link}",
                "{statement}.\n\n{emphasis} {conclusion}",
                "{rhetorical_question}\n\n{answer}"
            ],
            "thread_starter": [
                "{topic_intro}\n\nA thread 🧵👇",
                "1/ {opening_statement}",
                "{number}/ {point}"
            ]
        }
    
    def process_input(self, user_input: str) -> Dict:
        """
        Analyze user input to determine intent and style
        """
        
        input_lower = user_input.lower()
        
        # Detect market intent
        tickers = re.findall(r'\$[A-Z]+', user_input.upper())
        has_ticker = len(tickers) > 0
        
        # Detect question
        is_question = '?' in user_input
        
        # Detect sentiment
        bullish_words = ['bullish', 'moon', 'up', 'pump', 'long', 'buy']
        bearish_words = ['bearish', 'dump', 'down', 'short', 'sell', 'crash']
        
        sentiment = "neutral"
        if any(word in input_lower for word in bullish_words):
            sentiment = "bullish"
        elif any(word in input_lower for word in bearish_words):
            sentiment = "bearish"
        
        # Determine style
        if has_ticker:
            style = "market_analysis"
        elif any(word in input_lower for word in ['best', 'worst', 'time', 'everyone', 'nobody']):
            style = "philosophical"
        elif len(user_input) < 30:
            style = "quick_take"
        else:
            style = "general"
        
        return {
            "original_input": user_input,
            "style": style,
            "sentiment": sentiment,
            "has_ticker": has_ticker,
            "tickers": tickers,
            "is_question": is_question
        }
    
    def generate_tweet(self, user_input: str) -> List[str]:
        """
        Generate Miles-style tweets from user input
        Returns top 3 options for user to choose from
        """
        
        # Analyze input
        input_analysis = self.process_input(user_input)
        
        # Generate based on style
        if input_analysis["style"] == "market_analysis":
            tweets = self.generate_market_tweet(input_analysis)
        elif input_analysis["style"] == "philosophical":
            tweets = self.generate_philosophical_tweet(input_analysis)
        elif input_analysis["style"] == "quick_take":
            tweets = self.generate_quick_take(input_analysis)
        else:
            tweets = self.generate_general_tweet(input_analysis)
        
        # Ensure all tweets are within Twitter limit
        valid_tweets = [t for t in tweets if len(t) <= 280]
        
        return valid_tweets[:3]  # Return top 3 options
    
    def generate_market_tweet(self, analysis: Dict) -> List[str]:
        """Generate market analysis tweets"""
        
        tweets = []
        ticker = analysis["tickers"][0] if analysis["tickers"] else "$BTC"
        
        if analysis["sentiment"] == "bullish":
            tweets.extend([
                f"{ticker} chart looking absolutely fire right now.\n\nClean break above resistance with volume.\n\nNext target: moon 🚀",
                f"Ser, {ticker} is literally printing money.\n\nIf you're not in, NGMI.\n\n(NFA DYOR)",
                f"{ticker} {analysis['original_input']}\n\nUp only from here.\n\nYou heard it here first."
            ])
        elif analysis["sentiment"] == "bearish":
            tweets.extend([
                f"{ticker} about to get absolutely rekt.\n\nSupport broken, no buyers in sight.\n\nProtect your capital.",
                f"Warning: {ticker} showing major weakness.\n\nThis is not the dip you want to buy.\n\nPatience pays.",
                f"{ticker} {analysis['original_input']}\n\nBears in full control.\n\nDon't catch falling knives."
            ])
        else:
            tweets.extend([
                f"{ticker} at a critical juncture here.\n\nCould go either way tbh.\n\nWait for confirmation.",
                f"Thoughts on {ticker}?\n\n{analysis['original_input']}\n\nInteresting setup developing.",
                f"{ticker} {analysis['original_input']}\n\nLet's see how this plays out.\n\nStaying neutral for now."
            ])
        
        return tweets
    
    def generate_philosophical_tweet(self, analysis: Dict) -> List[str]:
        """Generate philosophical/motivational tweets"""
        
        input_text = analysis["original_input"]
        
        tweets = [
            f"This is the best time in history to {input_text}.\n\nIt's also the worst time to sit on the sidelines.\n\nThe choice is yours.",
            f"Everyone is talking about {input_text}.\n\nNobody is actually doing it.\n\nBe nobody.",
            f"The market rewards those who {input_text}.\n\nIt punishes those who hesitate.\n\nPosition yourself accordingly."
        ]
        
        return tweets
    
    def generate_quick_take(self, analysis: Dict) -> List[str]:
        """Generate short, punchy tweets"""
        
        input_text = analysis["original_input"]
        
        tweets = [
            f"{input_text}\n\nBased.",
            f"{input_text}\n\nSer, this is the alpha.",
            f"{input_text}\n\nFew understand this."
        ]
        
        if analysis["is_question"]:
            tweets.extend([
                f"{input_text}\n\nYes. Next question.",
                f"{input_text}\n\nThe answer is always liquidity.",
                f"{input_text}\n\nAnon, you already know the answer."
            ])
        
        return tweets
    
    def generate_general_tweet(self, analysis: Dict) -> List[str]:
        """Generate general tweets for any input"""
        
        input_text = analysis["original_input"]
        
        # Extract key concept
        key_words = [w for w in input_text.split() if len(w) > 4]
        topic = key_words[0] if key_words else "this"
        
        tweets = [
            f"Unpopular opinion: {input_text}\n\nBut I said what I said.",
            f"{input_text}\n\nThis is exactly why we're early.\n\nNGMI if you're not paying attention.",
            f"Real talk:\n\n{input_text}\n\nThat's the tweet."
        ]
        
        return tweets

# USAGE INTERFACE
class TwitterInterface:
    """
    Simple interface for Twitter/X integration
    """
    
    def __init__(self):
        self.bot = MilesTwitterBot()
        
    def compose_tweet(self, user_input: str) -> Dict:
        """
        Main function called when user types in Twitter compose box
        
        Args:
            user_input: Raw text from Twitter compose box
            
        Returns:
            Dict with tweet options and metadata
        """
        
        # Generate options
        tweet_options = self.bot.generate_tweet(user_input)
        
        # Add engagement predictions
        engagement_scores = self.predict_engagement(tweet_options)
        
        return {
            "input": user_input,
            "tweets": tweet_options,
            "engagement_scores": engagement_scores,
            "recommended": 0,  # Index of recommended tweet
            "metadata": {
                "style": self.bot.process_input(user_input)["style"],
                "has_media_suggestion": any("chart" in t.lower() for t in tweet_options)
            }
        }
    
    def predict_engagement(self, tweets: List[str]) -> List[float]:
        """
        Predict engagement score for each tweet option
        """
        
        scores = []
        
        for tweet in tweets:
            score = 0.5  # Base score
            
            # Factors that increase engagement
            if "?" in tweet:
                score += 0.1  # Questions engage
            if any(word in tweet.lower() for word in ["unpopular opinion", "thread", "alpha"]):
                score += 0.15
            if "$" in tweet:
                score += 0.1  # Tickers get attention
            if len(tweet) < 100:
                score += 0.05  # Concise tweets perform better
            if any(emoji in tweet for emoji in ["🚀", "🔥", "👇", "💎"]):
                score += 0.1
            
            scores.append(min(score, 1.0))
        
        return scores

# EXAMPLE USAGE
if __name__ == "__main__":
    # Initialize interface
    interface = TwitterInterface()
    
    # Test inputs that might be typed in Twitter
    test_inputs = [
        "btc looking bullish",
        "is this the top",
        "defi summer vibes",
        "everyone talking about AI agents nobody building",
        "thoughts on $ETH",
        "bear market blues",
        "gm"
    ]
    
    print("🐦 Miles Deutscher Twitter Bot - Test Results\n")
    print("=" * 60)
    
    for test_input in test_inputs:
        result = interface.compose_tweet(test_input)
        
        print(f"\n📝 Input: '{test_input}'")
        print(f"🎯 Style: {result['metadata']['style']}")
        print("\n🔥 Generated Options:")
        
        for i, (tweet, score) in enumerate(zip(result['tweets'], result['engagement_scores'])):
            recommended = "⭐" if i == result['recommended'] else "  "
            print(f"\n{recommended} Option {i+1} (engagement: {score:.2f}):")
            print(f"   {tweet}")
        
        print("\n" + "-" * 60)