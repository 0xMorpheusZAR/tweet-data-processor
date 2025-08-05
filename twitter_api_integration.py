"""
X/Twitter API Integration for Miles Deutscher AI
Real-time data collection and style learning
"""

import os
import json
import tweepy
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional
import time

class TwitterAPIClient:
    """
    Handles X/Twitter API v2 integration for enhanced data collection
    """
    
    def __init__(self, bearer_token: Optional[str] = None):
        """Initialize Twitter API client"""
        
        # Use environment variable if token not provided
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        
        if not self.bearer_token:
            raise ValueError("Twitter Bearer Token required. Set TWITTER_BEARER_TOKEN environment variable.")
        
        # Initialize client
        self.client = tweepy.Client(bearer_token=self.bearer_token)
        
        # Miles's Twitter handle
        self.miles_username = "milesdeutscher"
        self.miles_user_id = None
        
    def get_user_id(self) -> str:
        """Get Miles's Twitter user ID"""
        
        if not self.miles_user_id:
            user = self.client.get_user(username=self.miles_username)
            self.miles_user_id = user.data.id
            
        return self.miles_user_id
    
    def fetch_recent_tweets(self, max_results: int = 100) -> List[Dict]:
        """
        Fetch Miles's most recent tweets
        
        Args:
            max_results: Number of tweets to fetch (max 100)
            
        Returns:
            List of tweet dictionaries with enhanced data
        """
        
        user_id = self.get_user_id()
        
        # Fetch tweets with all available fields
        tweets = self.client.get_users_tweets(
            id=user_id,
            max_results=max_results,
            tweet_fields=[
                'created_at', 'public_metrics', 'referenced_tweets',
                'conversation_id', 'in_reply_to_user_id', 'entities',
                'context_annotations', 'possibly_sensitive', 'lang'
            ],
            exclude=['retweets', 'replies']  # Focus on original content
        )
        
        if not tweets.data:
            return []
        
        # Process tweets into structured format
        processed_tweets = []
        
        for tweet in tweets.data:
            processed = {
                'id': tweet.id,
                'text': tweet.text,
                'created_at': tweet.created_at.isoformat(),
                'metrics': {
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                    'replies': tweet.public_metrics['reply_count'],
                    'quotes': tweet.public_metrics['quote_count'],
                    'impressions': tweet.public_metrics.get('impression_count', 0)
                },
                'engagement_rate': self._calculate_engagement_rate(tweet.public_metrics),
                'has_media': bool(tweet.entities.get('urls', [])),
                'hashtags': [tag['tag'] for tag in tweet.entities.get('hashtags', [])],
                'mentions': [mention['username'] for mention in tweet.entities.get('mentions', [])],
                'style_features': self._extract_style_features(tweet.text)
            }
            
            processed_tweets.append(processed)
        
        return processed_tweets
    
    def fetch_high_engagement_tweets(self, days: int = 30, min_engagement_rate: float = 0.05) -> List[Dict]:
        """
        Fetch Miles's highest performing tweets for style learning
        
        Args:
            days: Number of days to look back
            min_engagement_rate: Minimum engagement rate threshold
            
        Returns:
            High-performing tweets sorted by engagement
        """
        
        user_id = self.get_user_id()
        start_time = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        
        # Fetch tweets with pagination
        all_tweets = []
        pagination_token = None
        
        while len(all_tweets) < 500:  # Limit total tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=100,
                start_time=start_time,
                pagination_token=pagination_token,
                tweet_fields=['created_at', 'public_metrics', 'entities'],
                exclude=['retweets', 'replies']
            )
            
            if not tweets.data:
                break
                
            all_tweets.extend(tweets.data)
            
            # Check for next page
            if hasattr(tweets, 'meta') and tweets.meta.get('next_token'):
                pagination_token = tweets.meta['next_token']
            else:
                break
        
        # Process and filter high-engagement tweets
        high_performers = []
        
        for tweet in all_tweets:
            engagement_rate = self._calculate_engagement_rate(tweet.public_metrics)
            
            if engagement_rate >= min_engagement_rate:
                processed = {
                    'text': tweet.text,
                    'engagement_rate': engagement_rate,
                    'total_engagement': sum([
                        tweet.public_metrics['like_count'],
                        tweet.public_metrics['retweet_count'] * 2,  # Weight retweets
                        tweet.public_metrics['reply_count'],
                        tweet.public_metrics['quote_count'] * 1.5  # Weight quotes
                    ]),
                    'created_at': tweet.created_at.isoformat(),
                    'style_features': self._extract_style_features(tweet.text)
                }
                high_performers.append(processed)
        
        # Sort by engagement
        high_performers.sort(key=lambda x: x['total_engagement'], reverse=True)
        
        return high_performers
    
    def _calculate_engagement_rate(self, metrics: Dict) -> float:
        """Calculate engagement rate from public metrics"""
        
        impressions = metrics.get('impression_count', 1)  # Avoid division by zero
        if impressions == 0:
            impressions = 1
            
        engagements = (
            metrics['like_count'] +
            metrics['retweet_count'] * 2 +
            metrics['reply_count'] +
            metrics['quote_count'] * 1.5
        )
        
        return engagements / impressions if impressions > 0 else 0
    
    def _extract_style_features(self, text: str) -> Dict:
        """Extract style features from tweet text"""
        
        lines = text.split('\n')
        
        return {
            'length': len(text),
            'line_count': len(lines),
            'has_question': '?' in text,
            'has_ticker': '$' in text,
            'starts_with_link': text.strip().startswith('http'),
            'ends_with_link': text.strip().endswith(('.com', '.co', '.xyz', '.io')),
            'has_numbers': any(char.isdigit() for char in text),
            'structure': self._identify_structure(lines),
            'opening_style': self._identify_opening(text),
            'uses_miles_phrases': self._check_miles_phrases(text)
        }
    
    def _identify_structure(self, lines: List[str]) -> str:
        """Identify tweet structure pattern"""
        
        if len(lines) == 1:
            return "single_line"
        elif len(lines) == 3:
            return "three_part"
        elif len(lines) == 2:
            return "two_part"
        else:
            return "multi_line"
    
    def _identify_opening(self, text: str) -> str:
        """Identify opening style"""
        
        openings = {
            'direct_address': ['Anon,', 'Ser,', 'GM', 'Chat,'],
            'statement': ['Real talk:', 'Unpopular opinion:', 'Look,'],
            'question': text.strip().startswith(('Is', 'Are', 'What', 'Why', 'How')),
            'ticker': text.strip().startswith('$')
        }
        
        for style, patterns in openings.items():
            if style == 'question':
                if patterns:  # It's a boolean
                    return 'question'
            else:
                for pattern in patterns:
                    if text.strip().startswith(pattern):
                        return style
        
        return 'standard'
    
    def _check_miles_phrases(self, text: str) -> List[str]:
        """Check for signature Miles phrases"""
        
        phrases = [
            'few understand', 'based', 'ngmi', 'wagmi', 'up only',
            'down bad', 'ser', 'anon', 'math ain\'t mathing',
            'that\'s it. that\'s the tweet', 'but I said what I said'
        ]
        
        found = []
        text_lower = text.lower()
        
        for phrase in phrases:
            if phrase in text_lower:
                found.append(phrase)
        
        return found

