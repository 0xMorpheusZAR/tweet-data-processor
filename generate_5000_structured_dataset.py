"""
Generate structured dataset of 5000 Miles-style tweets
Based on analyzed patterns from existing data
"""
import json
import random
from datetime import datetime, timedelta
import hashlib
from typing import Dict, List

class MilesDatasetGenerator:
    def __init__(self):
        # Load existing patterns and data
        self.patterns = self.load_patterns()
        self.topics = self.load_topics()
        self.templates = self.load_templates()
        
    def load_patterns(self):
        """Load known Miles patterns"""
        return {
            "3_part_classic": {
                "weight": 0.25,
                "template": "{dismissive}\n\n{focus}\n\n{reality}",
                "examples": [
                    {
                        "dismissive": "Everyone's obsessed with {topic}",
                        "focus": "The real game is {insight}",
                        "reality": "Few understand this"
                    },
                    {
                        "dismissive": "Most people think {common_belief}",
                        "focus": "What actually matters: {truth}",
                        "reality": "This is the way"
                    }
                ]
            },
            "5_part": {
                "weight": 0.15,
                "template": "{observation}\n\n{insight1}\n\n{insight2}\n\n{insight3}\n\n{conclusion}",
                "examples": [
                    {
                        "observation": "The {market} is telling us something",
                        "insight1": "1. {point1}",
                        "insight2": "2. {point2}",
                        "insight3": "3. {point3}",
                        "conclusion": "Position accordingly"
                    }
                ]
            },
            "7_part": {
                "weight": 0.10,
                "template": "{intro}\n\n{point1}\n\n{point2}\n\n{point3}\n\n{point4}\n\n{point5}\n\n{conclusion}",
                "examples": [
                    {
                        "intro": "Quick thread on {topic}:",
                        "point1": "First, {insight1}",
                        "point2": "Second, {insight2}",
                        "point3": "Third, {insight3}",
                        "point4": "Fourth, {insight4}",
                        "point5": "Finally, {insight5}",
                        "conclusion": "TLDR: {summary}"
                    }
                ]
            },
            "short_take": {
                "weight": 0.30,
                "template": "{statement}",
                "examples": [
                    "{market_observation}",
                    "{philosophical_insight}",
                    "{trading_wisdom}"
                ]
            },
            "question": {
                "weight": 0.20,
                "template": "{question}\n\n{context}",
                "examples": [
                    {
                        "question": "What if {scenario}?",
                        "context": "Think about it"
                    }
                ]
            }
        }
    
    def load_topics(self):
        """Load topic categories and keywords"""
        return {
            "altcoins": {
                "keywords": ["alts", "altcoin", "alt season", "rotation", "dominance"],
                "insights": [
                    "understanding rotation patterns",
                    "positioning before the herd",
                    "recognizing accumulation phases",
                    "timing the dominance shift"
                ]
            },
            "market_analysis": {
                "keywords": ["market", "trend", "structure", "levels", "support", "resistance"],
                "insights": [
                    "reading between the lines",
                    "understanding market psychology",
                    "identifying key levels",
                    "recognizing trend changes"
                ]
            },
            "trading": {
                "keywords": ["trade", "position", "entry", "exit", "risk", "reward"],
                "insights": [
                    "managing risk properly",
                    "waiting for confirmation",
                    "scaling positions correctly",
                    "protecting capital first"
                ]
            },
            "philosophy": {
                "keywords": ["think", "mindset", "success", "failure", "learn"],
                "insights": [
                    "mastering your emotions",
                    "thinking independently",
                    "learning from mistakes",
                    "staying disciplined"
                ]
            },
            "crypto_analysis": {
                "keywords": ["btc", "bitcoin", "eth", "ethereum", "crypto"],
                "insights": [
                    "understanding the macro",
                    "following smart money",
                    "recognizing cycle patterns",
                    "timing the market cycles"
                ]
            }
        }
    
    def load_templates(self):
        """Load sentence templates"""
        return {
            "dismissive": [
                "Everyone's focused on {topic}",
                "Most people think {belief}",
                "The crowd believes {misconception}",
                "Everyone wants {desire}",
                "People are obsessed with {focus}"
            ],
            "focus": [
                "What matters: {insight}",
                "The real game: {truth}",
                "Focus on: {important}",
                "Reality: {fact}",
                "Truth is: {revelation}"
            ],
            "reality": [
                "Few understand this",
                "Most will miss it",
                "This is the way",
                "Simple as that",
                "Few"
            ],
            "market_observation": [
                "{market} looking {sentiment}",
                "This {timeframe} tells you everything",
                "{indicator} flashing {signal}",
                "The {pattern} is obvious",
                "{metric} at {level}"
            ],
            "philosophical_insight": [
                "Success requires {quality}",
                "The best traders {action}",
                "Winners {behavior}",
                "Mastery comes from {practice}",
                "{virtue} beats {vice} every time"
            ],
            "trading_wisdom": [
                "Never {mistake}",
                "Always {good_practice}",
                "The key: {secret}",
                "Remember: {reminder}",
                "{rule} is everything"
            ]
        }
    
    def generate_tweet_text(self, pattern_type: str) -> str:
        """Generate tweet text based on pattern"""
        pattern = self.patterns[pattern_type]
        
        # Select random topic
        topic = random.choice(list(self.topics.keys()))
        topic_data = self.topics[topic]
        
        # Generate based on pattern type
        if pattern_type == "3_part_classic":
            example = random.choice(pattern["examples"])
            dismissive = random.choice(self.templates["dismissive"])
            focus = random.choice(self.templates["focus"])
            reality = random.choice(self.templates["reality"])
            
            # Fill in placeholders
            topic_word = random.choice(topic_data["keywords"])
            insight = random.choice(topic_data["insights"])
            
            # Safe format dismissive
            if "{belief}" in dismissive:
                dismissive = dismissive.format(belief=f"about {topic_word}")
            elif "{misconception}" in dismissive:
                dismissive = dismissive.format(misconception=f"about {topic_word}")
            elif "{desire}" in dismissive:
                dismissive = dismissive.format(desire=topic_word)
            elif "{focus}" in dismissive:
                dismissive = dismissive.format(focus=topic_word)
            else:
                dismissive = dismissive.format(topic=topic_word)
            
            # Safe format focus
            if "{truth}" in focus:
                focus = focus.format(truth=insight)
            elif "{important}" in focus:
                focus = focus.format(important=insight)
            elif "{fact}" in focus:
                focus = focus.format(fact=insight)
            elif "{revelation}" in focus:
                focus = focus.format(revelation=insight)
            else:
                focus = focus.format(insight=insight)
            
            text = f"{dismissive}\n\n{focus}\n\n{reality}"
            
            return text
            
        elif pattern_type == "short_take":
            template_type = random.choice(["market_observation", "philosophical_insight", "trading_wisdom"])
            template = random.choice(self.templates[template_type])
            
            # Fill based on template type
            if template_type == "market_observation":
                replacements = {
                    "market": random.choice(["BTC", "ETH", "Alts", "Market"]),
                    "sentiment": random.choice(["bullish", "bearish", "ready", "coiled"]),
                    "timeframe": random.choice(["daily", "weekly", "4H", "monthly"]),
                    "indicator": random.choice(["RSI", "Volume", "OI", "Funding"]),
                    "signal": random.choice(["green", "red", "divergence", "strength"]),
                    "pattern": random.choice(["setup", "structure", "trend", "pattern"]),
                    "metric": random.choice(["Support", "Resistance", "MA", "VWAP"]),
                    "level": random.choice(["key levels", "ATH", "critical zone", "breakout"])
                }
            else:
                replacements = {
                    "quality": random.choice(["patience", "discipline", "focus", "consistency"]),
                    "action": random.choice(["wait", "plan", "execute", "adapt"]),
                    "behavior": random.choice(["adapt", "learn", "evolve", "persist"]),
                    "practice": random.choice(["repetition", "study", "experience", "failure"]),
                    "virtue": random.choice(["Patience", "Discipline", "Focus", "Planning"]),
                    "vice": random.choice(["greed", "fear", "hope", "impulse"]),
                    "mistake": random.choice(["overtrade", "revenge trade", "FOMO", "panic sell"]),
                    "good_practice": random.choice(["plan your trades", "manage risk", "stay patient", "follow the trend"]),
                    "secret": random.choice(["position sizing", "risk management", "patience", "discipline"]),
                    "reminder": random.choice(["capital preservation", "the trend is your friend", "plan the trade", "cut losses"]),
                    "rule": random.choice(["Risk management", "Position sizing", "Patience", "Discipline"])
                }
            
            # Safe string formatting
            for key, value in replacements.items():
                template = template.replace(f"{{{key}}}", value)
            
            return template
            
        elif pattern_type == "5_part":
            topic_word = random.choice(topic_data["keywords"])
            insights = random.sample(topic_data["insights"], 3)
            
            text = f"The {topic_word} situation:\n\n"
            text += f"1. {insights[0].capitalize()}\n\n"
            text += f"2. {insights[1].capitalize()}\n\n"
            text += f"3. {insights[2].capitalize()}\n\n"
            text += "Position accordingly."
            
            return text
            
        else:  # question
            topic_word = random.choice(topic_data["keywords"])
            scenarios = [
                f"{topic_word} breaks out here",
                f"this is the {topic_word} bottom",
                f"everyone's wrong about {topic_word}",
                f"the {topic_word} narrative shifts"
            ]
            
            scenario = random.choice(scenarios)
            return f"What if {scenario}?\n\nThink about it."
    
    def generate_metrics(self, quality_score: float) -> Dict:
        """Generate realistic engagement metrics based on quality"""
        base_likes = random.randint(50, 500)
        
        if quality_score > 0.8:
            likes = base_likes * random.uniform(2, 5)
            retweets = likes * random.uniform(0.2, 0.4)
        elif quality_score > 0.6:
            likes = base_likes * random.uniform(1.5, 2.5)
            retweets = likes * random.uniform(0.15, 0.3)
        else:
            likes = base_likes
            retweets = likes * random.uniform(0.1, 0.2)
        
        return {
            "likes": int(likes),
            "retweets": int(retweets),
            "replies": int(likes * random.uniform(0.05, 0.15)),
            "quotes": int(retweets * random.uniform(0.1, 0.3)),
            "impressions": int(likes * random.uniform(20, 50))
        }
    
    def generate_tweet(self, index: int) -> Dict:
        """Generate a complete structured tweet"""
        # Select pattern based on weights
        pattern_types = list(self.patterns.keys())
        weights = [self.patterns[pt]["weight"] for pt in pattern_types]
        pattern_type = random.choices(pattern_types, weights=weights)[0]
        
        # Generate text
        text = self.generate_tweet_text(pattern_type)
        
        # Generate timestamp (last 6 months)
        days_ago = random.randint(0, 180)
        timestamp = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        # Calculate quality score
        quality_score = 0.5
        if pattern_type in ["3_part_classic", "5_part", "7_part"]:
            quality_score += 0.2
        if len(text) > 100:
            quality_score += 0.1
        if "http" not in text:
            quality_score += 0.1
        quality_score = min(1.0, quality_score + random.uniform(-0.1, 0.2))
        
        # Generate metrics
        metrics = self.generate_metrics(quality_score)
        
        # Generate ID
        tweet_id = hashlib.md5(f"{index}{text}".encode()).hexdigest()[:16]
        
        # Detect topic
        text_lower = text.lower()
        topics = []
        for topic, data in self.topics.items():
            if any(keyword in text_lower for keyword in data["keywords"]):
                topics.append(topic)
        if not topics:
            topics = ["general"]
        
        return {
            "id": tweet_id,
            "created_at": timestamp.isoformat(),
            "text": text,
            "clean_text": text.replace("http://", "").replace("https://", "").strip(),
            "type": "short_take" if pattern_type == "short_take" else pattern_type,
            "pattern": pattern_type,
            "word_count": len(text.split()),
            "char_count": len(text),
            "metrics": metrics,
            "engagement_rate": round(sum(metrics.values()) / max(metrics.get("impressions", 10000), 1), 4),
            "virality_score": round(min(1.0, (metrics["likes"] + metrics["retweets"] * 3) / 10000), 4),
            "entities": {
                "hashtags": [],
                "mentions": [],
                "urls": [],
                "cashtags": []
            },
            "is_reply": False,
            "is_thread": pattern_type == "7_part",
            "has_media": False,
            "source": "generated",
            "language": "en",
            "possibly_sensitive": False,
            "quality_score": round(quality_score, 2),
            "topic_categories": topics,
            "sentiment": random.choice(["bullish", "bearish", "neutral"]),
            "key_phrases": []
        }
    
    def generate_dataset(self, count: int = 5000) -> List[Dict]:
        """Generate full dataset"""
        tweets = []
        
        print(f"Generating {count} structured tweets...")
        
        for i in range(count):
            if i % 500 == 0:
                print(f"Generated {i} tweets...")
            
            tweet = self.generate_tweet(i)
            tweets.append(tweet)
        
        # Sort by date (newest first)
        tweets.sort(key=lambda x: x["created_at"], reverse=True)
        
        print(f"Generated {len(tweets)} tweets!")
        return tweets
    
    def calculate_statistics(self, tweets: List[Dict]) -> Dict:
        """Calculate dataset statistics"""
        total_likes = sum(t['metrics']['likes'] for t in tweets)
        total_retweets = sum(t['metrics']['retweets'] for t in tweets)
        
        # Pattern distribution
        pattern_counts = {}
        for tweet in tweets:
            pattern = tweet['pattern']
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Topic distribution
        topic_counts = {}
        for tweet in tweets:
            for topic in tweet['topic_categories']:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Quality distribution
        quality_scores = [t['quality_score'] for t in tweets]
        high_quality = sum(1 for s in quality_scores if s >= 0.7)
        
        return {
            "total_tweets": len(tweets),
            "date_range": {
                "earliest": min(t['created_at'] for t in tweets),
                "latest": max(t['created_at'] for t in tweets)
            },
            "engagement": {
                "total_likes": total_likes,
                "total_retweets": total_retweets,
                "avg_likes": round(total_likes / len(tweets), 2),
                "avg_retweets": round(total_retweets / len(tweets), 2),
                "highest_likes": max(t['metrics']['likes'] for t in tweets),
                "highest_retweets": max(t['metrics']['retweets'] for t in tweets)
            },
            "patterns": pattern_counts,
            "topics": topic_counts,
            "quality": {
                "average": round(sum(quality_scores) / len(quality_scores), 3),
                "min": min(quality_scores),
                "max": max(quality_scores),
                "high_quality_count": high_quality,
                "high_quality_percentage": round(high_quality / len(tweets) * 100, 1)
            },
            "content": {
                "avg_word_count": round(sum(t['word_count'] for t in tweets) / len(tweets), 1),
                "avg_char_count": round(sum(t['char_count'] for t in tweets) / len(tweets), 1)
            }
        }
    
    def save_dataset(self, tweets: List[Dict], filename: str = "miles_5000_tweets_structured.json"):
        """Save the generated dataset"""
        output = {
            "metadata": {
                "source": "Generated based on Miles Deutscher patterns",
                "username": "milesdeutscher",
                "user_id": "1042881640908840960",
                "fetch_date": datetime.now().isoformat(),
                "total_tweets": len(tweets),
                "api_version": "2.0",
                "structure_version": "1.0",
                "generation_method": "pattern-based"
            },
            "statistics": self.calculate_statistics(tweets),
            "tweets": tweets
        }
        
        # Save as JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(tweets)} tweets to {filename}")
        
        # Save as JSONL
        jsonl_filename = filename.replace('.json', '.jsonl')
        with open(jsonl_filename, 'w', encoding='utf-8') as f:
            for tweet in tweets:
                f.write(json.dumps(tweet, ensure_ascii=False) + '\n')
        
        print(f"Also saved as JSONL: {jsonl_filename}")

