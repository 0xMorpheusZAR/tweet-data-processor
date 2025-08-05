"""
Miles Deutscher AI - Training Data Update System
Fetches latest tweets and updates training dataset
"""

import os
import json
import time
import urllib.request
import urllib.parse
import ssl
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple
import re
import hashlib
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training_update.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TrainingDataUpdater:
    """Updates training data with latest tweets from Miles Deutscher"""
    
    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN', 
            'AAAAAAAAAAAAAAAAAAAAAJi13QEAAAAAghVwuLws1YdchbwCAkUjqqwu6oc%3DeImrILD6DNOvuOdZiH42oFM3Ww7zTLYaiz1onypLp8XNzCskQ7')
        
        self.existing_tweets = set()
        self.new_tweets = []
        self.stats = {
            'existing_count': 0,
            'new_count': 0,
            'high_quality_count': 0,
            'filtered_count': 0
        }
        
    def load_existing_data(self) -> List[Dict]:
        """Load existing training data"""
        training_data = []
        
        # Check which file to use
        data_files = ['miles_1000_enhanced.jsonl', 'data.jsonl']
        
        for file_name in data_files:
            if os.path.exists(file_name):
                logger.info(f"Loading existing data from {file_name}")
                
                try:
                    with open(file_name, 'r', encoding='utf-8') as f:
                        for line in f:
                            entry = json.loads(line)
                            training_data.append(entry)
                            
                            # Track existing tweets by text hash
                            text = entry.get('completion', '').strip()
                            if text:
                                text_hash = hashlib.md5(text.encode()).hexdigest()
                                self.existing_tweets.add(text_hash)
                    
                    self.stats['existing_count'] = len(training_data)
                    logger.info(f"Loaded {len(training_data)} existing training examples")
                    break
                    
                except Exception as e:
                    logger.error(f"Error loading {file_name}: {e}")
        
        return training_data
    
    def fetch_latest_tweets(self, count: int = 200, since_hours: int = 168) -> List[Dict]:
        """Fetch latest tweets from Miles (last 7 days by default)"""
        logger.info(f"Fetching latest tweets from @milesdeutscher (last {since_hours} hours)")
        
        try:
            # Get user ID
            url = "https://api.twitter.com/2/users/by/username/milesdeutscher"
            req = urllib.request.Request(url)
            req.add_header('Authorization', f'Bearer {self.bearer_token}')
            
            context = ssl.create_default_context()
            with urllib.request.urlopen(req, context=context) as response:
                user_data = json.loads(response.read().decode())
            
            if 'data' not in user_data:
                logger.error("Could not fetch user data")
                return []
            
            user_id = user_data['data']['id']
            
            # Calculate time window
            start_time = (datetime.utcnow() - timedelta(hours=since_hours)).isoformat() + 'Z'
            
            # Fetch tweets
            tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            params = {
                'max_results': min(count, 100),
                'tweet.fields': 'created_at,public_metrics,context_annotations,entities,referenced_tweets',
                'exclude': 'retweets',
                'start_time': start_time
            }
            
            tweets_url += '?' + urllib.parse.urlencode(params)
            
            req = urllib.request.Request(tweets_url)
            req.add_header('Authorization', f'Bearer {self.bearer_token}')
            
            with urllib.request.urlopen(req, context=context) as response:
                tweets_data = json.loads(response.read().decode())
            
            tweets = tweets_data.get('data', [])
            logger.info(f"Fetched {len(tweets)} recent tweets")
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            return []
    
    def analyze_tweet_quality(self, tweet: Dict) -> Dict:
        """Analyze tweet quality and characteristics"""
        text = tweet.get('text', '')
        metrics = tweet.get('public_metrics', {})
        
        # Calculate engagement score
        engagement = (
            metrics.get('like_count', 0) * 1 +
            metrics.get('retweet_count', 0) * 2 +
            metrics.get('reply_count', 0) * 1.5 +
            metrics.get('quote_count', 0) * 2.5
        )
        
        # Analyze structure
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        structure = f"{len(lines)}_part"
        
        # Detect patterns
        is_thread = text.startswith('🧵') or text.endswith('👇')
        has_link = 'http' in text or 't.co' in text
        is_reply = text.startswith('@')
        
        # Calculate quality score
        quality_score = 0.5  # Base score
        
        if engagement > 500:
            quality_score += 0.3
        elif engagement > 200:
            quality_score += 0.2
        elif engagement > 100:
            quality_score += 0.1
        
        if structure in ['3_part', '2_part']:
            quality_score += 0.1
        
        if not is_thread and not has_link and not is_reply:
            quality_score += 0.1
        
        return {
            'text': text,
            'structure': structure,
            'engagement': engagement,
            'quality_score': min(quality_score, 1.0),
            'is_thread': is_thread,
            'has_link': has_link,
            'metrics': metrics,
            'created_at': tweet.get('created_at', '')
        }
    
    def filter_and_process_tweets(self, tweets: List[Dict]) -> List[Dict]:
        """Filter and process tweets for training"""
        processed = []
        
        for tweet in tweets:
            # Analyze quality
            analysis = self.analyze_tweet_quality(tweet)
            
            # Check if already exists
            text_hash = hashlib.md5(analysis['text'].encode()).hexdigest()
            if text_hash in self.existing_tweets:
                continue
            
            # Filter criteria
            if analysis['is_thread']:
                self.stats['filtered_count'] += 1
                continue
            
            if analysis['quality_score'] < 0.4:
                self.stats['filtered_count'] += 1
                continue
            
            # Create training entry
            entry = {
                'prompt': 'Write a tweet in the style of Miles Deutscher:',
                'completion': f" {analysis['text']}",
                'metadata': {
                    'source': 'twitter_update',
                    'collected_at': datetime.now().isoformat(),
                    'quality_score': analysis['quality_score'],
                    'engagement': analysis['engagement'],
                    'structure': analysis['structure'],
                    'metrics': analysis['metrics']
                }
            }
            
            processed.append(entry)
            self.new_tweets.append(analysis)
            
            if analysis['quality_score'] >= 0.7:
                self.stats['high_quality_count'] += 1
        
        self.stats['new_count'] = len(processed)
        logger.info(f"Processed {len(processed)} new tweets for training")
        
        return processed
    
    def update_training_data(self, existing_data: List[Dict], new_data: List[Dict]) -> None:
        """Update training data files"""
        if not new_data:
            logger.info("No new tweets to add")
            return
        
        # Combine datasets
        combined_data = existing_data + new_data
        
        # Save updated dataset
        output_file = 'miles_enhanced_updated.jsonl'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in combined_data:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved updated dataset to {output_file}")
        logger.info(f"Total training examples: {len(combined_data)}")
        
        # Save update report
        self.save_update_report(combined_data)
    
    def save_update_report(self, combined_data: List[Dict]) -> None:
        """Save detailed update report"""
        report = {
            'update_timestamp': datetime.now().isoformat(),
            'statistics': {
                'previous_count': self.stats['existing_count'],
                'new_tweets_added': self.stats['new_count'],
                'filtered_out': self.stats['filtered_count'],
                'high_quality_new': self.stats['high_quality_count'],
                'total_count': len(combined_data)
            },
            'quality_distribution': self._calculate_quality_distribution(combined_data),
            'structure_distribution': self._calculate_structure_distribution(combined_data),
            'top_new_tweets': self._get_top_new_tweets(5)
        }
        
        with open('training_update_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("Saved update report to training_update_report.json")
    
    def _calculate_quality_distribution(self, data: List[Dict]) -> Dict:
        """Calculate quality score distribution"""
        distribution = {
            'high': 0,  # >= 0.7
            'medium': 0,  # 0.4 - 0.7
            'low': 0  # < 0.4
        }
        
        for entry in data:
            score = entry.get('metadata', {}).get('quality_score', 0.5)
            if score >= 0.7:
                distribution['high'] += 1
            elif score >= 0.4:
                distribution['medium'] += 1
            else:
                distribution['low'] += 1
        
        return distribution
    
    def _calculate_structure_distribution(self, data: List[Dict]) -> Dict:
        """Calculate structure distribution"""
        structures = defaultdict(int)
        
        for entry in data:
            structure = entry.get('metadata', {}).get('structure', 'unknown')
            structures[structure] += 1
        
        return dict(structures)
    
    def _get_top_new_tweets(self, count: int) -> List[Dict]:
        """Get top new tweets by engagement"""
        sorted_tweets = sorted(self.new_tweets, 
                             key=lambda x: x['engagement'], 
                             reverse=True)
        
        return [
            {
                'text': tweet['text'][:100] + '...' if len(tweet['text']) > 100 else tweet['text'],
                'engagement': tweet['engagement'],
                'structure': tweet['structure']
            }
            for tweet in sorted_tweets[:count]
        ]
    
    def run_update(self):
        """Run complete training data update"""
        print("\n" + "="*60)
        print("Miles Deutscher AI - Training Data Update")
        print("="*60)
        
        # Load existing data
        print("\n1. Loading existing training data...")
        existing_data = self.load_existing_data()
        
        # Fetch latest tweets
        print("\n2. Fetching latest tweets from @milesdeutscher...")
        latest_tweets = self.fetch_latest_tweets(count=200, since_hours=168)
        
        if not latest_tweets:
            print("No new tweets fetched. Check API connection.")
            return
        
        # Process new tweets
        print("\n3. Processing and filtering new tweets...")
        new_data = self.filter_and_process_tweets(latest_tweets)
        
        # Update training data
        print("\n4. Updating training dataset...")
        self.update_training_data(existing_data, new_data)
        
        # Print summary
        print("\n" + "="*60)
        print("Update Summary:")
        print(f"  • Previous training examples: {self.stats['existing_count']}")
        print(f"  • New tweets fetched: {len(latest_tweets)}")
        print(f"  • New tweets added: {self.stats['new_count']}")
        print(f"  • High quality new tweets: {self.stats['high_quality_count']}")
        print(f"  • Filtered out: {self.stats['filtered_count']}")
        print(f"  • Total training examples: {self.stats['existing_count'] + self.stats['new_count']}")
        print("="*60)
        
        if self.stats['new_count'] > 0:
            print("\n✅ Training data successfully updated!")
            print(f"New file: miles_enhanced_updated.jsonl")
            print(f"Report: training_update_report.json")
        else:
            print("\n⚠️  No new tweets added (all were duplicates or filtered)")

# Utility functions for manual operations
def merge_datasets(file1: str, file2: str, output: str):
    """Merge two JSONL datasets"""
    seen_texts = set()
    merged_data = []
    
    for file_name in [file1, file2]:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    text = entry.get('completion', '').strip()
                    
                    # Avoid duplicates
                    text_hash = hashlib.md5(text.encode()).hexdigest()
                    if text_hash not in seen_texts:
                        seen_texts.add(text_hash)
                        merged_data.append(entry)
    
    # Save merged data
    with open(output, 'w', encoding='utf-8') as f:
        for entry in merged_data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"Merged {len(merged_data)} unique examples into {output}")