class TwitterDataEnhancer:
    """
    Enhances training data with real-time Twitter data
    """
    
    def __init__(self, api_client: TwitterAPIClient):
        self.api = api_client
        
    def update_training_data(self, existing_data_path: str = 'data.jsonl') -> str:
        """
        Update training data with fresh tweets from API
        
        Returns:
            Path to enhanced dataset
        """
        
        print("Fetching recent high-engagement tweets...")
        
        # Fetch high performers from last 30 days
        high_performers = self.api.fetch_high_engagement_tweets(days=30)
        
        print(f"Found {len(high_performers)} high-engagement tweets")
        
        # Load existing data
        existing_tweets = []
        if os.path.exists(existing_data_path):
            with open(existing_data_path, 'r', encoding='utf-8') as f:
                for line in f:
                    existing_tweets.append(json.loads(line))
        
        # Add new tweets to training data
        new_entries = 0
        
        for tweet in high_performers:
            # Check if tweet already exists
            if not any(tweet['text'] in entry.get('completion', '') for entry in existing_tweets):
                # Create training entry
                entry = {
                    "prompt": f"Write a tweet in the style of Miles Deutscher. Here are some examples:\n\n{self._get_examples()}\n\nNow write a new tweet:",
                    "completion": f" {tweet['text']}",
                    "metadata": {
                        "engagement_rate": tweet['engagement_rate'],
                        "style_features": tweet['style_features'],
                        "source": "twitter_api",
                        "collected_at": datetime.utcnow().isoformat()
                    }
                }
                
                existing_tweets.append(entry)
                new_entries += 1
        
        # Save enhanced dataset
        enhanced_path = 'data_enhanced.jsonl'
        
        with open(enhanced_path, 'w', encoding='utf-8') as f:
            for entry in existing_tweets:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        print(f"Added {new_entries} new tweets to training data")
        print(f"Total training examples: {len(existing_tweets)}")
        print(f"Enhanced dataset saved to: {enhanced_path}")
        
        return enhanced_path
    
    def _get_examples(self) -> str:
        """Get example tweets for prompt"""
        
        examples = [
            "The overhang is just noise.\n\nWhat matters: macro liquidity meeting a narrative so powerful it makes bagholders capitulate.\n\nUntil then? We're all just trading chop.",
            "Real talk: Your bags aren't pumping because we need BOTH macro tailwind AND a fresh narrative.\n\nOne without the other = underwhelming pumps and cope posting.\n\nMath ain't mathing without both.",
            "Everyone's waiting for alt season like it's Christmas morning.\n\nNews flash: Santa needs two things - macro liquidity and a narrative bigger than your bags.\n\nNo gifts without both."
        ]
        
        return "\n\n".join(examples)
    
    def analyze_style_evolution(self) -> Dict:
        """
        Analyze how Miles's style has evolved over time
        """
        
        print("Analyzing style evolution...")
        
        # Fetch tweets from different time periods
        recent_tweets = self.api.fetch_recent_tweets(max_results=100)
        
        # Analyze patterns
        analysis = {
            'current_trends': self._analyze_current_trends(recent_tweets),
            'popular_structures': self._analyze_structures(recent_tweets),
            'engagement_patterns': self._analyze_engagement_patterns(recent_tweets),
            'vocabulary_shifts': self._analyze_vocabulary(recent_tweets)
        }
        
        return analysis
    
    def _analyze_current_trends(self, tweets: List[Dict]) -> Dict:
        """Analyze current trending patterns"""
        
        trends = {
            'avg_length': sum(t['style_features']['length'] for t in tweets) / len(tweets),
            'question_ratio': sum(1 for t in tweets if t['style_features']['has_question']) / len(tweets),
            'ticker_ratio': sum(1 for t in tweets if t['style_features']['has_ticker']) / len(tweets),
            'link_placement': {
                'start': sum(1 for t in tweets if t['style_features']['starts_with_link']) / len(tweets),
                'end': sum(1 for t in tweets if t['style_features']['ends_with_link']) / len(tweets)
            }
        }
        
        return trends
    
    def _analyze_structures(self, tweets: List[Dict]) -> Dict:
        """Analyze tweet structures"""
        
        structures = {}
        for tweet in tweets:
            structure = tweet['style_features']['structure']
            structures[structure] = structures.get(structure, 0) + 1
        
        # Convert to percentages
        total = len(tweets)
        return {k: (v/total)*100 for k, v in structures.items()}
    
    def _analyze_engagement_patterns(self, tweets: List[Dict]) -> Dict:
        """Analyze what drives engagement"""
        
        high_engagement = [t for t in tweets if t['engagement_rate'] > 0.05]
        
        patterns = {
            'high_engagement_structures': {},
            'high_engagement_features': {
                'avg_length': 0,
                'has_question': 0,
                'has_ticker': 0
            }
        }
        
        if high_engagement:
            # Structure analysis
            for tweet in high_engagement:
                structure = tweet['style_features']['structure']
                patterns['high_engagement_structures'][structure] = \
                    patterns['high_engagement_structures'].get(structure, 0) + 1
            
            # Feature analysis
            patterns['high_engagement_features']['avg_length'] = \
                sum(t['style_features']['length'] for t in high_engagement) / len(high_engagement)
            patterns['high_engagement_features']['has_question'] = \
                sum(1 for t in high_engagement if t['style_features']['has_question']) / len(high_engagement)
            patterns['high_engagement_features']['has_ticker'] = \
                sum(1 for t in high_engagement if t['style_features']['has_ticker']) / len(high_engagement)
        
        return patterns
    
    def _analyze_vocabulary(self, tweets: List[Dict]) -> Dict:
        """Analyze vocabulary usage"""
        
        all_phrases = []
        for tweet in tweets:
            all_phrases.extend(tweet['style_features'].get('uses_miles_phrases', []))
        
        # Count phrase frequency
        phrase_counts = {}
        for phrase in all_phrases:
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        
        # Sort by frequency
        sorted_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'top_phrases': sorted_phrases[:10],
            'total_unique_phrases': len(set(all_phrases))
        }

# Usage example
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║        X/Twitter API Integration Setup               ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    print("\nTo use this integration:")
    print("1. Get your Twitter API Bearer Token from developer.twitter.com")
    print("2. Set environment variable: TWITTER_BEARER_TOKEN=your_token_here")
    print("3. Run the data enhancement:")
    print("\n   python twitter_api_integration.py")
    
    # Example usage (commented out - requires API token)
    """
    # Initialize API client
    api = TwitterAPIClient()
    
    # Create data enhancer
    enhancer = TwitterDataEnhancer(api)
    
    # Update training data with fresh tweets
    enhanced_dataset = enhancer.update_training_data()
    
    # Analyze style evolution
    style_analysis = enhancer.analyze_style_evolution()
    
    print("\nStyle Analysis Results:")
    print(json.dumps(style_analysis, indent=2))
    """