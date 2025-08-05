import json
import sys

# Set UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

def extract_tweet_examples():
    # Read tweets from tweets.js
    with open('tweets.js', 'r', encoding='utf-8') as f:
        content = f.read()
        start_idx = content.find('[')
        tweet_objects = json.loads(content[start_idx:])
    
    # Categories for organizing tweets
    categories = {
        'market_analysis': [],
        'trading_insights': [],
        'crypto_commentary': [],
        'personal_thoughts': [],
        'educational': []
    }
    
    # Extract tweets
    all_tweets = []
    for tweet_obj in tweet_objects:
        if 'tweet' in tweet_obj and 'full_text' in tweet_obj['tweet']:
            full_text = tweet_obj['tweet']['full_text']
            # Skip replies and retweets
            if not full_text.startswith('@') and not full_text.startswith('RT'):
                all_tweets.append(full_text)
    
    print("=== MILES DEUTSCHER TWEET EXAMPLES ===\n")
    print(f"Total original tweets: {len(all_tweets)}\n")
    
    # Show diverse examples
    print("## MARKET ANALYSIS & TRADING")
    print("-" * 80)
    market_keywords = ['$BTC', '$ETH', 'bitcoin', 'chart', 'price', 'market', 'bull', 'bear', 'alt season']
    for tweet in all_tweets[:100]:
        if any(keyword.lower() in tweet.lower() for keyword in market_keywords):
            print(f"• {tweet}")
            print()
            categories['market_analysis'].append(tweet)
            if len(categories['market_analysis']) >= 5:
                break
    
    print("\n## CRYPTO INSIGHTS & COMMENTARY")
    print("-" * 80)
    crypto_keywords = ['defi', 'nft', 'protocol', 'yield', 'stake', 'liquidity', 'airdrop']
    count = 0
    for tweet in all_tweets:
        if any(keyword.lower() in tweet.lower() for keyword in crypto_keywords) and tweet not in categories['market_analysis']:
            print(f"• {tweet}")
            print()
            count += 1
            if count >= 5:
                break
    
    print("\n## GENERAL TWEETS & THOUGHTS")
    print("-" * 80)
    count = 0
    for tweet in all_tweets[10:]:
        if len(tweet) > 50 and tweet not in categories['market_analysis']:
            print(f"• {tweet}")
            print()
            count += 1
            if count >= 5:
                break
    
    # Show tweet characteristics
    print("\n## TWEET CHARACTERISTICS")
    print("-" * 80)
    lengths = [len(t) for t in all_tweets]
    print(f"Average length: {sum(lengths)/len(lengths):.0f} characters")
    print(f"Shortest tweet: {min(lengths)} characters")
    print(f"Longest tweet: {max(lengths)} characters")
    
    # Common patterns
    print("\nCommon patterns:")
    print(f"- Uses links: {sum(1 for t in all_tweets if 'https://t.co' in t)} tweets")
    print(f"- Uses hashtags: {sum(1 for t in all_tweets if '#' in t)} tweets")
    print(f"- Uses dollar signs (tickers): {sum(1 for t in all_tweets if '$' in t)} tweets")
    print(f"- Question tweets: {sum(1 for t in all_tweets if '?' in t)} tweets")
    print(f"- Exclamation tweets: {sum(1 for t in all_tweets if '!' in t)} tweets")

if __name__ == "__main__":
    extract_tweet_examples()