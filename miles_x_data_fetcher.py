"""
Miles Deutscher X/Twitter Data Fetcher
Pulls comprehensive tweet data using X Pro API
"""
import requests
import json
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from collections import defaultdict

# Import our secure credential management
try:
    from config.credentials import credential_manager
except:
    # Fallback for direct execution
    import sys
    sys.path.append(str(Path(__file__).parent))
    from config.credentials import credential_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TweetData:
    """Structured tweet data"""
    id: str
    text: str
    created_at: str
    author_id: str
    conversation_id: str
    in_reply_to_user_id: Optional[str] = None
    referenced_tweets: Optional[List[Dict]] = None
    public_metrics: Optional[Dict[str, int]] = None
    context_annotations: Optional[List[Dict]] = None
    entities: Optional[Dict] = None
    lang: Optional[str] = None
    possibly_sensitive: Optional[bool] = None
    
    @property
    def engagement_score(self) -> float:
        """Calculate engagement score"""
        if not self.public_metrics:
            return 0.0
        
        metrics = self.public_metrics
        score = (
            metrics.get('like_count', 0) * 1.0 +
            metrics.get('retweet_count', 0) * 2.0 +
            metrics.get('reply_count', 0) * 1.5 +
            metrics.get('quote_count', 0) * 3.0
        )
        
        # Normalize by impressions if available
        impressions = metrics.get('impression_count', 0)
        if impressions > 0:
            score = (score / impressions) * 10000
        
        return round(score, 2)
    
    @property
    def is_original(self) -> bool:
        """Check if this is an original tweet (not reply or retweet)"""
        if self.referenced_tweets:
            for ref in self.referenced_tweets:
                if ref.get('type') in ['retweeted', 'quoted']:
                    return False
        return self.in_reply_to_user_id is None
    
    def to_training_format(self) -> Dict[str, Any]:
        """Convert to training data format"""
        return {
            "prompt": "Write a tweet in the style of Miles Deutscher:",
            "completion": f" {self.text}",
            "metadata": {
                "tweet_id": self.id,
                "created_at": self.created_at,
                "engagement_score": self.engagement_score,
                "metrics": self.public_metrics,
                "lang": self.lang,
                "is_original": self.is_original,
                "char_count": len(self.text),
                "word_count": len(self.text.split())
            }
        }

