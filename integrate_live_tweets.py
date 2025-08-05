"""
Integrate live tweets from X API with existing dataset
"""
import json
from datetime import datetime

def integrate_live_tweets():
    """Integrate 739 live tweets with existing datasets"""
    print("=== Integrating Live X/Twitter Data ===\n")
    
    # Load live tweets
    with open('miles_tweets_live.json', 'r', encoding='utf-8') as f:
        live_data = json.load(f)
    
    print(f"[OK] Loaded {len(live_data['tweets'])} live tweets from X API")
    print(f"Date range: {live_data['statistics']['date_range']['earliest'][:10]} to {live_data['statistics']['date_range']['latest'][:10]}")
    print(f"Average engagement: {live_data['statistics']['engagement']['avg_likes']} likes\n")
    
    # Load existing final model
    with open('miles_final_data_model.json', 'r', encoding='utf-8') as f:
        final_model = json.load(f)
    
    print(f"[OK] Loaded existing model with {final_model['metadata']['total_tweets']} tweets\n")
    
    # Add live tweets to the model
    live_tweets_normalized = []
    for tweet in live_data['tweets']:
        # Add source identifier
        tweet['source'] = 'x_api_live'
        tweet['fetch_date'] = live_data['metadata']['fetch_date']
        live_tweets_normalized.append(tweet)
    
    # Combine with existing tweets
    all_tweets = final_model['all_tweets'] + live_tweets_normalized
    
    # Sort by quality score (descending)
    all_tweets.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
    
    # Update high quality training set
    high_quality_tweets = [t for t in all_tweets if t.get('quality_score', 0) >= 0.7]
    
    # Update statistics
    pattern_counts = {}
    for tweet in all_tweets:
        pattern = tweet.get('pattern', 'unknown')
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    
    # Create enhanced final model
    enhanced_model = {
        "metadata": {
            "version": "3.0",
            "created_at": datetime.now().isoformat(),
            "total_tweets": len(all_tweets),
            "live_tweets_added": len(live_data['tweets']),
            "sources": ["original_994", "finetune_500", "structured_5000", "original_741", "x_api_live"],
            "last_live_update": live_data['metadata']['fetch_date']
        },
        "statistics": {
            "pattern_distribution": pattern_counts,
            "live_tweet_stats": live_data['statistics'],
            "combined_stats": {
                "total_tweets": len(all_tweets),
                "high_quality_count": len(high_quality_tweets),
                "high_quality_percentage": round(len(high_quality_tweets) / len(all_tweets) * 100, 1)
            }
        },
        "training_sets": {
            "high_quality": {
                "count": len(high_quality_tweets),
                "tweets": high_quality_tweets[:3000]  # Top 3000
            }
        },
        "all_tweets": all_tweets
    }
    
    # Save enhanced model
    print("Saving enhanced model with live data...")
    
    with open('miles_final_model_with_live.json', 'w', encoding='utf-8') as f:
        json.dump(enhanced_model, f, indent=2, ensure_ascii=False)
    print("[OK] Saved miles_final_model_with_live.json")
    
    # Create training dataset with live examples
    with open('miles_training_with_live.jsonl', 'w', encoding='utf-8') as f:
        for tweet in high_quality_tweets[:3500]:  # Increased to 3500
            topics = tweet.get('topic_categories', [])
            topic = topics[0] if topics else 'crypto'
            
            training_example = {
                "prompt": f"Write a tweet in the style of Miles Deutscher about {topic}",
                "completion": tweet.get('text', tweet.get('clean_text', ''))
            }
            f.write(json.dumps(training_example, ensure_ascii=False) + '\n')
    print("[OK] Saved miles_training_with_live.jsonl")
    
    # Display summary
    print("\n=== Integration Summary ===")
    print(f"Previous total: {final_model['metadata']['total_tweets']} tweets")
    print(f"Added from X API: {len(live_data['tweets'])} tweets")
    print(f"New total: {len(all_tweets)} tweets")
    print(f"High quality tweets: {len(high_quality_tweets)}")
    
    print("\nTop patterns in combined dataset:")
    top_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for pattern, count in top_patterns:
        percentage = round(count / len(all_tweets) * 100, 1)
        print(f"  {pattern}: {count} ({percentage}%)")
    
    print("\n[SUCCESS] Live tweets integrated successfully!")
    
    return enhanced_model

if __name__ == "__main__":
    integrate_live_tweets()