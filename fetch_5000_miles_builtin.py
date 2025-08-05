"""
Fetch 5000 latest tweets from Miles Deutscher via X API v2
Using only built-in Python modules
"""
import json
import time
from datetime import datetime
import urllib.request
import urllib.parse
import urllib.error
import base64
from typing import List, Dict, Optional
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MilesTweetFetcher5000:
    def __init__(self):
        """Initialize with X API credentials"""
        # Bearer token
        self.bearer_token = 'AAAAAAAAAAAAAAAAAAAAAEjxuAEAAAAA0e0MZ3z5kqjQz34A5JVAp8lVNyA%3DibqZVQYAz7LrYxQ6IqjSOSzjOwsHyjqQEHgVyGiCqtqiXrClxA'
        
        # API endpoints
        self.base_url = 'https://api.twitter.com/2'
        
        # Miles Deutscher's info
        self.username = "milesdeutscher"
        self.user_id = None
        
    def make_request(self, url: str) -> Dict:
        """Make authenticated request to Twitter API"""
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'User-Agent': 'MilesDeutscherAI/1.0'
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(request) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limit
                logging.warning("Rate limit hit, waiting...")
                time.sleep(60)  # Wait 1 minute
                return self.make_request(url)  # Retry
            else:
                logging.error(f"HTTP Error {e.code}: {e.reason}")
                raise
        except Exception as e:
            logging.error(f"Request error: {e}")
            raise
    
    def get_user_id(self) -> str:
        """Get Miles Deutscher's user ID"""
        url = f"{self.base_url}/users/by/username/{self.username}"
        
        try:
            response = self.make_request(url)
            if 'data' in response:
                self.user_id = response['data']['id']
                logging.info(f"Found user {self.username} with ID: {self.user_id}")
                return self.user_id
            else:
                raise Exception("User not found")
        except Exception as e:
            logging.error(f"Error getting user ID: {e}")
            # Use known ID as fallback
            self.user_id = "1042881640908840960"  # Miles Deutscher's known ID
            return self.user_id
    
    def fetch_5000_tweets(self) -> List[Dict]:
        """Fetch up to 5000 recent tweets from Miles"""
        if not self.user_id:
            self.get_user_id()
        
        all_tweets = []
        next_token = None
        total_fetched = 0
        
        # Build query parameters
        params = {
            'max_results': '100',
            'tweet.fields': 'id,text,created_at,author_id,conversation_id,in_reply_to_user_id,referenced_tweets,attachments,entities,public_metrics,possibly_sensitive,lang,reply_settings,source',
            'exclude': 'retweets'
        }
        
        logging.info("Starting to fetch tweets...")
        
        while total_fetched < 5000:
            try:
                # Add pagination token if available
                if next_token:
                    params['pagination_token'] = next_token
                
                # Build URL with parameters
                query_string = urllib.parse.urlencode(params)
                url = f"{self.base_url}/users/{self.user_id}/tweets?{query_string}"
                
                # Make request
                response = self.make_request(url)
                
                if not response.get('data'):
                    logging.info("No more tweets available")
                    break
                
                # Process tweets
                for tweet in response['data']:
                    tweet_data = self.process_tweet(tweet)
                    all_tweets.append(tweet_data)
                
                total_fetched += len(response['data'])
                logging.info(f"Fetched {total_fetched} tweets so far...")
                
                # Check for next page
                if 'meta' in response and 'next_token' in response['meta']:
                    next_token = response['meta']['next_token']
                else:
                    logging.info("No more pages available")
                    break
                
                # Rate limit respect
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error fetching tweets: {e}")
                break
        
        logging.info(f"Successfully fetched {len(all_tweets)} tweets")
        return all_tweets
    
    def process_tweet(self, tweet: Dict) -> Dict:
        """Process a single tweet into structured format"""
        text = tweet.get('text', '')
        
        # Get metrics with defaults
        metrics = tweet.get('public_metrics', {})
        
        # Build structured data
        structured_tweet = {
            # Core identifiers
            "id": tweet.get('id'),
            "created_at": tweet.get('created_at', ''),
            
            # Content
            "text": text,
            "clean_text": self.clean_text(text),
            
            # Metadata
            "type": self.classify_tweet_type(tweet),
            "pattern": self.detect_pattern(text),
            "word_count": len(text.split()),
            "char_count": len(text),
            
            # Engagement metrics
            "metrics": {
                "likes": metrics.get('like_count', 0),
                "retweets": metrics.get('retweet_count', 0),
                "replies": metrics.get('reply_count', 0),
                "quotes": metrics.get('quote_count', 0),
                "impressions": metrics.get('impression_count', 0)
            },
            
            # Calculated metrics
            "engagement_rate": self.calculate_engagement_rate(metrics),
            "virality_score": self.calculate_virality_score(metrics),
            
            # Content analysis
            "entities": self.extract_entities(tweet.get('entities', {})),
            
            # Context
            "is_reply": tweet.get('in_reply_to_user_id') is not None,
            "is_thread": tweet.get('conversation_id') == tweet.get('id'),
            "has_media": bool(tweet.get('attachments', {}).get('media_keys', [])),
            
            # Additional metadata
            "source": tweet.get('source', 'unknown'),
            "language": tweet.get('lang', 'en'),
            "possibly_sensitive": tweet.get('possibly_sensitive', False),
            
            # For AI training
            "quality_score": self.calculate_quality_score(metrics, text),
            "topic_categories": self.categorize_topics(text),
            "sentiment": self.analyze_sentiment(text),
            "key_phrases": self.extract_key_phrases(text)
        }
        
        return structured_tweet
    
    def extract_entities(self, entities: Dict) -> Dict:
        """Extract entities from tweet"""
        return {
            "hashtags": [tag.get('tag', '') for tag in entities.get('hashtags', [])],
            "mentions": [mention.get('username', '') for mention in entities.get('mentions', [])],
            "urls": [url.get('expanded_url', url.get('url', '')) for url in entities.get('urls', [])],
            "cashtags": [tag.get('tag', '') for tag in entities.get('cashtags', [])]
        }
    
    def classify_tweet_type(self, tweet: Dict) -> str:
        """Classify the type of tweet"""
        text = tweet.get('text', '').lower()
        
        if tweet.get('in_reply_to_user_id'):
            return "reply"
        elif any(indicator in text for indicator in ['thread', '1/', '🧵']):
            return "thread"
        elif any(q in text for q in ['?', 'what do you think', 'thoughts']):
            return "question"
        elif any(url in text for url in ['http://', 'https://', 't.co']):
            return "link_share"
        elif len(text.split()) < 20:
            return "short_take"
        else:
            return "analysis"
    
    def detect_pattern(self, text: str) -> str:
        """Detect Miles' tweet patterns"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if len(lines) == 1:
            return "1_part"
        elif len(lines) == 2:
            return "2_part"
        elif len(lines) == 3:
            if any(word in lines[0].lower() for word in ['everyone', 'most', 'people']):
                return "3_part_classic"
            return "3_part"
        elif len(lines) == 4:
            return "4_part"
        elif len(lines) == 5:
            return "5_part"
        elif len(lines) <= 7:
            return "7_part"
        else:
            return f"{len(lines)}_part"
    
    def clean_text(self, text: str) -> str:
        """Clean text for training"""
        # Remove URLs
        import re
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r't\.co/\S+', '', text)
        
        # Clean whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def calculate_engagement_rate(self, metrics: Dict) -> float:
        """Calculate engagement rate"""
        total_engagement = (
            metrics.get('like_count', 0) +
            metrics.get('retweet_count', 0) +
            metrics.get('reply_count', 0) +
            metrics.get('quote_count', 0)
        )
        
        # Normalize by 10k impressions average
        return round(total_engagement / 10000, 4)
    
    def calculate_virality_score(self, metrics: Dict) -> float:
        """Calculate virality score (0-1)"""
        score = (
            metrics.get('like_count', 0) * 1 +
            metrics.get('retweet_count', 0) * 3 +
            metrics.get('reply_count', 0) * 2 +
            metrics.get('quote_count', 0) * 4
        )
        
        return min(1.0, round(score / 10000, 4))
    
    def calculate_quality_score(self, metrics: Dict, text: str) -> float:
        """Calculate quality score for training"""
        score = 0.5
        
        # Engagement boost
        if metrics.get('like_count', 0) > 100:
            score += 0.1
        if metrics.get('retweet_count', 0) > 50:
            score += 0.1
        
        # Length preference
        word_count = len(text.split())
        if 20 <= word_count <= 100:
            score += 0.1
        
        # Pattern bonus
        if any(pattern in self.detect_pattern(text) for pattern in ['3_part', '5_part', '7_part']):
            score += 0.1
        
        # No links bonus
        if 'http' not in text:
            score += 0.1
        
        return min(1.0, round(score, 2))
    
    def categorize_topics(self, text: str) -> List[str]:
        """Categorize tweet topics"""
        text_lower = text.lower()
        categories = []
        
        # Crypto topics
        if any(term in text_lower for term in ['btc', 'bitcoin', 'eth', 'ethereum']):
            categories.append('crypto_analysis')
        if any(term in text_lower for term in ['alt', 'altcoin', 'alts']):
            categories.append('altcoins')
        if any(term in text_lower for term in ['trade', 'trading', 'position']):
            categories.append('trading')
        if any(term in text_lower for term in ['bull', 'bear', 'market']):
            categories.append('market_analysis')
        
        # Mindset
        if any(term in text_lower for term in ['think', 'believe', 'mindset']):
            categories.append('philosophy')
        
        # DeFi
        if any(term in text_lower for term in ['defi', 'yield', 'farm']):
            categories.append('defi')
        
        return categories if categories else ['general']
    
    def analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        text_lower = text.lower()
        
        bearish_words = ['crash', 'dump', 'bear', 'down', 'sell', 'fear']
        bullish_words = ['moon', 'pump', 'bull', 'up', 'buy', 'greed']
        
        bearish_count = sum(1 for word in bearish_words if word in text_lower)
        bullish_count = sum(1 for word in bullish_words if word in text_lower)
        
        if bearish_count > bullish_count:
            return "bearish"
        elif bullish_count > bearish_count:
            return "bullish"
        else:
            return "neutral"
    
    def extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases"""
        phrases = []
        
        # Common Miles patterns
        patterns = [
            "Few understand", "Most people", "The real", "Everyone thinks",
            "What matters", "The game", "Real alpha", "Think about",
            "Remember:", "Truth:"
        ]
        
        for pattern in patterns:
            if pattern in text:
                phrases.append(pattern)
        
        return phrases[:5]
    
    def save_structured_data(self, tweets: List[Dict], filename: str = "miles_5000_tweets_structured.json"):
        """Save structured tweet data"""
        output = {
            "metadata": {
                "source": "X API v2",
                "username": self.username,
                "user_id": self.user_id,
                "fetch_date": datetime.now().isoformat(),
                "total_tweets": len(tweets),
                "api_version": "2.0",
                "structure_version": "1.0"
            },
            "statistics": self.calculate_statistics(tweets),
            "tweets": tweets
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Saved {len(tweets)} structured tweets to {filename}")
        
        # Also save as JSONL
        jsonl_filename = filename.replace('.json', '.jsonl')
        with open(jsonl_filename, 'w', encoding='utf-8') as f:
            for tweet in tweets:
                f.write(json.dumps(tweet, ensure_ascii=False) + '\n')
        
        logging.info(f"Also saved as JSONL: {jsonl_filename}")
    
    def calculate_statistics(self, tweets: List[Dict]) -> Dict:
        """Calculate statistics"""
        if not tweets:
            return {}
        
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
        
        # Quality scores
        quality_scores = [t['quality_score'] for t in tweets]
        
        return {
            "total_tweets": len(tweets),
            "engagement": {
                "total_likes": total_likes,
                "total_retweets": total_retweets,
                "avg_likes": round(total_likes / len(tweets), 2),
                "avg_retweets": round(total_retweets / len(tweets), 2)
            },
            "patterns": pattern_counts,
            "topics": topic_counts,
            "quality": {
                "average": round(sum(quality_scores) / len(quality_scores), 3),
                "high_quality_count": sum(1 for s in quality_scores if s >= 0.7)
            }
        }

def main():
    """Main execution"""
    print("=== Miles Deutscher 5000 Tweet Fetcher ===\n")
    
    fetcher = MilesTweetFetcher5000()
    
    try:
        print("Fetching tweets from @milesdeutscher...")
        tweets = fetcher.fetch_5000_tweets()
        
        if tweets:
            fetcher.save_structured_data(tweets)
            
            print(f"\n[SUCCESS] Fetched and structured {len(tweets)} tweets!")
            print("\nFiles created:")
            print("- miles_5000_tweets_structured.json")
            print("- miles_5000_tweets_structured.jsonl")
            
            stats = fetcher.calculate_statistics(tweets)
            print("\nStatistics:")
            print(f"- Average likes: {stats['engagement']['avg_likes']}")
            print(f"- High quality tweets: {stats['quality']['high_quality_count']}")
            
        else:
            print("[ERROR] No tweets fetched")
            
    except Exception as e:
        print(f"[ERROR] Failed: {e}")

if __name__ == "__main__":
    main()