class MilesDataFetcher:
    """Fetches and processes Miles Deutscher's X/Twitter data"""
    
    BASE_URL = "https://api.twitter.com/2"
    MILES_USERNAME = "milesdeutscher"
    
    def __init__(self):
        self.headers = credential_manager.get_headers()
        self.user_id = None
        self.rate_limit_remaining = 300
        self.rate_limit_reset = None
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with rate limit handling"""
        url = f"{self.BASE_URL}{endpoint}"
        
        # Check rate limits
        if self.rate_limit_remaining <= 1:
            if self.rate_limit_reset:
                sleep_time = self.rate_limit_reset - time.time()
                if sleep_time > 0:
                    logger.info(f"Rate limit reached. Sleeping for {sleep_time:.0f} seconds...")
                    time.sleep(sleep_time + 1)
        
        response = requests.get(url, headers=self.headers, params=params)
        
        # Update rate limit info
        self.rate_limit_remaining = int(response.headers.get('x-rate-limit-remaining', 300))
        reset_timestamp = response.headers.get('x-rate-limit-reset')
        if reset_timestamp:
            self.rate_limit_reset = int(reset_timestamp)
        
        if response.status_code != 200:
            logger.error(f"API request failed: {response.status_code} - {response.text}")
            response.raise_for_status()
        
        return response.json()
    
    def get_user_id(self) -> str:
        """Get Miles Deutscher's user ID"""
        if self.user_id:
            return self.user_id
        
        endpoint = f"/users/by/username/{self.MILES_USERNAME}"
        data = self._make_request(endpoint)
        
        if 'data' in data:
            self.user_id = data['data']['id']
            logger.info(f"Found user ID for @{self.MILES_USERNAME}: {self.user_id}")
            return self.user_id
        
        raise ValueError(f"Could not find user @{self.MILES_USERNAME}")
    
    def fetch_tweets(self, max_results: int = 100, limit: Optional[int] = None) -> List[TweetData]:
        """
        Fetch tweets from Miles Deutscher
        
        Args:
            max_results: Number of tweets per request (10-100)
            limit: Total number of tweets to fetch (None for all available)
        """
        user_id = self.get_user_id()
        endpoint = f"/users/{user_id}/tweets"
        
        # Tweet fields to request
        tweet_fields = [
            "id", "text", "created_at", "author_id", "conversation_id",
            "in_reply_to_user_id", "referenced_tweets", "public_metrics",
            "context_annotations", "entities", "lang", "possibly_sensitive"
        ]
        
        params = {
            "max_results": min(max_results, 100),
            "tweet.fields": ",".join(tweet_fields),
            "exclude": "replies"  # Exclude replies to focus on original content
        }
        
        all_tweets = []
        pagination_token = None
        
        while True:
            if pagination_token:
                params['pagination_token'] = pagination_token
            
            logger.info(f"Fetching tweets... (collected: {len(all_tweets)})")
            data = self._make_request(endpoint, params)
            
            if 'data' in data:
                tweets = [TweetData(**tweet) for tweet in data['data']]
                all_tweets.extend(tweets)
                
                logger.info(f"Fetched {len(tweets)} tweets. Total: {len(all_tweets)}")
            
            # Check if we've reached the limit
            if limit and len(all_tweets) >= limit:
                all_tweets = all_tweets[:limit]
                break
            
            # Check for next page
            if 'meta' in data and 'next_token' in data['meta']:
                pagination_token = data['meta']['next_token']
            else:
                break
        
        return all_tweets
    
    def analyze_tweet_patterns(self, tweets: List[TweetData]) -> Dict[str, Any]:
        """Analyze patterns in Miles' tweets"""
        analysis = {
            "total_tweets": len(tweets),
            "original_tweets": sum(1 for t in tweets if t.is_original),
            "languages": defaultdict(int),
            "engagement_stats": {
                "avg_likes": 0,
                "avg_retweets": 0,
                "avg_replies": 0,
                "avg_quotes": 0,
                "avg_impressions": 0,
                "avg_engagement_score": 0
            },
            "content_stats": {
                "avg_char_length": 0,
                "avg_word_count": 0,
                "contains_media": 0,
                "contains_urls": 0,
                "contains_hashtags": 0
            },
            "time_patterns": defaultdict(int),
            "top_tweets": []
        }
        
        # Calculate statistics
        total_metrics = defaultdict(int)
        char_lengths = []
        word_counts = []
        engagement_scores = []
        
        for tweet in tweets:
            # Language distribution
            if tweet.lang:
                analysis["languages"][tweet.lang] += 1
            
            # Engagement metrics
            if tweet.public_metrics:
                for metric, value in tweet.public_metrics.items():
                    total_metrics[metric] += value
                engagement_scores.append(tweet.engagement_score)
            
            # Content analysis
            char_lengths.append(len(tweet.text))
            word_counts.append(len(tweet.text.split()))
            
            if tweet.entities:
                if tweet.entities.get('media'):
                    analysis["content_stats"]["contains_media"] += 1
                if tweet.entities.get('urls'):
                    analysis["content_stats"]["contains_urls"] += 1
                if tweet.entities.get('hashtags'):
                    analysis["content_stats"]["contains_hashtags"] += 1
            
            # Time patterns (hour of day)
            created_time = datetime.fromisoformat(tweet.created_at.replace('Z', '+00:00'))
            hour = created_time.hour
            analysis["time_patterns"][hour] += 1
        
        # Calculate averages
        if tweets:
            tweet_count = len(tweets)
            analysis["engagement_stats"]["avg_likes"] = round(total_metrics["like_count"] / tweet_count, 2)
            analysis["engagement_stats"]["avg_retweets"] = round(total_metrics["retweet_count"] / tweet_count, 2)
            analysis["engagement_stats"]["avg_replies"] = round(total_metrics["reply_count"] / tweet_count, 2)
            analysis["engagement_stats"]["avg_quotes"] = round(total_metrics["quote_count"] / tweet_count, 2)
            
            if total_metrics["impression_count"] > 0:
                analysis["engagement_stats"]["avg_impressions"] = round(total_metrics["impression_count"] / tweet_count, 2)
            
            if engagement_scores:
                analysis["engagement_stats"]["avg_engagement_score"] = round(sum(engagement_scores) / len(engagement_scores), 2)
            
            analysis["content_stats"]["avg_char_length"] = round(sum(char_lengths) / len(char_lengths), 2)
            analysis["content_stats"]["avg_word_count"] = round(sum(word_counts) / len(word_counts), 2)
        
        # Get top tweets by engagement
        sorted_tweets = sorted(tweets, key=lambda t: t.engagement_score, reverse=True)[:10]
        analysis["top_tweets"] = [
            {
                "id": t.id,
                "text": t.text[:100] + "..." if len(t.text) > 100 else t.text,
                "engagement_score": t.engagement_score,
                "metrics": t.public_metrics
            }
            for t in sorted_tweets
        ]
        
        return analysis
    
    def save_to_json(self, tweets: List[TweetData], filename: str = "miles_tweets_data.json"):
        """Save tweets to JSON file"""
        output_path = Path(filename)
        
        # Convert to dictionaries
        data = {
            "metadata": {
                "username": self.MILES_USERNAME,
                "user_id": self.user_id,
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "total_tweets": len(tweets),
                "original_tweets": sum(1 for t in tweets if t.is_original)
            },
            "tweets": [asdict(tweet) for tweet in tweets],
            "analysis": self.analyze_tweet_patterns(tweets)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(tweets)} tweets to {output_path}")
        return output_path
    
    def save_training_data(self, tweets: List[TweetData], filename: str = "miles_training_data.jsonl"):
        """Save tweets in training format (JSONL)"""
        output_path = Path(filename)
        
        # Filter for high-quality original tweets
        training_tweets = [
            tweet for tweet in tweets 
            if tweet.is_original and tweet.engagement_score > 50
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for tweet in training_tweets:
                training_data = tweet.to_training_format()
                f.write(json.dumps(training_data, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(training_tweets)} training examples to {output_path}")
        return output_path

def main():
    """Main execution function"""
    logger.info("Starting Miles Deutscher X data collection...")
    
    fetcher = MilesDataFetcher()
    
    try:
        # Fetch tweets (adjust limit as needed)
        tweets = fetcher.fetch_tweets(max_results=100, limit=1000)
        logger.info(f"Successfully fetched {len(tweets)} tweets")
        
        # Save raw data
        json_path = fetcher.save_to_json(tweets, "miles_x_data_complete.json")
        
        # Save training data
        training_path = fetcher.save_training_data(tweets, "miles_x_training_data.jsonl")
        
        # Print analysis summary
        analysis = fetcher.analyze_tweet_patterns(tweets)
        print("\n=== Miles Deutscher Tweet Analysis ===")
        print(f"Total tweets collected: {analysis['total_tweets']}")
        print(f"Original tweets: {analysis['original_tweets']}")
        print(f"Average engagement score: {analysis['engagement_stats']['avg_engagement_score']}")
        print(f"Average likes: {analysis['engagement_stats']['avg_likes']}")
        print(f"Average retweets: {analysis['engagement_stats']['avg_retweets']}")
        print(f"\nTop performing tweet:")
        if analysis['top_tweets']:
            top = analysis['top_tweets'][0]
            print(f"  Score: {top['engagement_score']}")
            print(f"  Text: {top['text']}")
        
    except Exception as e:
        logger.error(f"Error during data collection: {e}")
        raise

if __name__ == "__main__":
    main()