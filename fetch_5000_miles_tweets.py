"""
Fetch 5000 latest tweets from Miles Deutscher via X API v2
Structures data perfectly for final data model
"""
import tweepy
import json
import time
from datetime import datetime
import os
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
        # Get credentials from environment or use provided ones
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN', 'AAAAAAAAAAAAAAAAAAAAAEjxuAEAAAAA0e0MZ3z5kqjQz34A5JVAp8lVNyA%3DibqZVQYAz7LrYxQ6IqjSOSzjOwsHyjqQEHgVyGiCqtqiXrClxA')
        
        # Initialize client
        self.client = tweepy.Client(bearer_token=self.bearer_token, wait_on_rate_limit=True)
        
        # Miles Deutscher's Twitter username
        self.username = "milesdeutscher"
        self.user_id = None
        
    def get_user_id(self) -> str:
        """Get Miles Deutscher's user ID"""
        try:
            user = self.client.get_user(username=self.username)
            self.user_id = user.data.id
            logging.info(f"Found user {self.username} with ID: {self.user_id}")
            return self.user_id
        except Exception as e:
            logging.error(f"Error getting user ID: {e}")
            raise
    
    def fetch_5000_tweets(self) -> List[Dict]:
        """Fetch up to 5000 recent tweets from Miles"""
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
            'reply_settings', 'source'
        ]
        
        # User fields
        user_fields = ['id', 'name', 'username', 'description', 'public_metrics']
        
        # Media fields
        media_fields = ['media_key', 'type', 'url', 'alt_text']
        
        # Expansions
        expansions = ['author_id', 'referenced_tweets.id', 'attachments.media_keys']
        
        logging.info("Starting to fetch tweets...")
        
        while total_fetched < 5000:
            try:
                # Calculate how many tweets to fetch in this request
                remaining = 5000 - total_fetched
                max_results = min(100, remaining)  # API max is 100 per request
                
                # Fetch tweets
                tweets = self.client.get_users_tweets(
                    id=self.user_id,
                    max_results=max_results,
                    tweet_fields=tweet_fields,
                    user_fields=user_fields,
                    media_fields=media_fields,
                    expansions=expansions,
                    pagination_token=next_token,
                    exclude=['retweets']  # Exclude pure retweets
                )
                
                if not tweets.data:
                    logging.info("No more tweets available")
                    break
                
                # Process each tweet
                for tweet in tweets.data:
                    tweet_data = self.process_tweet(tweet, tweets.includes)
                    all_tweets.append(tweet_data)
                
                total_fetched += len(tweets.data)
                logging.info(f"Fetched {total_fetched} tweets so far...")
                
                # Get next page token
                if 'next_token' in tweets.meta:
                    next_token = tweets.meta['next_token']
                else:
                    logging.info("No more pages available")
                    break
                
                # Brief pause to be respectful to API
                time.sleep(0.5)
                
            except Exception as e:
                logging.error(f"Error fetching tweets: {e}")
                if "429" in str(e):  # Rate limit
                    logging.info("Rate limit hit, waiting 15 minutes...")
                    time.sleep(900)  # Wait 15 minutes
                    continue
                else:
                    break
        
        logging.info(f"Successfully fetched {len(all_tweets)} tweets")
        return all_tweets
    
    def process_tweet(self, tweet, includes) -> Dict:
        """Process a single tweet into structured format"""
        # Extract text and clean it
        text = tweet.text
        
        # Determine tweet type and structure
        tweet_type = self.classify_tweet_type(tweet)
        pattern = self.detect_pattern(text)
        
        # Build structured data
        structured_tweet = {
            # Core identifiers
            "id": tweet.id,
            "created_at": tweet.created_at.isoformat() if hasattr(tweet.created_at, 'isoformat') else str(tweet.created_at),
            
            # Content
            "text": text,
            "clean_text": self.clean_text(text),
            
            # Metadata
            "type": tweet_type,
            "pattern": pattern,
            "word_count": len(text.split()),
            "char_count": len(text),
            
            # Engagement metrics
            "metrics": {
                "likes": tweet.public_metrics.get('like_count', 0),
                "retweets": tweet.public_metrics.get('retweet_count', 0),
                "replies": tweet.public_metrics.get('reply_count', 0),
                "quotes": tweet.public_metrics.get('quote_count', 0),
                "impressions": tweet.public_metrics.get('impression_count', 0) if 'impression_count' in tweet.public_metrics else None
            },
            
            # Calculated metrics
            "engagement_rate": self.calculate_engagement_rate(tweet.public_metrics),
            "virality_score": self.calculate_virality_score(tweet.public_metrics),
            
            # Content analysis
            "entities": {
                "hashtags": [tag['tag'] for tag in tweet.entities.get('hashtags', [])] if tweet.entities else [],
                "mentions": [mention['username'] for mention in tweet.entities.get('mentions', [])] if tweet.entities else [],
                "urls": [url['expanded_url'] for url in tweet.entities.get('urls', [])] if tweet.entities else [],
                "cashtags": [tag['tag'] for tag in tweet.entities.get('cashtags', [])] if tweet.entities else []
            },
            
            # Context
            "is_reply": tweet.in_reply_to_user_id is not None,
            "is_thread": tweet.conversation_id == tweet.id,
            "has_media": bool(tweet.attachments.get('media_keys', [])) if tweet.attachments else False,
            
            # Additional metadata
            "source": tweet.source,
            "language": tweet.lang,
            "possibly_sensitive": tweet.possibly_sensitive if hasattr(tweet, 'possibly_sensitive') else False,
            
            # For AI training
            "quality_score": self.calculate_quality_score(tweet, text),
            "topic_categories": self.categorize_topics(text),
            "sentiment": self.analyze_sentiment(text),
            "key_phrases": self.extract_key_phrases(text)
        }
        
        return structured_tweet
    
    def classify_tweet_type(self, tweet) -> str:
        """Classify the type of tweet"""
        text = tweet.text.lower()
        
        if tweet.in_reply_to_user_id:
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
            # Check for classic 3-part structure
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
        # Remove URLs but keep the text
        import re
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r't\.co/\S+', '', text)
        
        # Clean extra whitespace
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
        
        impressions = metrics.get('impression_count', 1)
        if impressions and impressions > 0:
            return round(total_engagement / impressions, 4)
        
        # Fallback: normalize by assuming 10k average impressions
        return round(total_engagement / 10000, 4)
    
    def calculate_virality_score(self, metrics: Dict) -> float:
        """Calculate virality score (0-1)"""
        # Weighted score based on different engagement types
        score = (
            metrics.get('like_count', 0) * 1 +
            metrics.get('retweet_count', 0) * 3 +
            metrics.get('reply_count', 0) * 2 +
            metrics.get('quote_count', 0) * 4
        )
        
        # Normalize (assuming 10k engagement is viral)
        return min(1.0, round(score / 10000, 4))
    
    def calculate_quality_score(self, tweet, text: str) -> float:
        """Calculate quality score for training"""
        score = 0.5  # Base score
        
        # Engagement boost
        if tweet.public_metrics['like_count'] > 100:
            score += 0.1
        if tweet.public_metrics['retweet_count'] > 50:
            score += 0.1
        
        # Length preference (not too short, not too long)
        word_count = len(text.split())
        if 20 <= word_count <= 100:
            score += 0.1
        
        # Pattern bonus
        if any(pattern in self.detect_pattern(text) for pattern in ['3_part', '5_part', '7_part']):
            score += 0.1
        
        # No links bonus (original thoughts)
        if 'http' not in text:
            score += 0.1
        
        return min(1.0, round(score, 2))
    
    def categorize_topics(self, text: str) -> List[str]:
        """Categorize tweet topics"""
        text_lower = text.lower()
        categories = []
        
        # Crypto/Trading topics
        if any(term in text_lower for term in ['btc', 'bitcoin', 'eth', 'ethereum']):
            categories.append('crypto_analysis')
        if any(term in text_lower for term in ['alt', 'altcoin', 'alts']):
            categories.append('altcoins')
        if any(term in text_lower for term in ['trade', 'trading', 'position', 'entry', 'exit']):
            categories.append('trading')
        if any(term in text_lower for term in ['bull', 'bear', 'market', 'trend']):
            categories.append('market_analysis')
        
        # Philosophy/Mindset
        if any(term in text_lower for term in ['think', 'believe', 'mindset', 'psychology']):
            categories.append('philosophy')
        if any(term in text_lower for term in ['success', 'fail', 'win', 'lose']):
            categories.append('mindset')
        
        # DeFi/Tech
        if any(term in text_lower for term in ['defi', 'yield', 'farm', 'stake']):
            categories.append('defi')
        if any(term in text_lower for term in ['nft', 'jpeg', 'opensea']):
            categories.append('nft')
        
        return categories if categories else ['general']
    
    def analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        text_lower = text.lower()
        
        # Bearish indicators
        bearish_words = ['crash', 'dump', 'bear', 'down', 'sell', 'fear', 'panic', 'bottom']
        # Bullish indicators
        bullish_words = ['moon', 'pump', 'bull', 'up', 'buy', 'greed', 'fomo', 'top']
        
        bearish_count = sum(1 for word in bearish_words if word in text_lower)
        bullish_count = sum(1 for word in bullish_words if word in text_lower)
        
        if bearish_count > bullish_count:
            return "bearish"
        elif bullish_count > bearish_count:
            return "bullish"
        else:
            return "neutral"
    
    def extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases for training"""
        # Simple extraction of important phrases
        phrases = []
        
        # Look for quoted text
        import re
        quotes = re.findall(r'"([^"]*)"', text)
        phrases.extend(quotes)
        
        # Look for emphasis patterns
        emphasis = re.findall(r'\b[A-Z]{2,}\b', text)
        phrases.extend(emphasis)
        
        # Common Miles patterns
        if "Few understand" in text:
            phrases.append("Few understand")
        if "Most people" in text:
            phrases.append("Most people")
        if "The real" in text:
            phrases.append("The real")
        
        return list(set(phrases))[:5]  # Max 5 phrases
    
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
        
        # Also save as JSONL for easier processing
        jsonl_filename = filename.replace('.json', '.jsonl')
        with open(jsonl_filename, 'w', encoding='utf-8') as f:
            for tweet in tweets:
                f.write(json.dumps(tweet, ensure_ascii=False) + '\n')
        
        logging.info(f"Also saved as JSONL: {jsonl_filename}")
    
    def calculate_statistics(self, tweets: List[Dict]) -> Dict:
        """Calculate comprehensive statistics"""
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
        
        # Topic distribution
        topic_counts = {}
        for tweet in tweets:
            for topic in tweet['topic_categories']:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Type distribution
        type_counts = {}
        for tweet in tweets:
            tweet_type = tweet['type']
            type_counts[tweet_type] = type_counts.get(tweet_type, 0) + 1
        
        # Quality distribution
        quality_scores = [t['quality_score'] for t in tweets]
        
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
            "types": type_counts,
            "quality": {
                "average": round(sum(quality_scores) / len(quality_scores), 3),
                "min": min(quality_scores),
                "max": max(quality_scores),
                "high_quality_count": sum(1 for s in quality_scores if s >= 0.7)
            },
            "content": {
                "avg_word_count": round(sum(t['word_count'] for t in tweets) / len(tweets), 1),
                "avg_char_count": round(sum(t['char_count'] for t in tweets) / len(tweets), 1),
                "with_media": sum(1 for t in tweets if t['has_media']),
                "with_links": sum(1 for t in tweets if t['entities']['urls'])
            }
        }

def main():
    """Main execution"""
    print("=== Miles Deutscher 5000 Tweet Fetcher ===\n")
    
    fetcher = MilesTweetFetcher5000()
    
    try:
        # Fetch tweets
        print("Fetching up to 5000 tweets from @milesdeutscher...")
        tweets = fetcher.fetch_5000_tweets()
        
        if tweets:
            # Save structured data
            fetcher.save_structured_data(tweets)
            
            print(f"\n[SUCCESS] Fetched and structured {len(tweets)} tweets!")
            print("\nFiles created:")
            print("- miles_5000_tweets_structured.json (full structured data)")
            print("- miles_5000_tweets_structured.jsonl (line-delimited format)")
            
            # Show sample statistics
            stats = fetcher.calculate_statistics(tweets)
            print("\nQuick Statistics:")
            print(f"- Date range: {stats['date_range']['earliest'][:10]} to {stats['date_range']['latest'][:10]}")
            print(f"- Average likes: {stats['engagement']['avg_likes']}")
            print(f"- Average retweets: {stats['engagement']['avg_retweets']}")
            print(f"- High quality tweets: {stats['quality']['high_quality_count']}")
            
        else:
            print("[ERROR] No tweets fetched")
            
    except Exception as e:
        print(f"[ERROR] Failed to fetch tweets: {e}")
        logging.error(f"Full error: {e}", exc_info=True)

if __name__ == "__main__":
    main()