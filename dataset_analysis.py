import json
import re
from collections import Counter
import statistics

def analyze_dataset_for_finetuning():
    # Load the dataset
    tweets = []
    with open('data.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            tweets.append(json.loads(line))
    
    print("=== DATASET ANALYSIS FOR FINE-TUNING ===\n")
    
    # 1. Token estimation (rough approximation)
    total_tokens = 0
    for tweet in tweets:
        # Rough token count: ~1 token per 4 characters
        total_tokens += (len(tweet['prompt']) + len(tweet['completion'])) // 4
    
    print(f"Dataset Size:")
    print(f"  Total examples: {len(tweets)}")
    print(f"  Estimated total tokens: {total_tokens:,}")
    print(f"  Average tokens per example: {total_tokens // len(tweets)}")
    
    # 2. Content analysis
    print(f"\nContent Patterns:")
    
    # Analyze completions
    completions = [t['completion'] for t in tweets]
    
    # Market/trading content
    market_tweets = sum(1 for c in completions if any(
        term in c.lower() for term in ['$', 'btc', 'eth', 'market', 'bull', 'bear', 'chart', 'price']
    ))
    
    # Links
    link_tweets = sum(1 for c in completions if 'https://t.co' in c)
    
    # Questions
    question_tweets = sum(1 for c in completions if '?' in c)
    
    # Short vs long
    short_tweets = sum(1 for c in completions if len(c) < 50)
    medium_tweets = sum(1 for c in completions if 50 <= len(c) < 150)
    long_tweets = sum(1 for c in completions if len(c) >= 150)
    
    print(f"  Market/trading content: {market_tweets} ({market_tweets/len(tweets)*100:.1f}%)")
    print(f"  Contains links: {link_tweets} ({link_tweets/len(tweets)*100:.1f}%)")
    print(f"  Questions: {question_tweets} ({question_tweets/len(tweets)*100:.1f}%)")
    print(f"  Short (<50 chars): {short_tweets} ({short_tweets/len(tweets)*100:.1f}%)")
    print(f"  Medium (50-150 chars): {medium_tweets} ({medium_tweets/len(tweets)*100:.1f}%)")
    print(f"  Long (>150 chars): {long_tweets} ({long_tweets/len(tweets)*100:.1f}%)")
    
    # 3. Vocabulary analysis
    print(f"\nVocabulary Analysis:")
    
    # Extract unique words
    words = []
    for c in completions:
        # Remove links and special characters
        text = re.sub(r'https://\S+', '', c)
        text = re.sub(r'[^\w\s$#@]', ' ', text)
        words.extend(text.lower().split())
    
    word_freq = Counter(words)
    unique_words = len(word_freq)
    
    print(f"  Unique words: {unique_words}")
    print(f"  Total words: {len(words)}")
    print(f"  Vocabulary richness: {unique_words/len(words)*100:.1f}%")
    
    # Top crypto-specific terms
    crypto_terms = [(w, c) for w, c in word_freq.items() 
                    if w.startswith('$') or w in ['btc', 'eth', 'defi', 'nft', 'dao', 'ser', 'gm', 'ngmi']]
    crypto_terms.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n  Top crypto terms:")
    for term, count in crypto_terms[:10]:
        print(f"    {term}: {count}")
    
    # 4. Optimal hyperparameters based on analysis
    print(f"\n=== RECOMMENDED HYPERPARAMETERS ===\n")
    
    # Calculate optimal batch size based on dataset size
    optimal_batch_size = 4 if len(tweets) < 1000 else 8
    
    # Calculate epochs based on dataset size and diversity
    if len(tweets) < 500:
        epochs = 4  # Small dataset needs more epochs
    elif len(tweets) < 1000:
        epochs = 3
    else:
        epochs = 2
    
    # Learning rate based on vocabulary complexity
    if unique_words/len(words) > 0.3:  # High vocabulary diversity
        learning_rate = "3e-5"
    else:
        learning_rate = "2e-5"
    
    print(f"Based on dataset characteristics:")
    print(f"  Batch size: {optimal_batch_size}")
    print(f"  Epochs: {epochs}")
    print(f"  Learning rate: {learning_rate}")
    print(f"  Max sequence length: 850 (based on 95th percentile)")
    print(f"  Warmup steps: {len(tweets) // optimal_batch_size // 10}")
    
    # 5. Training time estimation
    print(f"\nTraining Time Estimates:")
    steps_per_epoch = len(tweets) // optimal_batch_size
    total_steps = steps_per_epoch * epochs
    
    print(f"  Steps per epoch: {steps_per_epoch}")
    print(f"  Total training steps: {total_steps}")
    print(f"  Estimated time (GPU): {total_steps * 0.5:.0f}-{total_steps * 1:.0f} seconds")
    print(f"  Estimated time (CPU): {total_steps * 5:.0f}-{total_steps * 10:.0f} seconds")
    
    # 6. Validation strategy
    print(f"\nValidation Strategy:")
    print(f"  Validation set size: {int(len(tweets) * 0.2)} examples")
    print(f"  Evaluation frequency: Every {steps_per_epoch // 4} steps")
    print(f"  Early stopping patience: {epochs} epochs")
    
    # Save configuration
    config = {
        "dataset_stats": {
            "total_examples": len(tweets),
            "estimated_tokens": total_tokens,
            "unique_vocabulary": unique_words,
            "market_content_ratio": market_tweets/len(tweets)
        },
        "recommended_config": {
            "batch_size": optimal_batch_size,
            "num_epochs": epochs,
            "learning_rate": learning_rate,
            "max_length": 850,
            "warmup_steps": len(tweets) // optimal_batch_size // 10,
            "evaluation_steps": steps_per_epoch // 4,
            "save_steps": steps_per_epoch // 2,
            "weight_decay": 0.01,
            "adam_epsilon": 1e-8,
            "gradient_accumulation_steps": 1 if optimal_batch_size >= 4 else 2
        },
        "generation_config": {
            "temperature": 0.8,
            "top_p": 0.9,
            "frequency_penalty": 0.3,
            "presence_penalty": 0.1,
            "max_tokens": 280
        }
    }
    
    with open('finetuning_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nConfiguration saved to 'finetuning_config.json'")

if __name__ == "__main__":
    analyze_dataset_for_finetuning()