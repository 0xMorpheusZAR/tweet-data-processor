import json
import statistics

def analyze_tweet_lengths():
    # Read the JSONL file
    lengths = []
    with open('data.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            tweet = json.loads(line)
            lengths.append(len(tweet['prompt']) + len(tweet['completion']))
    
    # Calculate statistics
    mean_length = statistics.mean(lengths)
    median_length = statistics.median(lengths)
    min_length = min(lengths)
    max_length = max(lengths)
    stdev_length = statistics.stdev(lengths)
    
    # Calculate percentiles
    sorted_lengths = sorted(lengths)
    p25 = sorted_lengths[int(len(sorted_lengths) * 0.25)]
    p75 = sorted_lengths[int(len(sorted_lengths) * 0.75)]
    p90 = sorted_lengths[int(len(sorted_lengths) * 0.90)]
    p95 = sorted_lengths[int(len(sorted_lengths) * 0.95)]
    
    # Print detailed statistics
    print(f"\n=== Tweet Length Analysis ===")
    print(f"Total tweets analyzed: {len(lengths)}")
    print(f"\nBasic Statistics:")
    print(f"  Mean length: {mean_length:.1f} characters")
    print(f"  Median length: {median_length:.1f} characters")
    print(f"  Standard deviation: {stdev_length:.1f} characters")
    print(f"  Min length: {min_length} characters")
    print(f"  Max length: {max_length} characters")
    
    print(f"\nPercentiles:")
    print(f"  25th percentile: {p25} characters")
    print(f"  50th percentile (median): {int(median_length)} characters")
    print(f"  75th percentile: {p75} characters")
    print(f"  90th percentile: {p90} characters")
    print(f"  95th percentile: {p95} characters")
    
    print(f"\nRecommendations for max_length:")
    print(f"  Conservative (95% coverage): {p95} characters")
    print(f"  Balanced (90% coverage): {p90} characters")
    print(f"  Aggressive (75% coverage): {p75} characters")
    
    # Create a simple text histogram
    print(f"\nLength Distribution (text histogram):")
    bin_size = 50
    bins = {}
    for length in lengths:
        bin_num = length // bin_size
        bins[bin_num] = bins.get(bin_num, 0) + 1
    
    max_count = max(bins.values())
    for i in range(min(bins.keys()), max(bins.keys()) + 1):
        count = bins.get(i, 0)
        bar_length = int((count / max_count) * 50)
        bar = '#' * bar_length
        print(f"  {i*bin_size:4d}-{(i+1)*bin_size-1:4d}: {bar} ({count})")

if __name__ == "__main__":
    analyze_tweet_lengths()