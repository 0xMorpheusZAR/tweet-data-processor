"""
Fetch Miles Deutscher tweets using live X/Twitter API v2
With updated credentials
"""
import json
import time
from datetime import datetime
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Dict
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MilesTweetFetcherLive:
    def __init__(self):
        """Initialize with new X API credentials"""
        # Updated credentials
        self.api_key = "TSNUMvJt8cZaS9EhIvVdgFcYA"
        self.api_secret = "H3uGj69Wqm50AHiVmNAFL1XYdPSIdvnJwRfuEezT8dAZglga1e"
        self.bearer_token = "AAAAAAAAAAAAAAAAAAAAAJi13QEAAAAAghVwuLws1YdchbwCAkUjqqwu6oc%3DeImrILD6DNOvuOdZiH42oFM3Ww7zTLYaiz1onypLp8XNzCskQ7"
        
        # API endpoints
        self.base_url = 'https://api.twitter.com/2'
        
        # Miles Deutscher's info
        self.username = "milesdeutscher"
        self.user_id = None
        
    def make_request(self, url: str, method: str = "GET") -> Dict:
        """Make authenticated request to Twitter API"""
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'User-Agent': 'MilesDeutscherAI/2.0',
            'Content-Type': 'application/json'
        }
        
        request = urllib.request.Request(url, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(request) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            logging.error(f"HTTP Error {e.code}: {e.reason}")
            logging.error(f"Error details: {error_body}")
            
            if e.code == 429:  # Rate limit
                reset_time = e.headers.get('x-rate-limit-reset')
                if reset_time:
                    wait_time = int(reset_time) - int(time.time())
                    logging.info(f"Rate limit hit. Waiting {wait_time} seconds...")
                    time.sleep(max(wait_time, 60))
                    return self.make_request(url, method)  # Retry
            raise
        except Exception as e:
            logging.error(f"Request error: {e}")
            raise
    
    def get_user_id(self) -> str:
        """Get Miles Deutscher's user ID"""
        url = f"{self.base_url}/users/by/username/{self.username}"
        
        try:
            logging.info(f"Fetching user ID for @{self.username}...")
            response = self.make_request(url)
            
            if 'data' in response:
                self.user_id = response['data']['id']
                logging.info(f"Found user {self.username} with ID: {self.user_id}")
                return self.user_id
            else:
                logging.error(f"User not found: {response}")
                raise Exception("User not found")
                
        except Exception as e:
            logging.error(f"Error getting user ID: {e}")
            raise
    
    def fetch_tweets(self, max_tweets: int = 3200) -> List[Dict]:
        """Fetch tweets from Miles (API limit is 3200 most recent)"""
        if not self.user_id:
            self.get_user_id()
        
        all_tweets = []
        next_token = None
        total_fetched = 0
        
        # Tweet fields to retrieve
        tweet_fields = [
            'id', 'text', 'created_at', 'author_id',
            'conversation_id', 'in_reply_to_user_id',
            'referenced_tweets', 'attachments', 'entities',
            'public_metrics', 'possibly_sensitive', 'lang',
            'reply_settings', 'source', 'context_annotations',
            'geo', 'withheld'
        ]
        
        # Build base params
        params = {
            'max_results': '100',  # Max per request
            'tweet.fields': ','.join(tweet_fields),
            'exclude': 'retweets,replies'  # Original tweets only
        }
        
        logging.info(f"Starting to fetch tweets (max: {max_tweets})...")
        
        while total_fetched < max_tweets:
            try:
                # Add pagination token if available
                current_params = params.copy()
                if next_token:
                    current_params['pagination_token'] = next_token
                
                # Build URL
                query_string = urllib.parse.urlencode(current_params)
                url = f"{self.base_url}/users/{self.user_id}/tweets?{query_string}"
                
                # Make request
                logging.info(f"Fetching batch... (current total: {total_fetched})")
                response = self.make_request(url)
                
                if not response.get('data'):
                    logging.info("No more tweets available")
                    break
                
                # Process tweets
                batch_tweets = []
                for tweet in response['data']:
                    processed = self.process_tweet(tweet)
                    batch_tweets.append(processed)
                    all_tweets.append(processed)
                
                batch_size = len(batch_tweets)
                total_fetched += batch_size
                logging.info(f"Fetched {batch_size} tweets in this batch (total: {total_fetched})")
                
                # Log sample tweet
                if batch_tweets:
                    sample = batch_tweets[0]
                    logging.info(f"Sample tweet: {sample['text'][:100]}...")
                    logging.info(f"Engagement: {sample['metrics']['likes']} likes, {sample['metrics']['retweets']} RTs")
                
                # Check for next page
                if 'meta' in response and 'next_token' in response['meta']:
                    next_token = response['meta']['next_token']
                else:
                    logging.info("No more pages available")
                    break
                
                # Rate limit respect (300 requests per 15 min = 1 per 3 seconds)
                time.sleep(3)
                
            except Exception as e:
                logging.error(f"Error fetching tweets: {e}")
                if "503" in str(e):
                    logging.info("Service unavailable, waiting 30 seconds...")
                    time.sleep(30)
                    continue
                break
        
        logging.info(f"Successfully fetched {len(all_tweets)} tweets total")
        return all_tweets
    
    def process_tweet(self, tweet: Dict) -> Dict:
        """Process tweet into structured format"""
        text = tweet.get('text', '')
        metrics = tweet.get('public_metrics', {})
        
        # Calculate engagement metrics
        total_engagement = (
            metrics.get('like_count', 0) +
            metrics.get('retweet_count', 0) * 3 +
            metrics.get('reply_count', 0) * 2 +
            metrics.get('quote_count', 0) * 4
        )
        
        # Detect pattern
        pattern = self.detect_pattern(text)
        
        # Build structured data
        structured_tweet = {
            # Core fields
            "id": tweet.get('id'),
            "created_at": tweet.get('created_at', ''),
            "text": text,
            "clean_text": self.clean_text(text),
            
            # Metadata
            "type": self.classify_tweet_type(tweet),
            "pattern": pattern,
            "word_count": len(text.split()),
            "char_count": len(text),
            
            # Engagement
            "metrics": {
                "likes": metrics.get('like_count', 0),
                "retweets": metrics.get('retweet_count', 0),
                "replies": metrics.get('reply_count', 0),
                "quotes": metrics.get('quote_count', 0),
                "impressions": metrics.get('impression_count', 0),
                "bookmarks": metrics.get('bookmark_count', 0)
            },
            
            # Calculated metrics
            "engagement_rate": round(total_engagement / max(metrics.get('impression_count', 10000), 1), 4),
            "virality_score": min(1.0, round(total_engagement / 10000, 4)),
            "quality_score": self.calculate_quality_score(metrics, text, pattern),
            
            # Entities
            "entities": self.extract_entities(tweet.get('entities', {})),
            
            # Context
            "is_reply": tweet.get('in_reply_to_user_id') is not None,
            "is_thread": tweet.get('conversation_id') == tweet.get('id'),
            "has_media": bool(tweet.get('attachments', {}).get('media_keys', [])),
            
            # Additional
            "source": tweet.get('source', 'unknown'),
            "language": tweet.get('lang', 'en'),
            "possibly_sensitive": tweet.get('possibly_sensitive', False),
            
            # AI training fields
            "topic_categories": self.categorize_topics(text),
            "sentiment": self.analyze_sentiment(text),
            "key_phrases": self.extract_key_phrases(text)
        }
        
        return structured_tweet
    
    def detect_pattern(self, text: str) -> str:
        """Detect Miles' tweet patterns"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if len(lines) == 1:
            return "1_part"
        elif len(lines) == 2:
            return "2_part"
        elif len(lines) == 3:
            # Check for classic pattern
            if any(word in lines[0].lower() for word in ['everyone', 'most', 'people', 'the crowd']):
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
        import re
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r't\.co/\S+', '', text)
        # Clean whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    def calculate_quality_score(self, metrics: Dict, text: str, pattern: str) -> float:
        """Calculate quality score"""
        score = 0.5  # Base
        
        # Engagement boost
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        
        if likes > 1000:
            score += 0.2
        elif likes > 500:
            score += 0.15
        elif likes > 100:
            score += 0.1
        
        if retweets > 100:
            score += 0.1
        
        # Pattern bonus
        if pattern in ['3_part_classic', '5_part', '7_part']:
            score += 0.1
        
        # Length preference
        word_count = len(text.split())
        if 30 <= word_count <= 150:
            score += 0.1
        
        return min(1.0, round(score, 2))
    
    def extract_entities(self, entities: Dict) -> Dict:
        """Extract entities"""
        return {
            "hashtags": [tag.get('tag', '') for tag in entities.get('hashtags', [])],
            "mentions": [m.get('username', '') for m in entities.get('mentions', [])],
            "urls": [u.get('expanded_url', u.get('url', '')) for u in entities.get('urls', [])],
            "cashtags": [c.get('tag', '') for c in entities.get('cashtags', [])]
        }
    
    def categorize_topics(self, text: str) -> List[str]:
        """Categorize topics"""
        text_lower = text.lower()
        categories = []
        
        topic_keywords = {
            'crypto_analysis': ['btc', 'bitcoin', 'eth', 'ethereum', 'crypto'],
            'altcoins': ['alt', 'alts', 'altcoin', 'altseason'],
            'trading': ['trade', 'trading', 'position', 'entry', 'exit'],
            'market_analysis': ['market', 'bull', 'bear', 'trend', 'cycle'],
            'defi': ['defi', 'yield', 'apy', 'liquidity', 'protocol'],
            'philosophy': ['think', 'mindset', 'believe', 'understand']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(topic)
        
        return categories if categories else ['general']
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment"""
        text_lower = text.lower()
        
        bearish_words = ['crash', 'dump', 'bear', 'down', 'sell', 'fear', 'bottom', 'capitulation']
        bullish_words = ['moon', 'pump', 'bull', 'up', 'buy', 'bullish', 'breakout', 'rally']
        
        bearish_count = sum(1 for word in bearish_words if word in text_lower)
        bullish_count = sum(1 for word in bullish_words if word in text_lower)
        
        if bearish_count > bullish_count:
            return "bearish"
        elif bullish_count > bearish_count:
            return "bullish"
        else:
            return "neutral"
    
    def classify_tweet_type(self, tweet: Dict) -> str:
        """Classify the type of tweet"""
        text = tweet.get('text', '').lower()
        
        if tweet.get('in_reply_to_user_id'):
            return "reply"
        elif any(indicator in text for indicator in ['thread', '1/', '🧵']):
            return "thread"
        elif '?' in text:
            return "question"
        elif any(url in text for url in ['http://', 'https://', 't.co']):
            return "link_share"
        elif len(text.split()) < 20:
            return "short_take"
        else:
            return "analysis"
    
    def extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases"""
        phrases = []
        
        # Common Miles phrases
        key_patterns = [
            "Few understand", "Few get it", "Few will make it",
            "Most people", "Everyone thinks", "The crowd",
            "What matters", "The real", "Think about",
            "Position accordingly", "Plan accordingly",
            "This is the way", "Study this", "Remember this"
        ]
        
        for pattern in key_patterns:
            if pattern.lower() in text.lower():
                phrases.append(pattern)
        
        return phrases[:5]
    
    def save_tweets(self, tweets: List[Dict], filename: str = "miles_tweets_live.json"):
        """Save fetched tweets"""
        output = {
            "metadata": {
                "source": "X API v2 (Live)",
                "username": self.username,
                "user_id": self.user_id,
                "fetch_date": datetime.now().isoformat(),
                "total_tweets": len(tweets),
                "api_version": "2.0"
            },
            "statistics": self.calculate_statistics(tweets),
            "tweets": tweets
        }
        
        # Save JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        logging.info(f"Saved {len(tweets)} tweets to {filename}")
        
        # Save JSONL
        jsonl_filename = filename.replace('.json', '.jsonl')
        with open(jsonl_filename, 'w', encoding='utf-8') as f:
            for tweet in tweets:
                f.write(json.dumps(tweet, ensure_ascii=False) + '\n')
        logging.info(f"Also saved as JSONL: {jsonl_filename}")
    
    def calculate_statistics(self, tweets: List[Dict]) -> Dict:
        """Calculate statistics"""
        if not tweets:
            return {}
        
        # Basic stats
        total_likes = sum(t['metrics']['likes'] for t in tweets)
        total_retweets = sum(t['metrics']['retweets'] for t in tweets)
        
        # Pattern distribution
        pattern_counts = {}
        for tweet in tweets:
            pattern = tweet['pattern']
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Quality distribution
        quality_scores = [t['quality_score'] for t in tweets]
        high_quality = sum(1 for s in quality_scores if s >= 0.7)
        
        return {
            "total_tweets": len(tweets),
            "date_range": {
                "earliest": min(t['created_at'] for t in tweets) if tweets else "",
                "latest": max(t['created_at'] for t in tweets) if tweets else ""
            },
            "engagement": {
                "total_likes": total_likes,
                "total_retweets": total_retweets,
                "avg_likes": round(total_likes / len(tweets), 2) if tweets else 0,
                "avg_retweets": round(total_retweets / len(tweets), 2) if tweets else 0
            },
            "patterns": pattern_counts,
            "quality": {
                "high_quality_count": high_quality,
                "high_quality_percentage": round(high_quality / len(tweets) * 100, 1) if tweets else 0
            }
        }

def main():
    """Main execution"""
    print("=== Miles Deutscher Live Tweet Fetcher ===\n")
    
    fetcher = MilesTweetFetcherLive()
    
    try:
        # Fetch tweets (Twitter API limit is 3200 most recent)
        print("Fetching tweets from @milesdeutscher...")
        print("Note: Twitter API limits to 3200 most recent tweets\n")
        
        tweets = fetcher.fetch_tweets(max_tweets=3200)
        
        if tweets:
            # Save the data
            fetcher.save_tweets(tweets)
            
            # Display summary
            stats = fetcher.calculate_statistics(tweets)
            print(f"\n[SUCCESS] Fetched {len(tweets)} tweets!")
            print(f"\nDate range: {stats['date_range']['earliest'][:10]} to {stats['date_range']['latest'][:10]}")
            print(f"Average likes: {stats['engagement']['avg_likes']}")
            print(f"Average retweets: {stats['engagement']['avg_retweets']}")
            print(f"High quality tweets: {stats['quality']['high_quality_count']} ({stats['quality']['high_quality_percentage']}%)")
            
            print("\nPattern distribution:")
            for pattern, count in sorted(stats['patterns'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {pattern}: {count}")
            
            print("\nFiles created:")
            print("- miles_tweets_live.json (structured data)")
            print("- miles_tweets_live.jsonl (line-delimited)")
            
        else:
            print("[ERROR] No tweets fetched")
            
    except Exception as e:
        print(f"[ERROR] Failed to fetch tweets: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()