def main():
    """Main execution"""
    print("=== Miles Deutscher 5000 Tweet Dataset Generator ===\n")
    
    generator = MilesDatasetGenerator()
    
    # Generate dataset
    tweets = generator.generate_dataset(5000)
    
    # Save dataset
    generator.save_dataset(tweets)
    
    # Display statistics
    stats = generator.calculate_statistics(tweets)
    
    print("\n=== Dataset Statistics ===")
    print(f"Total tweets: {stats['total_tweets']}")
    print(f"Date range: {stats['date_range']['earliest'][:10]} to {stats['date_range']['latest'][:10]}")
    print(f"Average likes: {stats['engagement']['avg_likes']}")
    print(f"Average retweets: {stats['engagement']['avg_retweets']}")
    print(f"High quality tweets: {stats['quality']['high_quality_count']} ({stats['quality']['high_quality_percentage']}%)")
    
    print("\nPattern distribution:")
    for pattern, count in sorted(stats['patterns'].items(), key=lambda x: x[1], reverse=True):
        percentage = round(count / stats['total_tweets'] * 100, 1)
        print(f"  {pattern}: {count} ({percentage}%)")
    
    print("\nTopic distribution:")
    for topic, count in sorted(stats['topics'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {topic}: {count}")
    
    print("\n[SUCCESS] Dataset generation complete!")

if __name__ == "__main__":
    main()