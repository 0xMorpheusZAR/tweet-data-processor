"""
Miles Deutscher 1000 Tweets Fetcher & Advanced Training System
Fetches last 1000 tweets with deep analysis and model improvement
"""

import os
import json
import time
import urllib.request
import urllib.parse
import ssl
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict
import re
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('miles_1000_tweets.log'),
        logging.StreamHandler()
    ]
)

class Advanced1000TweetsFetcher:
    """Fetch and analyze 1000 tweets from Miles Deutscher"""
    
    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN', 
            'AAAAAAAAAAAAAAAAAAAAAJi13QEAAAAAghVwuLws1YdchbwCAkUjqqwu6oc%3DeImrILD6DNOvuOdZiH42oFM3Ww7zTLYaiz1onypLp8XNzCskQ7')
        
        self.all_tweets = []
        self.analyzed_data = {
            'patterns': defaultdict(int),
            'vocabulary': Counter(),
            'structures': defaultdict(int),
            'time_patterns': defaultdict(list),
            'engagement_patterns': defaultdict(list),
            'high_performers': [],
            'topics': defaultdict(int)
        }
        
    def fetch_1000_tweets(self) -> List:
        """Fetch up to 1000 recent tweets from Miles"""
        logging.info("Starting fetch of 1000 tweets from @milesdeutscher...")
        
        # Get user ID first
        try:
            url = "https://api.twitter.com/2/users/by/username/milesdeutscher"
            req = urllib.request.Request(url)
            req.add_header('Authorization', f'Bearer {self.bearer_token}')
            
            context = ssl.create_default_context()
            with urllib.request.urlopen(req, context=context) as response:
                user_data = json.loads(response.read().decode())
            
            if 'data' not in user_data:
                logging.error("Could not fetch user data")
                return []
            
            user_id = user_data['data']['id']
            logging.info(f"Found user ID: {user_id}")
            
        except Exception as e:
            logging.error(f"Error fetching user ID: {e}")
            return []
        
        # Fetch tweets in batches (Twitter API allows max 100 per request)
        next_token = None
        total_fetched = 0
        
        while total_fetched < 1000:
            try:
                # Build request URL
                tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
                params = {
                    'max_results': 100,  # Maximum allowed
                    'tweet.fields': 'created_at,public_metrics,context_annotations,entities,referenced_tweets',
                    'exclude': 'retweets'
                }
                
                if next_token:
                    params['pagination_token'] = next_token
                
                tweets_url += '?' + urllib.parse.urlencode(params)
                
                # Make request
                req = urllib.request.Request(tweets_url)
                req.add_header('Authorization', f'Bearer {self.bearer_token}')
                
                logging.info(f"Fetching batch... (current total: {total_fetched})")
                
                with urllib.request.urlopen(req, context=context) as response:
                    response_data = json.loads(response.read().decode())
                
                if 'data' in response_data:
                    tweets = response_data['data']
                    self.all_tweets.extend(tweets)
                    total_fetched += len(tweets)
                    
                    logging.info(f"Fetched {len(tweets)} tweets. Total: {total_fetched}")
                    
                    # Check for next page
                    if 'meta' in response_data and 'next_token' in response_data['meta']:
                        next_token = response_data['meta']['next_token']
                    else:
                        break  # No more tweets
                    
                    # Rate limit protection
                    time.sleep(1)
                else:
                    break
                    
            except Exception as e:
                logging.error(f"Error fetching tweets batch: {e}")
                break
        
        logging.info(f"Successfully fetched {len(self.all_tweets)} tweets total")
        return self.all_tweets
    
    def deep_analyze_tweets(self):
        """Perform deep analysis on all fetched tweets"""
        logging.info("Performing deep analysis on fetched tweets...")
        
        for tweet in self.all_tweets:
            self._analyze_single_tweet(tweet)
        
        # Post-process analysis
        self._identify_top_patterns()
        self._calculate_optimal_parameters()
        self._generate_insights()
        
    def _analyze_single_tweet(self, tweet: Dict):
        """Analyze individual tweet in detail"""
        text = tweet.get('text', '')
        metrics = tweet.get('public_metrics', {})
        created_at = tweet.get('created_at', '')
        
        # Structure analysis
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        structure = f"{len(lines)}_part"
        self.analyzed_data['structures'][structure] += 1
        
        # Three-part canonical structure detection
        if len(lines) == 3:
            # Check if it follows dismiss → focus → reality pattern
            if any(word in lines[0].lower() for word in ['noise', 'everyone', 'the', 'your']):
                if any(word in lines[1].lower() for word in ['what matters', 'real', 'truth', 'focus']):
                    self.analyzed_data['patterns']['canonical_3_part'] += 1
        
        # Vocabulary extraction
        words = re.findall(r'\b\w+\b', text.lower())
        self.analyzed_data['vocabulary'].update(words)
        
        # Topic detection
        topics = self._detect_topics(text)
        for topic in topics:
            self.analyzed_data['topics'][topic] += 1
        
        # Engagement analysis
        engagement_score = self._calculate_engagement(metrics)
        
        if engagement_score > 500:  # High engagement threshold
            self.analyzed_data['high_performers'].append({
                'text': text,
                'engagement': engagement_score,
                'structure': structure,
                'metrics': metrics,
                'topics': topics
            })
        
        # Time pattern analysis
        if created_at:
            hour = datetime.fromisoformat(created_at.replace('Z', '+00:00')).hour
            self.analyzed_data['time_patterns'][hour].append(engagement_score)
        
        # Engagement by structure
        self.analyzed_data['engagement_patterns'][structure].append(engagement_score)
    
    def _detect_topics(self, text: str) -> List[str]:
        """Detect topics in tweet"""
        topics = []
        text_lower = text.lower()
        
        topic_keywords = {
            'macro': ['macro', 'liquidity', 'fed', 'monetary', 'gdp'],
            'bitcoin': ['bitcoin', 'btc', 'halving', 'satoshi'],
            'altcoins': ['alt', 'altcoin', 'eth', 'sol', 'avax'],
            'trading': ['trade', 'trading', 'position', 'chart', 'ta'],
            'market_sentiment': ['bull', 'bear', 'pump', 'dump', 'moon'],
            'philosophy': ['noise', 'matters', 'truth', 'reality', 'few'],
            'defi': ['defi', 'yield', 'protocol', 'tvl', 'liquidity'],
            'nft': ['nft', 'jpeg', 'opensea', 'collection']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _calculate_engagement(self, metrics: Dict) -> float:
        """Calculate weighted engagement score"""
        return (
            metrics.get('like_count', 0) * 1 +
            metrics.get('retweet_count', 0) * 2 +
            metrics.get('reply_count', 0) * 1.5 +
            metrics.get('quote_count', 0) * 2.5
        )
    
    def _identify_top_patterns(self):
        """Identify most successful patterns"""
        logging.info("\nTop Patterns Identified:")
        
        # Most common structures
        top_structures = sorted(self.analyzed_data['structures'].items(), 
                              key=lambda x: x[1], reverse=True)[:5]
        
        logging.info("Most Common Structures:")
        for structure, count in top_structures:
            avg_engagement = sum(self.analyzed_data['engagement_patterns'][structure]) / len(self.analyzed_data['engagement_patterns'][structure])
            logging.info(f"  - {structure}: {count} tweets, avg engagement: {avg_engagement:.1f}")
        
        # Top vocabulary
        top_words = self.analyzed_data['vocabulary'].most_common(50)
        key_vocabulary = [word for word, count in top_words if len(word) > 3 and count > 5]
        logging.info(f"\nKey Vocabulary: {', '.join(key_vocabulary[:20])}")
        
        # Best performing topics
        topic_engagement = {}
        for tweet in self.analyzed_data['high_performers']:
            for topic in tweet['topics']:
                if topic not in topic_engagement:
                    topic_engagement[topic] = []
                topic_engagement[topic].append(tweet['engagement'])
        
        logging.info("\nHigh-Engagement Topics:")
        for topic, engagements in sorted(topic_engagement.items(), 
                                       key=lambda x: sum(x[1])/len(x[1]), reverse=True):
            avg_engagement = sum(engagements) / len(engagements)
            logging.info(f"  - {topic}: {avg_engagement:.1f} avg engagement")
    
    def _calculate_optimal_parameters(self):
        """Calculate optimal generation parameters"""
        self.optimal_params = {
            'preferred_structure': None,
            'optimal_length': None,
            'best_posting_times': [],
            'high_engagement_patterns': [],
            'vocabulary_focus': []
        }
        
        # Preferred structure (by engagement)
        best_structure = None
        best_avg_engagement = 0
        
        for structure, engagements in self.analyzed_data['engagement_patterns'].items():
            if engagements:
                avg = sum(engagements) / len(engagements)
                if avg > best_avg_engagement:
                    best_avg_engagement = avg
                    best_structure = structure
        
        self.optimal_params['preferred_structure'] = best_structure
        
        # Optimal length
        lengths = [len(tweet['text']) for tweet in self.all_tweets]
        self.optimal_params['optimal_length'] = sum(lengths) // len(lengths) if lengths else 150
        
        # Best posting times
        time_performance = {}
        for hour, engagements in self.analyzed_data['time_patterns'].items():
            if engagements:
                time_performance[hour] = sum(engagements) / len(engagements)
        
        top_hours = sorted(time_performance.items(), key=lambda x: x[1], reverse=True)[:3]
        self.optimal_params['best_posting_times'] = [hour for hour, _ in top_hours]
        
        logging.info(f"\nOptimal Parameters Calculated:")
        logging.info(f"  - Preferred Structure: {self.optimal_params['preferred_structure']}")
        logging.info(f"  - Optimal Length: {self.optimal_params['optimal_length']} chars")
        logging.info(f"  - Best Posting Times: {self.optimal_params['best_posting_times']}")
    
    def _generate_insights(self):
        """Generate actionable insights"""
        insights = []
        
        # Structure insights
        if self.analyzed_data['patterns']['canonical_3_part'] > 50:
            insights.append("Strong preference for 3-part structure (dismiss → focus → reality)")
        
        # Engagement insights
        high_performers = self.analyzed_data['high_performers']
        if high_performers:
            avg_high_length = sum(len(t['text']) for t in high_performers) // len(high_performers)
            insights.append(f"High-engagement tweets average {avg_high_length} characters")
        
        # Topic insights
        top_topics = sorted(self.analyzed_data['topics'].items(), 
                          key=lambda x: x[1], reverse=True)[:3]
        insights.append(f"Top topics: {', '.join([t[0] for t in top_topics])}")
        
        logging.info("\nKey Insights:")
        for insight in insights:
            logging.info(f"  • {insight}")
        
        return insights
    
    def create_enhanced_training_data(self):
        """Create enhanced training dataset from analyzed tweets"""
        logging.info("\nCreating enhanced training dataset...")
        
        training_data = []
        
        # Prioritize high-engagement tweets
        for tweet in self.analyzed_data['high_performers']:
            entry = {
                'prompt': 'Write a tweet in the style of Miles Deutscher:',
                'completion': f" {tweet['text']}",
                'metadata': {
                    'engagement_score': tweet['engagement'],
                    'structure': tweet['structure'],
                    'topics': tweet['topics'],
                    'quality_score': min(tweet['engagement'] / 1000, 1.0),  # Normalized
                    'source': '1000_tweets_fetch',
                    'collected_at': datetime.now().isoformat()
                }
            }
            training_data.append(entry)
        
        # Add other tweets with quality scoring
        for tweet in self.all_tweets:
            if not any(tweet['text'] == t['text'] for t in self.analyzed_data['high_performers']):
                metrics = tweet.get('public_metrics', {})
                engagement = self._calculate_engagement(metrics)
                
                entry = {
                    'prompt': 'Write a tweet in the style of Miles Deutscher:',
                    'completion': f" {tweet['text']}",
                    'metadata': {
                        'engagement_score': engagement,
                        'quality_score': min(engagement / 500, 0.8),  # Lower cap for regular tweets
                        'source': '1000_tweets_fetch',
                        'collected_at': datetime.now().isoformat()
                    }
                }
                training_data.append(entry)
        
        # Save enhanced dataset
        with open('miles_1000_enhanced.jsonl', 'w', encoding='utf-8') as f:
            for entry in training_data:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        logging.info(f"Created enhanced dataset with {len(training_data)} examples")
        logging.info(f"High-quality examples: {len(self.analyzed_data['high_performers'])}")
        
        # Save analysis results
        analysis_report = {
            'total_tweets_analyzed': len(self.all_tweets),
            'structures': dict(self.analyzed_data['structures']),
            'top_topics': dict(sorted(self.analyzed_data['topics'].items(), 
                                    key=lambda x: x[1], reverse=True)[:10]),
            'optimal_parameters': self.optimal_params,
            'high_performers_count': len(self.analyzed_data['high_performers']),
            'vocabulary_size': len(self.analyzed_data['vocabulary']),
            'timestamp': datetime.now().isoformat()
        }
        
        with open('miles_1000_analysis.json', 'w') as f:
            json.dump(analysis_report, f, indent=2)
        
        return training_data
    
    def generate_model_improvements(self):
        """Generate specific model improvement recommendations"""
        improvements = {
            'pattern_weights': {},
            'vocabulary_emphasis': [],
            'structure_preferences': {},
            'topic_boosts': {}
        }
        
        # Calculate pattern weights based on engagement
        for structure, engagements in self.analyzed_data['engagement_patterns'].items():
            if engagements:
                avg_engagement = sum(engagements) / len(engagements)
                improvements['pattern_weights'][structure] = min(avg_engagement / 500, 2.0)
        
        # Vocabulary emphasis (top performing words)
        high_engagement_words = Counter()
        for tweet in self.analyzed_data['high_performers']:
            words = re.findall(r'\b\w+\b', tweet['text'].lower())
            high_engagement_words.update(words)
        
        improvements['vocabulary_emphasis'] = [
            word for word, count in high_engagement_words.most_common(100)
            if len(word) > 3 and count > 2
        ]
        
        # Structure preferences
        total_tweets = sum(self.analyzed_data['structures'].values())
        for structure, count in self.analyzed_data['structures'].items():
            improvements['structure_preferences'][structure] = count / total_tweets
        
        # Topic boosts
        for topic, count in self.analyzed_data['topics'].items():
            improvements['topic_boosts'][topic] = min(count / 100, 1.5)
        
        # Save improvements
        with open('model_improvements.json', 'w') as f:
            json.dump(improvements, f, indent=2)
        
        logging.info("\nModel improvements generated and saved to model_improvements.json")
        
        return improvements

# Main execution
if __name__ == "__main__":
    print("""
    ================================================================
         Miles Deutscher 1000 Tweets Advanced Fetcher             
    ================================================================
    """)
    
    fetcher = Advanced1000TweetsFetcher()
    
    # Fetch tweets
    print("\n[FETCH] Fetching last 1000 tweets from @milesdeutscher...")
    tweets = fetcher.fetch_1000_tweets()
    
    if tweets:
        # Analyze tweets
        print(f"\n[ANALYZE] Analyzing {len(tweets)} tweets...")
        fetcher.deep_analyze_tweets()
        
        # Create enhanced training data
        print("\n[CREATE] Creating enhanced training dataset...")
        training_data = fetcher.create_enhanced_training_data()
        
        # Generate model improvements
        print("\n[OPTIMIZE] Generating model improvement recommendations...")
        improvements = fetcher.generate_model_improvements()
        
        print("\n[COMPLETE] Results saved to:")
        print("  - miles_1000_enhanced.jsonl (training data)")
        print("  - miles_1000_analysis.json (analysis report)")
        print("  - model_improvements.json (optimization parameters)")
        print("  - miles_1000_tweets.log (detailed logs)")
    else:
        print("\n[ERROR] Failed to fetch tweets. Check API credentials and connection.")