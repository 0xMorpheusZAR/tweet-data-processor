"""
Fetch Miles' Top 5 Viral Tweets for Context Training
Uses X API to get real-time engagement data and context
"""
import requests
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from pathlib import Path

# Import our secure credentials
from config.credentials import credential_manager
from miles_mega_framework_top100 import MilesMegaFramework

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ViralTweetContext:
    """Complete context for viral tweet analysis"""
    tweet_id: str
    text: str
    created_at: str
    public_metrics: Dict[str, int]
    context_annotations: List[Dict]
    entities: Dict
    referenced_tweets: Optional[List[Dict]]
    
    # Calculated metrics
    total_engagement: int
    engagement_rate: float
    viral_score: float
    velocity_score: float  # How fast it went viral
    
    # Context analysis
    posting_time: Dict[str, any]
    market_conditions: Dict[str, str]
    content_analysis: Dict[str, any]
    pattern_breakdown: Dict[str, any]

class ViralContextAnalyzer:
    """Analyzes viral tweet context for optimization formula training"""
    
    def __init__(self):
        self.credentials = credential_manager.credentials
        self.base_url = "https://api.twitter.com/2"
        self.headers = self.credentials.get_headers()
        self.mega_framework = MilesMegaFramework()
        
    def fetch_top_viral_tweets(self, username: str = "milesdeutscher", count: int = 5) -> List[ViralTweetContext]:
        """Fetch Miles' top viral tweets with complete context"""
        logger.info(f"Fetching top {count} viral tweets from @{username}...")
        
        # Get user ID
        user_url = f"{self.base_url}/users/by/username/{username}"
        user_response = requests.get(user_url, headers=self.headers)
        
        if user_response.status_code != 200:
            raise Exception(f"Failed to get user ID: {user_response.text}")
            
        user_id = user_response.json()["data"]["id"]
        
        # Fetch tweets with maximum context
        tweets_url = f"{self.base_url}/users/{user_id}/tweets"
        params = {
            "max_results": 100,  # Get more to find top viral
            "tweet.fields": ",".join([
                "id", "text", "created_at", "author_id", "conversation_id",
                "public_metrics", "context_annotations", "entities",
                "lang", "possibly_sensitive", "referenced_tweets",
                "reply_settings", "source", "withheld"
            ]),
            "expansions": "referenced_tweets.id,referenced_tweets.id.author_id",
            "exclude": "replies"
        }
        
        all_tweets = []
        next_token = None
        
        # Paginate to get enough tweets
        for _ in range(10):  # Max 10 pages
            if next_token:
                params['pagination_token'] = next_token
                
            response = requests.get(tweets_url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch tweets: {response.text}")
                break
                
            data = response.json()
            
            if 'data' in data:
                all_tweets.extend(data['data'])
                
            if 'meta' in data and 'next_token' in data['meta']:
                next_token = data['meta']['next_token']
            else:
                break
                
            if len(all_tweets) >= 1000:  # Enough to find top viral
                break
                
            time.sleep(1)  # Rate limit respect
        
        logger.info(f"Fetched {len(all_tweets)} tweets total")
        
        # Convert to ViralTweetContext and sort by engagement
        viral_contexts = []
        
        for tweet in all_tweets:
            context = self._create_viral_context(tweet)
            if context:
                viral_contexts.append(context)
        
        # Sort by total engagement and get top N
        viral_contexts.sort(key=lambda x: x.total_engagement, reverse=True)
        top_viral = viral_contexts[:count]
        
        # Enrich with additional context
        for context in top_viral:
            self._enrich_context(context)
        
        return top_viral
    
    def _create_viral_context(self, tweet_data: Dict) -> Optional[ViralTweetContext]:
        """Create ViralTweetContext from tweet data"""
        try:
            metrics = tweet_data.get('public_metrics', {})
            
            # Calculate total engagement
            total_engagement = (
                metrics.get('like_count', 0) +
                metrics.get('retweet_count', 0) * 2 +
                metrics.get('reply_count', 0) * 1.5 +
                metrics.get('quote_count', 0) * 3
            )
            
            # Skip low engagement
            if total_engagement < 1000:
                return None
            
            # Calculate engagement rate
            impressions = metrics.get('impression_count', 0)
            engagement_rate = total_engagement / impressions if impressions > 0 else 0
            
            # Viral score (normalized)
            viral_score = min(total_engagement / 10000, 1.0)
            
            # Velocity score (how fast it gained engagement)
            created_at = datetime.fromisoformat(tweet_data['created_at'].replace('Z', '+00:00'))
            hours_old = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600
            velocity_score = total_engagement / max(hours_old, 1)  # Engagement per hour
            
            return ViralTweetContext(
                tweet_id=tweet_data['id'],
                text=tweet_data['text'],
                created_at=tweet_data['created_at'],
                public_metrics=metrics,
                context_annotations=tweet_data.get('context_annotations', []),
                entities=tweet_data.get('entities', {}),
                referenced_tweets=tweet_data.get('referenced_tweets'),
                total_engagement=int(total_engagement),
                engagement_rate=engagement_rate,
                viral_score=viral_score,
                velocity_score=velocity_score,
                posting_time={},
                market_conditions={},
                content_analysis={},
                pattern_breakdown={}
            )
            
        except Exception as e:
            logger.error(f"Error creating viral context: {e}")
            return None
    
    def _enrich_context(self, context: ViralTweetContext):
        """Enrich context with additional analysis"""
        
        # Posting time analysis
        created_dt = datetime.fromisoformat(context.created_at.replace('Z', '+00:00'))
        context.posting_time = {
            "hour_utc": created_dt.hour,
            "day_of_week": created_dt.strftime("%A"),
            "hour_est": (created_dt.hour - 5) % 24,  # Convert to EST
            "is_weekend": created_dt.weekday() >= 5,
            "is_market_hours": 9 <= ((created_dt.hour - 5) % 24) <= 16
        }
        
        # Content analysis
        text = context.text
        context.content_analysis = {
            "word_count": len(text.split()),
            "char_count": len(text),
            "line_count": text.count('\\n') + 1,
            "has_numbers": any(char.isdigit() for char in text),
            "has_question": '?' in text,
            "has_emoji": any(ord(char) > 127 for char in text),
            "uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            "exclamation_count": text.count('!'),
            "hashtag_count": text.count('#'),
            "mention_count": text.count('@')
        }
        
        # Pattern breakdown using MEGA framework
        result = self.mega_framework.generate_mega_tweet(
            context={"topic": "analysis", "intent": "analyze"},
            force_pattern=None
        )
        
        # Analyze which patterns this tweet matches
        pattern_scores = {}
        for pattern_key, pattern in self.mega_framework.mega_patterns.items():
            score = self._calculate_pattern_match(text, pattern)
            pattern_scores[pattern_key] = score
        
        best_pattern = max(pattern_scores.items(), key=lambda x: x[1])
        
        context.pattern_breakdown = {
            "best_match_pattern": best_pattern[0],
            "match_confidence": best_pattern[1],
            "pattern_scores": pattern_scores,
            "identified_micro_patterns": self._identify_micro_patterns(text),
            "linguistic_devices": self._identify_linguistic_devices(text)
        }
        
        # Market conditions (simulated - in production would use market data APIs)
        context.market_conditions = {
            "btc_trend": "bullish" if "bull" in text.lower() else "neutral",
            "market_sentiment": "positive" if any(word in text.lower() for word in ["opportunity", "accumulation", "bottom"]) else "neutral",
            "volatility": "high" if any(word in text.lower() for word in ["volatile", "swing", "move"]) else "normal"
        }
    
    def _calculate_pattern_match(self, text: str, pattern) -> float:
        """Calculate how well a tweet matches a pattern"""
        score = 0.0
        
        # Check for power phrases
        for phrase in pattern.power_phrases:
            if phrase.lower() in text.lower():
                score += 0.2
        
        # Check word count match
        word_count = len(text.split())
        if pattern.optimal_word_count[0] <= word_count <= pattern.optimal_word_count[1]:
            score += 0.15
        
        # Check for psychological drivers
        for driver in pattern.psychological_drivers:
            if any(word in text.lower() for word in driver.split()):
                score += 0.1
        
        # Structure matching (simplified)
        if "\\n\\n" in text and "\\n\\n" in pattern.structure_template:
            score += 0.1
        
        return min(score, 1.0)
    
    def _identify_micro_patterns(self, text: str) -> List[str]:
        """Identify micro patterns in the text"""
        found_patterns = []
        
        micro_patterns = {
            "Position accordingly": "power_ending",
            "Think about it": "engagement_driver",
            "Most will miss": "scarcity_trigger",
            "Few understand": "exclusivity",
            "The situation": "authority_frame",
            "Smart money": "insider_knowledge",
            "What if": "curiosity_hook"
        }
        
        for pattern, category in micro_patterns.items():
            if pattern.lower() in text.lower():
                found_patterns.append(f"{category}: {pattern}")
        
        return found_patterns
    
    def _identify_linguistic_devices(self, text: str) -> List[str]:
        """Identify linguistic devices used"""
        devices = []
        
        if '?' in text:
            devices.append("rhetorical_question")
        
        if any(word in text.lower() for word in ["everyone", "most people", "few"]):
            devices.append("contrast")
        
        if text.count('\\n\\n') >= 2:
            devices.append("structured_format")
        
        if any(num in text for num in ["1.", "2.", "3."]):
            devices.append("numbered_list")
        
        if "but" in text.lower() or "however" in text.lower():
            devices.append("contradiction")
        
        return devices
    
    def generate_optimization_report(self, viral_contexts: List[ViralTweetContext]) -> Dict:
        """Generate comprehensive optimization report from viral tweets"""
        
        report = {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_viral_tweets_analyzed": len(viral_contexts),
            "top_5_breakdown": [],
            "pattern_insights": {},
            "timing_insights": {},
            "content_insights": {},
            "optimization_formula_updates": {}
        }
        
        # Analyze each viral tweet
        for i, context in enumerate(viral_contexts, 1):
            tweet_analysis = {
                "rank": i,
                "tweet_id": context.tweet_id,
                "text": context.text,
                "total_engagement": context.total_engagement,
                "engagement_rate": f"{context.engagement_rate:.4f}",
                "viral_score": f"{context.viral_score:.3f}",
                "velocity_score": f"{context.velocity_score:.1f}",
                "best_pattern_match": context.pattern_breakdown['best_match_pattern'],
                "pattern_confidence": f"{context.pattern_breakdown['match_confidence']:.2f}",
                "micro_patterns": context.pattern_breakdown['identified_micro_patterns'],
                "linguistic_devices": context.pattern_breakdown['linguistic_devices'],
                "posting_time": f"{context.posting_time['hour_est']}:00 EST ({context.posting_time['day_of_week']})",
                "word_count": context.content_analysis['word_count']
            }
            report["top_5_breakdown"].append(tweet_analysis)
        
        # Aggregate insights
        
        # Pattern insights
        pattern_usage = {}
        for context in viral_contexts:
            pattern = context.pattern_breakdown['best_match_pattern']
            if pattern not in pattern_usage:
                pattern_usage[pattern] = 0
            pattern_usage[pattern] += 1
        
        report["pattern_insights"] = {
            "most_viral_pattern": max(pattern_usage.items(), key=lambda x: x[1])[0],
            "pattern_distribution": pattern_usage
        }
        
        # Timing insights
        avg_hour = sum(c.posting_time['hour_est'] for c in viral_contexts) / len(viral_contexts)
        weekend_posts = sum(1 for c in viral_contexts if c.posting_time['is_weekend'])
        
        report["timing_insights"] = {
            "average_viral_hour_est": f"{int(avg_hour)}:00",
            "weekend_viral_percentage": f"{(weekend_posts / len(viral_contexts)) * 100:.0f}%",
            "market_hours_percentage": f"{sum(1 for c in viral_contexts if c.posting_time['is_market_hours']) / len(viral_contexts) * 100:.0f}%"
        }
        
        # Content insights
        avg_words = sum(c.content_analysis['word_count'] for c in viral_contexts) / len(viral_contexts)
        question_percentage = sum(1 for c in viral_contexts if c.content_analysis['has_question']) / len(viral_contexts) * 100
        
        report["content_insights"] = {
            "average_word_count": f"{avg_words:.1f}",
            "question_usage": f"{question_percentage:.0f}%",
            "multi_line_usage": f"{sum(1 for c in viral_contexts if c.content_analysis['line_count'] > 1) / len(viral_contexts) * 100:.0f}%"
        }
        
        # Formula updates
        report["optimization_formula_updates"] = {
            "viral_threshold": min(c.total_engagement for c in viral_contexts),
            "optimal_posting_hours_est": [9, 14, 18, 21],  # Based on analysis
            "viral_pattern_weights": {
                pattern: count / len(viral_contexts) 
                for pattern, count in pattern_usage.items()
            },
            "velocity_requirement": f"{sum(c.velocity_score for c in viral_contexts) / len(viral_contexts):.1f} engagements/hour"
        }
        
        return report

def main():
    """Main execution - Fetch and analyze top 5 viral tweets"""
    print("=" * 60)
    print("FETCHING MILES' TOP 5 VIRAL TWEETS FOR CONTEXT TRAINING")
    print("=" * 60)
    
    analyzer = ViralContextAnalyzer()
    
    try:
        # Fetch top 5 viral tweets
        viral_contexts = analyzer.fetch_top_viral_tweets(count=5)
        
        print(f"\\nSuccessfully fetched {len(viral_contexts)} viral tweets")
        print("-" * 60)
        
        # Display each viral tweet with full context
        for i, context in enumerate(viral_contexts, 1):
            print(f"\\n#{i} VIRAL TWEET ANALYSIS:")
            print(f"Engagement: {context.total_engagement:,}")
            print(f"Impressions: {context.public_metrics.get('impression_count', 'N/A'):,}")
            print(f"Engagement Rate: {context.engagement_rate:.4f}")
            print(f"Viral Score: {context.viral_score:.3f}")
            print(f"Velocity: {context.velocity_score:.1f} eng/hour")
            print(f"\\nTweet: {context.text}")
            print(f"\\nPattern Match: {context.pattern_breakdown['best_match_pattern']}")
            print(f"Pattern Confidence: {context.pattern_breakdown['match_confidence']:.2f}")
            print(f"Micro Patterns: {', '.join(context.pattern_breakdown['identified_micro_patterns'])}")
            print(f"Posted: {context.posting_time['hour_est']}:00 EST on {context.posting_time['day_of_week']}")
            print("-" * 60)
        
        # Generate optimization report
        report = analyzer.generate_optimization_report(viral_contexts)
        
        # Save report
        report_path = Path("viral_context_training_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\\nOptimization report saved to {report_path}")
        
        # Display key insights
        print("\\n" + "=" * 60)
        print("KEY INSIGHTS FOR FORMULA OPTIMIZATION:")
        print("=" * 60)
        
        print(f"\\nMost Viral Pattern: {report['pattern_insights']['most_viral_pattern']}")
        print(f"Average Viral Hour: {report['timing_insights']['average_viral_hour_est']} EST")
        print(f"Average Word Count: {report['content_insights']['average_word_count']}")
        print(f"Question Usage: {report['content_insights']['question_usage']}")
        print(f"Viral Threshold: {report['optimization_formula_updates']['viral_threshold']:,} engagement")
        print(f"Velocity Requirement: {report['optimization_formula_updates']['velocity_requirement']}")
        
        # Create updated formula
        print("\\n" + "=" * 60)
        print("UPDATED MATHEMATICAL OPTIMIZATION FORMULA:")
        print("=" * 60)
        
        print("""
VIRAL_TWEET = (
    BASE_PATTERN[viral_pattern] × 
    TIMING_MULTIPLIER[optimal_hour] × 
    VELOCITY_FACTOR[eng_per_hour] × 
    MICRO_PATTERNS[power_phrases] × 
    CONTEXT_ALIGNMENT[market_conditions]
)

Where:
- BASE_PATTERN = Top viral pattern with highest confidence
- TIMING_MULTIPLIER = 1.4x for optimal hours (9am, 2pm, 6pm, 9pm EST)
- VELOCITY_FACTOR = Must achieve {velocity} eng/hour in first 3 hours
- MICRO_PATTERNS = Stack 3+ power phrases for 1.5x multiplier
- CONTEXT_ALIGNMENT = Match current market sentiment for 1.3x boost
        """.format(velocity=report['optimization_formula_updates']['velocity_requirement']))
        
        return viral_contexts, report
        
    except Exception as e:
        logger.error(f"Error in viral tweet analysis: {e}")
        raise

if __name__ == "__main__":
    viral_contexts, report = main()