"""
Integrate the fine-tuning dataset with Miles AI Ultimate System
"""
import json
import os

def integrate_dataset():
    """Integrate miles_deutscher_dataset.jsonl with the Ultimate System"""
    
    print("=== Miles AI Dataset Integration ===\n")
    
    # Load the fine-tuning dataset
    dataset_path = "miles_deutscher_dataset.jsonl"
    training_examples = []
    
    print(f"Loading fine-tuning dataset from {dataset_path}...")
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            training_examples.append(json.loads(line))
    
    print(f"[OK] Loaded {len(training_examples)} training examples\n")
    
    # Extract unique completions for pattern analysis
    unique_tweets = []
    for example in training_examples:
        completion = example['completion'].strip()
        if completion and not completion.startswith('RT'):
            unique_tweets.append(completion)
    
    print(f"[OK] Extracted {len(unique_tweets)} unique tweets\n")
    
    # Create enhanced training data format for Ultimate System
    enhanced_data = []
    for i, tweet in enumerate(unique_tweets[:500]):  # Limit to 500 for performance
        enhanced_data.append({
            "id": f"finetune_{i}",
            "text": tweet,
            "source": "original_dataset",
            "pattern": "unknown",  # Will be analyzed by system
            "quality_score": 0.8   # High quality from original dataset
        })
    
    # Save enhanced data
    output_path = "miles_finetune_enhanced.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "tweets": enhanced_data,
            "metadata": {
                "source": "miles_deutscher_dataset.jsonl",
                "total_examples": len(training_examples),
                "processed_tweets": len(enhanced_data),
                "integration_date": "2025-01-08"
            }
        }, f, indent=2)
    
    print(f"[OK] Created enhanced dataset: {output_path}")
    print(f"  - Total examples: {len(training_examples)}")
    print(f"  - Processed tweets: {len(enhanced_data)}")
    
    # Create integration config for Ultimate System
    config = {
        "dataset_integration": {
            "primary_source": "miles_1000_enhanced.jsonl",
            "finetune_source": "miles_finetune_enhanced.json",
            "merge_strategy": "weighted",
            "weights": {
                "primary": 0.7,
                "finetune": 0.3
            }
        },
        "pattern_recognition": {
            "use_finetune_examples": True,
            "min_confidence": 0.6
        },
        "generation_config": {
            "temperature": 0.8,
            "top_p": 0.9,
            "use_examples": True,
            "example_count": 3
        }
    }
    
    config_path = "integration_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n[OK] Created integration config: {config_path}")
    
    # Display sample integrated data
    print("\n=== Sample Integrated Data ===")
    for i in range(min(3, len(enhanced_data))):
        tweet = enhanced_data[i]
        print(f"\nExample {i+1}:")
        print(f"Text: {tweet['text'][:100]}...")
        print(f"Source: {tweet['source']}")
        print(f"Quality Score: {tweet['quality_score']}")
    
    print("\n=== Integration Complete! ===")
    print("\nNext steps:")
    print("1. The Ultimate System can now load miles_finetune_enhanced.json")
    print("2. Use integration_config.json for weighted merging")
    print("3. The system will combine both datasets for improved generation")
    print("\nTotal training data available:")
    print(f"- Original enhanced dataset: 994 tweets")
    print(f"- Fine-tuning dataset: {len(enhanced_data)} tweets")
    print(f"- Combined total: {994 + len(enhanced_data)} examples")

if __name__ == "__main__":
    integrate_dataset()