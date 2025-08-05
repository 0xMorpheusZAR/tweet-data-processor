"""
Run the original tweet processor with Miles Deutscher identifier
"""

import subprocess
import sys
import os

print("""
================================================================
    MILES DEUTSCHER AI - Original Tweet Processor
================================================================

This will run the original process_tweets.py script to:
1. Process tweets.js file
2. Create proper fine-tuning dataset
3. Generate data.jsonl with correct format

================================================================
""")

# Set the identifier
IDENTIFIER = "Miles Deutscher"

print(f"\nUsing identifier: '{IDENTIFIER}'")
print("This will create prompts like: 'Write a tweet in the style of Miles Deutscher'")

# Create a temporary script that auto-inputs the identifier
temp_script = """
import json
import random

def process_tweets(user_identifier):
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
                prompt = f\"\"\"Write a tweet in the style of {user_identifier}. Here are some examples:\\n\\n{example_tweets[0]}\\n\\n{example_tweets[1]}\\n\\n{example_tweets[2]}\\n\\nNow write a new tweet:\"\"\"
                
                dataset.append({
                    "prompt": prompt,
                    "completion": " " + full_text
                })
        else:
            print(f"Tweet object missing required fields. Keys present: {tweet_obj.keys()}")
    
    # Shuffle the dataset for better training
    random.shuffle(dataset)
    
    # Save the dataset as a JSONL file
    with open('data_miles_original.jsonl', 'w', encoding='utf-8') as f:
        for item in dataset:
            # Convert any sets to lists before JSON serialization
            json_str = json.dumps(item, ensure_ascii=False, default=lambda x: list(x) if isinstance(x, set) else x)
            f.write(json_str + '\\n')
    
    print(f"Processed {len(dataset)} tweets successfully!")
    print(f"Using {len(example_tweets)} example tweets in the prompt")
    
    return len(dataset)

# Set random seed for reproducibility
random.seed(42)
num_processed = process_tweets('""" + IDENTIFIER + """')
print(f"\\nDataset created: data_miles_original.jsonl")
print(f"Total training examples: {num_processed}")
"""

# Write temporary script
with open('temp_process.py', 'w', encoding='utf-8') as f:
    f.write(temp_script)

# Run the temporary script
try:
    result = subprocess.run([sys.executable, 'temp_process.py'], 
                          capture_output=True, text=True)
    
    print("\n--- Process Output ---")
    print(result.stdout)
    
    if result.stderr:
        print("\n--- Errors (if any) ---")
        print(result.stderr)
    
    # Clean up
    os.remove('temp_process.py')
    
    # Now run the split dataset script
    print("\n" + "="*60)
    print("Running split_dataset.py to create train/val split...")
    print("="*60)
    
    # Check if split_dataset.py exists
    if os.path.exists('split_dataset.py'):
        # First rename the output file to data.jsonl temporarily
        if os.path.exists('data_miles_original.jsonl'):
            os.rename('data_miles_original.jsonl', 'data.jsonl')
        
        result = subprocess.run([sys.executable, 'split_dataset.py'], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Rename back
        if os.path.exists('data.jsonl'):
            os.rename('data.jsonl', 'data_miles_original.jsonl')
    
    # Analyze tweet lengths
    print("\n" + "="*60)
    print("Running analyze_tweet_lengths.py...")
    print("="*60)
    
    if os.path.exists('analyze_tweet_lengths.py'):
        result = subprocess.run([sys.executable, 'analyze_tweet_lengths.py'], 
                              capture_output=True, text=True)
        print(result.stdout)
    
    print("\n" + "="*60)
    print("✅ Original Processing Complete!")
    print("="*60)
    print("\nFiles created:")
    print("  - data_miles_original.jsonl (full dataset)")
    print("  - train.jsonl (training split)")
    print("  - val.jsonl (validation split)")
    
except Exception as e:
    print(f"\nError: {e}")
    # Clean up temp file if error
    if os.path.exists('temp_process.py'):
        os.remove('temp_process.py')