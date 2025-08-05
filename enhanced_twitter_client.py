"""
Enhanced Twitter Client using python-twitter library
Combines tweepy with python-twitter for maximum functionality
"""

import os
from dotenv import load_dotenv
import pytwitter
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

class EnhancedTwitterClient:
    """
    Enhanced client using python-twitter (pytwitter) library
    Provides additional functionality and easier API access
    """
    
    def __init__(self):
        # Get credentials from environment
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Initialize python-twitter client
        self.client = pytwitter.Api(
            bearer_token=self.bearer_token,
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            application_only_auth=True
        )
        
        # Miles's info
        self.miles_username = "milesdeutscher"
        self._user_id = None
    
    def get_user_info(self) -> Dict:
        """Get detailed user information"""
        
        resp = self.client.get_user(username=self.miles_username)
        
        if resp.data:
            user = resp.data
            self._user_id = user.id
            
            return {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'description': user.description,
                'followers': user.public_metrics.followers_count,
                'following': user.public_metrics.following_count,
                'tweet_count': user.public_metrics.tweet_count,
                'created_at': user.created_at
            }
        
        return {}
    
    def get_timeline_tweets(self, max_results: int = 100) -> List[Dict]:
        """
        Get user timeline with enhanced data
        """
        
        if not self._user_id:
            self.get_user_info()
        
        # Get timeline
        resp = self.client.get_timelines(
            user_id=self._user_id,
            max_results=min(max_results, 100),
            tweet_fields=[
                "created_at", "public_metrics", "context_annotations",
                "entities", "referenced_tweets", "conversation_id",
                "possibly_sensitive", "reply_settings", "lang"
            ],
            exclude=["retweets", "replies"]
        )
        
        tweets = []
        
        if resp.data:
            for tweet in resp.data:
                processed = self._process_tweet(tweet)
                tweets.append(processed)
        
        return tweets
    
    def search_user_tweets(self, query: str = None, days_back: int = 7) -> List[Dict]:
        """
        Search Miles's tweets with specific criteria
        """
        
        # Build search query
        if query:
            search_query = f"from:{self.miles_username} {query}"
        else:
            search_query = f"from:{self.miles_username}"
        
        # Add time constraint
        start_time = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + "Z"
        
        resp = self.client.search_tweets(
            query=search_query,
            max_results=100,
            start_time=start_time,
            tweet_fields=["created_at", "public_metrics", "entities", "context_annotations"]
        )
        
        tweets = []
        
        if resp.data:
            for tweet in resp.data:
                processed = self._process_tweet(tweet)
                tweets.append(processed)
        
        return tweets
    
    def get_tweet_context(self, tweet_id: str) -> Dict:
        """
        Get full context of a tweet including conversation
        """
        
        # Get the tweet
        resp = self.client.get_tweet(
            tweet_id=tweet_id,
            tweet_fields=["created_at", "public_metrics", "conversation_id", "referenced_tweets"],
            expansions=["referenced_tweets.id", "author_id"]
        )
        
        if resp.data:
            return {
                'tweet': self._process_tweet(resp.data),
                'includes': resp.includes if hasattr(resp, 'includes') else {}
            }
        
        return {}
    
    def analyze_engagement_patterns(self, tweets: List[Dict]) -> Dict:
        """
        Analyze engagement patterns with enhanced metrics
        """
        
        if not tweets:
            return {}
        
        # Time-based analysis
        hour_engagement = {}
        day_engagement = {}
        
        # Content analysis
        with_media = []
        with_links = []
        with_questions = []
        
        for tweet in tweets:
            # Parse time
            created = datetime.fromisoformat(tweet['created_at'].replace('Z', '+00:00'))
            hour = created.hour
            day = created.strftime('%A')
            
            engagement = tweet['engagement_score']
            
            # Time tracking
            if hour not in hour_engagement:
                hour_engagement[hour] = []
            hour_engagement[hour].append(engagement)
            
            if day not in day_engagement:
                day_engagement[day] = []
            day_engagement[day].append(engagement)
            
            # Content tracking
            if tweet.get('has_media'):
                with_media.append(engagement)
            if tweet.get('has_links'):
                with_links.append(engagement)
            if '?' in tweet['text']:
                with_questions.append(engagement)
        
        # Calculate averages
        analysis = {
            'best_hours': self._get_top_times(hour_engagement),
            'best_days': self._get_top_times(day_engagement),
            'content_performance': {
                'with_media': sum(with_media) / len(with_media) if with_media else 0,
                'with_links': sum(with_links) / len(with_links) if with_links else 0,
                'with_questions': sum(with_questions) / len(with_questions) if with_questions else 0
            }
        }
        
        return analysis
    
    def _process_tweet(self, tweet) -> Dict:
        """Process raw tweet data into structured format"""
        
        # Extract metrics
        metrics = tweet.public_metrics
        total_engagement = (
            metrics.like_count + 
            metrics.retweet_count * 2 + 
            metrics.reply_count + 
            metrics.quote_count * 1.5
        )
        
        impressions = metrics.impression_count if hasattr(metrics, 'impression_count') else max(total_engagement * 20, 1)
        engagement_rate = total_engagement / impressions
        
        # Extract entities
        entities = tweet.entities if hasattr(tweet, 'entities') else {}
        
        return {
            'id': tweet.id,
            'text': tweet.text,
            'created_at': tweet.created_at,
            'metrics': {
                'likes': metrics.like_count,
                'retweets': metrics.retweet_count,
                'replies': metrics.reply_count,
                'quotes': metrics.quote_count
            },
            'engagement_score': engagement_rate,
            'total_engagement': total_engagement,
            'has_media': bool(entities.get('urls', [])),
            'has_links': bool(entities.get('urls', [])),
            'hashtags': [tag.tag for tag in entities.get('hashtags', [])],
            'mentions': [mention.username for mention in entities.get('mentions', [])]
        }
    
    def _get_top_times(self, time_engagement: Dict) -> List[tuple]:
        """Get top performing times"""
        
        avg_engagement = {}
        for time, engagements in time_engagement.items():
            avg_engagement[time] = sum(engagements) / len(engagements)
        
        # Sort by engagement
        sorted_times = sorted(avg_engagement.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_times[:3]  # Top 3

class MilesStyleExtractor:
    """
    Extract and analyze Miles's writing style using enhanced data
    """
    
    def __init__(self, client: EnhancedTwitterClient):
        self.client = client
    
    def extract_style_patterns(self, min_engagement: float = 0.05) -> Dict:
        """
        Extract comprehensive style patterns
        """
        
        # Get recent high-performing tweets
        tweets = self.client.get_timeline_tweets(max_results=100)
        
        # Filter by engagement
        high_performers = [t for t in tweets if t['engagement_score'] >= min_engagement]
        
        print(f"Analyzing {len(high_performers)} high-performing tweets...")
        
        patterns = {
            'openings': {},
            'structures': {},
            'closings': {},
            'phrases': [],
            'avg_metrics': {}
        }
        
        for tweet in high_performers:
            text = tweet['text']
            lines = text.split('\n')
            
            # Analyze opening
            opening = self._get_opening_pattern(text)
            patterns['openings'][opening] = patterns['openings'].get(opening, 0) + 1
            
            # Analyze structure
            structure = f"{len(lines)}_part"
            patterns['structures'][structure] = patterns['structures'].get(structure, 0) + 1
            
            # Extract key phrases
            phrases = self._extract_key_phrases(text)
            patterns['phrases'].extend(phrases)
        
        # Calculate averages
        if high_performers:
            patterns['avg_metrics'] = {
                'length': sum(len(t['text']) for t in high_performers) / len(high_performers),
                'engagement': sum(t['engagement_score'] for t in high_performers) / len(high_performers),
                'lines': sum(len(t['text'].split('\n')) for t in high_performers) / len(high_performers)
            }
        
        # Get engagement patterns
        patterns['engagement_analysis'] = self.client.analyze_engagement_patterns(high_performers)
        
        return patterns
    
    def _get_opening_pattern(self, text: str) -> str:
        """Identify opening pattern"""
        
        text = text.strip()
        
        # Check for specific openings
        if text.startswith(('Anon,', 'Ser,', 'Chat,')):
            return 'direct_address'
        elif text.startswith(('Real talk:', 'Unpopular opinion:', 'Look,')):
            return 'statement_intro'
        elif text.startswith('$'):
            return 'ticker_start'
        elif text.startswith('http'):
            return 'link_first'
        elif text[0].isupper() and '?' in text.split('\n')[0]:
            return 'question'
        else:
            return 'standard'
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract Miles's signature phrases"""
        
        key_phrases = [
            'just noise', 'what matters', 'until then', 'few understand',
            'based', 'ngmi', 'wagmi', 'up only', 'down bad',
            'math ain\'t mathing', 'that\'s the tweet', 'but I said what I said'
        ]
        
        found = []
        text_lower = text.lower()
        
        for phrase in key_phrases:
            if phrase in text_lower:
                found.append(phrase)
        
        return found

# Example usage
if __name__ == "__main__":
    print("🐦 Enhanced Twitter Client for Miles Deutscher AI")
    print("="*60)
    
    # Initialize enhanced client
    client = EnhancedTwitterClient()
    
    # Get user info
    print("\n📊 Fetching user information...")
    user_info = client.get_user_info()
    
    if user_info:
        print(f"✅ Connected to @{user_info['username']}")
        print(f"   Followers: {user_info['followers']:,}")
        print(f"   Total Tweets: {user_info['tweet_count']:,}")
    
    # Extract style patterns
    print("\n🎨 Extracting style patterns...")
    extractor = MilesStyleExtractor(client)
    patterns = extractor.extract_style_patterns()
    
    print("\n📈 Style Analysis Results:")
    print(f"   Average tweet length: {patterns['avg_metrics']['length']:.0f} chars")
    print(f"   Average engagement: {patterns['avg_metrics']['engagement']:.2%}")
    print(f"   Most common structure: {max(patterns['structures'], key=patterns['structures'].get)}")
    
    print("\n✅ Enhanced client ready for use!")