"""
Integrate all Miles Deutscher datasets into final data model
Combines:
1. Original 994 tweets from miles_1000_enhanced.jsonl
2. Fine-tuning dataset with 741 examples
3. New structured dataset with 5000 tweets
"""
import json
from datetime import datetime
from typing import Dict, List, Set
import os

class FinalDataModelIntegrator:
    def __init__(self):
        self.datasets = {}
        self.all_tweets = []
        self.pattern_analysis = {}
        self.quality_metrics = {}
        
    def load_datasets(self):
        """Load all available datasets"""
        print("Loading datasets...")
        
        # 1. Load original 994 tweets
        if os.path.exists("miles_1000_enhanced.jsonl"):
            with open("miles_1000_enhanced.jsonl", 'r', encoding='utf-8') as f:
                tweets = []
                for line in f:
                    tweets.append(json.loads(line))
                self.datasets['original_994'] = tweets
                print(f"[OK] Loaded {len(tweets)} tweets from miles_1000_enhanced.jsonl")
        
        # 2. Load fine-tuning enhanced dataset (500 tweets)
        if os.path.exists("miles_finetune_enhanced.json"):
            with open("miles_finetune_enhanced.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.datasets['finetune_500'] = data['tweets']
                print(f"[OK] Loaded {len(data['tweets'])} tweets from miles_finetune_enhanced.json")
        
        # 3. Load new 5000 structured tweets
        if os.path.exists("miles_5000_tweets_structured.json"):
            with open("miles_5000_tweets_structured.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.datasets['structured_5000'] = data['tweets']
                print(f"[OK] Loaded {len(data['tweets'])} tweets from miles_5000_tweets_structured.json")
        
        # 4. Load original dataset (741 examples)
        if os.path.exists("miles_deutscher_dataset.jsonl"):
            with open("miles_deutscher_dataset.jsonl", 'r', encoding='utf-8') as f:
                examples = []
                for line in f:
                    example = json.loads(line)
                    # Extract tweet from completion
                    if 'completion' in example:
                        examples.append({
                            "text": example['completion'].strip(),
                            "source": "original_dataset",
                            "type": "training_example"
                        })
                self.datasets['original_741'] = examples
                print(f"[OK] Loaded {len(examples)} examples from miles_deutscher_dataset.jsonl")
        
        print(f"\nTotal datasets loaded: {len(self.datasets)}")
        
    def normalize_tweet(self, tweet: Dict, source: str) -> Dict:
        """Normalize tweet structure across different sources"""
        normalized = {
            "source": source,
            "original_format": {}
        }
        
        # Handle different formats
        if source == "original_994":
            normalized.update({
                "id": tweet.get('id', ''),
                "text": tweet.get('text', ''),
                "clean_text": tweet.get('clean_text', tweet.get('text', '')),
                "created_at": tweet.get('created_at', ''),
                "pattern": tweet.get('pattern', 'unknown'),
                "metrics": tweet.get('metrics', {}),
                "quality_score": tweet.get('quality_score', 0.5),
                "topic_categories": tweet.get('topics', []),
                "engagement_rate": tweet.get('engagement_rate', 0),
                "word_count": len(tweet.get('text', '').split()),
                "original_format": tweet
            })
            
        elif source == "structured_5000":
            # Already in perfect format
            normalized.update(tweet)
            normalized["source"] = source
            
        elif source == "finetune_500":
            normalized.update({
                "id": tweet.get('id', ''),
                "text": tweet.get('text', ''),
                "clean_text": tweet.get('text', ''),
                "pattern": tweet.get('pattern', 'unknown'),
                "quality_score": tweet.get('quality_score', 0.8),
                "source": tweet.get('source', source),
                "metrics": {"likes": 0, "retweets": 0, "replies": 0, "quotes": 0},
                "topic_categories": [],
                "word_count": len(tweet.get('text', '').split())
            })
            
        elif source == "original_741":
            normalized.update({
                "id": f"training_{hash(tweet['text'])}"[:16],
                "text": tweet['text'],
                "clean_text": tweet['text'],
                "pattern": "unknown",
                "quality_score": 0.9,  # High quality training examples
                "source": source,
                "type": "training_example",
                "metrics": {"likes": 0, "retweets": 0, "replies": 0, "quotes": 0},
                "topic_categories": [],
                "word_count": len(tweet['text'].split())
            })
        
        return normalized
    
    def deduplicate_tweets(self, tweets: List[Dict]) -> List[Dict]:
        """Remove duplicate tweets based on text similarity"""
        seen_texts = set()
        unique_tweets = []
        
        for tweet in tweets:
            # Create a normalized version for comparison
            text_key = ' '.join(tweet.get('clean_text', tweet.get('text', '')).lower().split())
            
            if text_key and text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_tweets.append(tweet)
        
        print(f"Deduplication: {len(tweets)} -> {len(unique_tweets)} tweets")
        return unique_tweets
    
    def analyze_patterns(self, tweets: List[Dict]):
        """Analyze pattern distribution and effectiveness"""
        pattern_stats = {}
        
        for tweet in tweets:
            pattern = tweet.get('pattern', 'unknown')
            if pattern not in pattern_stats:
                pattern_stats[pattern] = {
                    'count': 0,
                    'total_engagement': 0,
                    'total_quality': 0,
                    'avg_word_count': 0
                }
            
            stats = pattern_stats[pattern]
            stats['count'] += 1
            
            # Calculate engagement
            metrics = tweet.get('metrics', {})
            engagement = (
                metrics.get('likes', 0) + 
                metrics.get('retweets', 0) * 3 +
                metrics.get('replies', 0) * 2
            )
            stats['total_engagement'] += engagement
            
            # Add quality score
            stats['total_quality'] += tweet.get('quality_score', 0.5)
            stats['avg_word_count'] += tweet.get('word_count', 0)
        
        # Calculate averages
        for pattern, stats in pattern_stats.items():
            if stats['count'] > 0:
                stats['avg_engagement'] = round(stats['total_engagement'] / stats['count'], 2)
                stats['avg_quality'] = round(stats['total_quality'] / stats['count'], 3)
                stats['avg_word_count'] = round(stats['avg_word_count'] / stats['count'], 1)
        
        self.pattern_analysis = pattern_stats
    
    def calculate_quality_distribution(self, tweets: List[Dict]):
        """Calculate quality score distribution"""
        quality_buckets = {
            'excellent': 0,  # >= 0.8
            'good': 0,       # >= 0.6
            'average': 0,    # >= 0.4
            'poor': 0        # < 0.4
        }
        
        for tweet in tweets:
            score = tweet.get('quality_score', 0.5)
            if score >= 0.8:
                quality_buckets['excellent'] += 1
            elif score >= 0.6:
                quality_buckets['good'] += 1
            elif score >= 0.4:
                quality_buckets['average'] += 1
            else:
                quality_buckets['poor'] += 1
        
        self.quality_metrics = quality_buckets
    
    def integrate_all_datasets(self):
        """Integrate all datasets into final model"""
        print("\n=== Integrating Datasets ===")
        
        all_tweets = []
        
        # Process each dataset
        for source, tweets in self.datasets.items():
            print(f"\nProcessing {source}...")
            normalized = [self.normalize_tweet(tweet, source) for tweet in tweets]
            all_tweets.extend(normalized)
            print(f"Added {len(normalized)} tweets from {source}")
        
        # Deduplicate
        print("\nDeduplicating tweets...")
        unique_tweets = self.deduplicate_tweets(all_tweets)
        
        # Analyze patterns
        print("\nAnalyzing patterns...")
        self.analyze_patterns(unique_tweets)
        
        # Calculate quality distribution
        print("Calculating quality distribution...")
        self.calculate_quality_distribution(unique_tweets)
        
        self.all_tweets = unique_tweets
        
    def create_final_model(self):
        """Create the final data model"""
        print("\n=== Creating Final Data Model ===")
        
        # Sort tweets by quality score (descending)
        self.all_tweets.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        # Create training sets
        high_quality_tweets = [t for t in self.all_tweets if t.get('quality_score', 0) >= 0.7]
        medium_quality_tweets = [t for t in self.all_tweets if 0.5 <= t.get('quality_score', 0) < 0.7]
        
        # Create final model structure
        final_model = {
            "metadata": {
                "version": "2.0",
                "created_at": datetime.now().isoformat(),
                "total_tweets": len(self.all_tweets),
                "unique_tweets": len(self.all_tweets),
                "sources": list(self.datasets.keys()),
                "integration_method": "normalized_deduplication"
            },
            "statistics": {
                "pattern_analysis": self.pattern_analysis,
                "quality_distribution": self.quality_metrics,
                "source_distribution": {
                    source: len([t for t in self.all_tweets if t.get('source') == source])
                    for source in self.datasets.keys()
                }
            },
            "training_sets": {
                "high_quality": {
                    "count": len(high_quality_tweets),
                    "avg_quality": round(sum(t.get('quality_score', 0) for t in high_quality_tweets) / len(high_quality_tweets), 3) if high_quality_tweets else 0,
                    "tweets": high_quality_tweets[:2000]  # Top 2000
                },
                "medium_quality": {
                    "count": len(medium_quality_tweets),
                    "avg_quality": round(sum(t.get('quality_score', 0) for t in medium_quality_tweets) / len(medium_quality_tweets), 3) if medium_quality_tweets else 0,
                    "tweets": medium_quality_tweets[:1000]  # Top 1000
                }
            },
            "all_tweets": self.all_tweets
        }
        
        # Save final model
        print("\nSaving final data model...")
        
        # Full model
        with open("miles_final_data_model.json", 'w', encoding='utf-8') as f:
            json.dump(final_model, f, indent=2, ensure_ascii=False)
        print("[OK] Saved miles_final_data_model.json")
        
        # Training-ready format (JSONL)
        with open("miles_final_training_data.jsonl", 'w', encoding='utf-8') as f:
            for tweet in high_quality_tweets[:3000]:  # Top 3000 for training
                # Get topic safely
                topics = tweet.get('topic_categories', [])
                topic = topics[0] if topics else 'crypto'
                
                training_example = {
                    "prompt": f"Write a tweet in the style of Miles Deutscher about {topic}",
                    "completion": tweet['text']
                }
                f.write(json.dumps(training_example, ensure_ascii=False) + '\n')
        print("[OK] Saved miles_final_training_data.jsonl")
        
        # Pattern examples
        pattern_examples = {}
        for tweet in self.all_tweets:
            pattern = tweet.get('pattern', 'unknown')
            if pattern not in pattern_examples:
                pattern_examples[pattern] = []
            if len(pattern_examples[pattern]) < 10:
                pattern_examples[pattern].append({
                    "text": tweet['text'],
                    "quality_score": tweet.get('quality_score', 0),
                    "metrics": tweet.get('metrics', {})
                })
        
        with open("miles_pattern_examples.json", 'w', encoding='utf-8') as f:
            json.dump(pattern_examples, f, indent=2, ensure_ascii=False)
        print("[OK] Saved miles_pattern_examples.json")
        
        return final_model
    
    def display_summary(self, final_model: Dict):
        """Display summary of final model"""
        print("\n=== Final Data Model Summary ===")
        print(f"Total tweets: {final_model['metadata']['total_tweets']}")
        print(f"High quality tweets: {final_model['training_sets']['high_quality']['count']}")
        print(f"Medium quality tweets: {final_model['training_sets']['medium_quality']['count']}")
        
        print("\nSource distribution:")
        for source, count in final_model['statistics']['source_distribution'].items():
            print(f"  {source}: {count}")
        
        print("\nPattern effectiveness (top 5):")
        patterns = sorted(
            final_model['statistics']['pattern_analysis'].items(),
            key=lambda x: x[1]['avg_quality'],
            reverse=True
        )[:5]
        
        for pattern, stats in patterns:
            print(f"  {pattern}:")
            print(f"    Count: {stats['count']}")
            print(f"    Avg quality: {stats['avg_quality']}")
            print(f"    Avg engagement: {stats['avg_engagement']}")
        
        print("\nQuality distribution:")
        for quality, count in final_model['statistics']['quality_distribution'].items():
            percentage = round(count / final_model['metadata']['total_tweets'] * 100, 1)
            print(f"  {quality}: {count} ({percentage}%)")
        
        print("\n[SUCCESS] Final data model created!")
        print("\nFiles created:")
        print("- miles_final_data_model.json (complete model)")
        print("- miles_final_training_data.jsonl (3000 best examples)")
        print("- miles_pattern_examples.json (pattern examples)")

def main():
    """Main execution"""
    integrator = FinalDataModelIntegrator()
    
    # Load all datasets
    integrator.load_datasets()
    
    # Integrate datasets
    integrator.integrate_all_datasets()
    
    # Create final model
    final_model = integrator.create_final_model()
    
    # Display summary
    integrator.display_summary(final_model)

if __name__ == "__main__":
    main()