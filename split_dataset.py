import json
import random

def split_dataset():
    # Read the JSONL file
    tweets = []
    with open('data.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            tweet = json.loads(line)
            tweets.append(tweet)
    
    # Shuffle the tweets
    random.shuffle(tweets)
    
    # Calculate split index
    split_idx = int(len(tweets) * 0.8)
    
    # Split into training and validation sets
    train_tweets = tweets[:split_idx]
    val_tweets = tweets[split_idx:]
    
    # Save training set
    with open('train.jsonl', 'w', encoding='utf-8') as f:
        for tweet in train_tweets:
            f.write(json.dumps(tweet, ensure_ascii=False) + '\n')
    
    # Save validation set
    with open('val.jsonl', 'w', encoding='utf-8') as f:
        for tweet in val_tweets:
            f.write(json.dumps(tweet, ensure_ascii=False) + '\n')
    
    print(f"Total tweets: {len(tweets)}")
    print(f"Training set size: {len(train_tweets)} (80%)")
    print(f"Validation set size: {len(val_tweets)} (20%)")

if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    split_dataset() 