def analyze_dataset(file_name: str):
    """Analyze a training dataset"""
    if not os.path.exists(file_name):
        print(f"File {file_name} not found")
        return
    
    data = []
    with open(file_name, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    
    # Analyze
    structures = defaultdict(int)
    quality_scores = []
    engagement_scores = []
    
    for entry in data:
        metadata = entry.get('metadata', {})
        
        structures[metadata.get('structure', 'unknown')] += 1
        
        if 'quality_score' in metadata:
            quality_scores.append(metadata['quality_score'])
        
        if 'engagement' in metadata:
            engagement_scores.append(metadata['engagement'])
    
    print(f"\nDataset Analysis: {file_name}")
    print(f"Total examples: {len(data)}")
    
    print("\nStructure distribution:")
    for structure, count in sorted(structures.items(), key=lambda x: x[1], reverse=True):
        print(f"  {structure}: {count} ({count/len(data)*100:.1f}%)")
    
    if quality_scores:
        print(f"\nQuality scores:")
        print(f"  Average: {sum(quality_scores)/len(quality_scores):.2f}")
        print(f"  High quality (>0.7): {len([s for s in quality_scores if s > 0.7])}")
    
    if engagement_scores:
        print(f"\nEngagement:")
        print(f"  Average: {sum(engagement_scores)/len(engagement_scores):.1f}")
        print(f"  High engagement (>500): {len([s for s in engagement_scores if s > 500])}")

# Main execution
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "merge" and len(sys.argv) == 5:
            merge_datasets(sys.argv[2], sys.argv[3], sys.argv[4])
        
        elif command == "analyze" and len(sys.argv) == 3:
            analyze_dataset(sys.argv[2])
        
        else:
            print("Usage:")
            print("  python update_training_data.py  # Run update")
            print("  python update_training_data.py merge file1.jsonl file2.jsonl output.jsonl")
            print("  python update_training_data.py analyze dataset.jsonl")
    
    else:
        # Run update
        updater = TrainingDataUpdater()
        updater.run_update()