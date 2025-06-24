import json
import matplotlib.pyplot as plt
import numpy as np

def analyze_tweet_lengths():
    # Read the JSONL file
    lengths = []
    with open('data.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            tweet = json.loads(line)
            lengths.append(len(tweet['prompt']) + len(tweet['completion']))
    
    # Create histogram
    plt.figure(figsize=(12, 6))
    plt.hist(lengths, bins=50, edgecolor='black')
    plt.title('Distribution of Tweet Lengths')
    plt.xlabel('Length (characters)')
    plt.ylabel('Number of Tweets')
    
    # Add statistics as text
    stats_text = f'Mean: {np.mean(lengths):.1f}\nMedian: {np.median(lengths):.1f}\nMin: {min(lengths)}\nMax: {max(lengths)}'
    plt.text(0.95, 0.95, stats_text,
             transform=plt.gca().transAxes,
             verticalalignment='top',
             horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Save the plot
    plt.savefig('tweet_length_distribution.png')
    
    # Print statistics
    print(f"Total tweets analyzed: {len(lengths)}")
    print(f"Mean length: {np.mean(lengths):.1f} characters")
    print(f"Median length: {np.median(lengths):.1f} characters")
    print(f"Min length: {min(lengths)} characters")
    print(f"Max length: {max(lengths)} characters")

if __name__ == "__main__":
    analyze_tweet_lengths() 