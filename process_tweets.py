import json
import random

def process_tweets():
    # Initialize empty dataset
    dataset = []
    example_tweets = []
    
    # Read tweets from file
    with open('tweets.js', 'r', encoding='utf-8') as f:
        # Skip the first line which might contain variable declaration
        content = f.read()
        print(f"File content length: {len(content)}")
        
        # Find the start of the JSON array
        start_idx = content.find('[')
        if start_idx == -1:
            raise ValueError("Could not find JSON array in tweets.js")
        print(f"Found JSON array start at index: {start_idx}")
        
        # Parse the JSON array
        try:
            tweet_objects = json.loads(content[start_idx:])
            print(f"Successfully parsed {len(tweet_objects)} tweet objects from JSON")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            # Print a small sample of the content to debug
            print("Content sample:", content[start_idx:start_idx+200])
            raise
    
    # First pass: collect example tweets
    for tweet_obj in tweet_objects:
        if 'tweet' in tweet_obj and 'full_text' in tweet_obj['tweet']:
            full_text = tweet_obj['tweet']['full_text']
            if not full_text.startswith('@'):
                example_tweets.append(full_text)
    
    # Shuffle and select 3 example tweets
    random.shuffle(example_tweets)
    example_tweets = example_tweets[:3]
    
    # Second pass: create training examples
    for tweet_obj in tweet_objects:
        if 'tweet' in tweet_obj and 'full_text' in tweet_obj['tweet']:
            full_text = tweet_obj['tweet']['full_text']
            # Skip tweets that start with '@'
            if not full_text.startswith('@') and not full_text.startswith('RT'):
                # Create a prompt that works with both instruction and chat formats
                prompt = f"""Write a tweet in the style of Harper Carroll AI. Here are some examples:

{example_tweets[0]}

{example_tweets[1]}

{example_tweets[2]}

Now write a new tweet:"""
                
                dataset.append({
                    "prompt": prompt,
                    "completion": " " + full_text
                })
        else:
            print(f"Tweet object missing required fields. Keys present: {tweet_obj.keys()}")
    
    # Shuffle the dataset for better training
    random.shuffle(dataset)
    
    # Save the dataset as a JSONL file
    with open('data.jsonl', 'w', encoding='utf-8') as f:
        for item in dataset:
            # Convert any sets to lists before JSON serialization
            json_str = json.dumps(item, ensure_ascii=False, default=lambda x: list(x) if isinstance(x, set) else x)
            f.write(json_str + '\n')
    
    print(f"Processed {len(dataset)} tweets successfully!")
    print(f"Using {len(example_tweets)} example tweets in the prompt")

if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    process_tweets() 