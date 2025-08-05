"""
Test Twitter API Connection and Fetch Miles's Latest Tweets
"""

import os
from dotenv import load_dotenv
from twitter_api_integration import TwitterAPIClient, TwitterDataEnhancer
import json

# Load environment variables
load_dotenv()

def test_api_connection():
    """Test the Twitter API connection with your credentials"""
    
    print("🔌 Testing Twitter API Connection...")
    print("="*60)
    
    try:
        # Initialize API client
        api = TwitterAPIClient()
        print("✅ API Client initialized successfully")
        
        # Test 1: Get Miles's user info
        print("\n📍 Fetching Miles Deutscher's Twitter profile...")
        user_id = api.get_user_id()
        print(f"✅ User ID: {user_id}")
        
        # Test 2: Fetch recent tweets
        print("\n📝 Fetching recent tweets...")
        recent_tweets = api.fetch_recent_tweets(max_results=5)
        
        if recent_tweets:
            print(f"✅ Successfully fetched {len(recent_tweets)} tweets")
            
            # Display sample tweet
            print("\n📊 Sample Tweet Analysis:")
            print("-"*60)
            tweet = recent_tweets[0]
            print(f"Text: {tweet['text'][:100]}...")
            print(f"Engagement Rate: {tweet['engagement_rate']:.2%}")
            print(f"Metrics: {tweet['metrics']}")
            print(f"Style: {tweet['style_features']['structure']}")
            
        # Test 3: Fetch high-engagement tweets
        print("\n🔥 Fetching high-engagement tweets from last 7 days...")
        high_performers = api.fetch_high_engagement_tweets(days=7, min_engagement_rate=0.03)
        
        if high_performers:
            print(f"✅ Found {len(high_performers)} high-engagement tweets")
            
            # Show top performer
            if high_performers:
                top_tweet = high_performers[0]
                print("\n🏆 Top Performing Tweet:")
                print("-"*60)
                print(f"Text: {top_tweet['text']}")
                print(f"Engagement Rate: {top_tweet['engagement_rate']:.2%}")
                print(f"Total Engagement: {top_tweet['total_engagement']}")
        
        # Test 4: Style Analysis
        print("\n🎨 Running style analysis...")
        enhancer = TwitterDataEnhancer(api)
        style_analysis = enhancer.analyze_style_evolution()
        
        print("\n📈 Current Style Trends:")
        print(f"Average Tweet Length: {style_analysis['current_trends']['avg_length']:.0f} chars")
        print(f"Question Ratio: {style_analysis['current_trends']['question_ratio']:.1%}")
        print(f"Contains Tickers: {style_analysis['current_trends']['ticker_ratio']:.1%}")
        
        print("\n📊 Popular Structures:")
        for structure, percentage in style_analysis['popular_structures'].items():
            print(f"  {structure}: {percentage:.1f}%")
        
        print("\n✅ All API tests passed successfully!")
        print("\nYour Twitter API integration is working correctly.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify your API credentials in .env file")
        print("3. Ensure your Twitter Developer account has proper access")
        return False

def quick_fetch_latest():
    """Quick function to fetch and display latest tweets"""
    
    api = TwitterAPIClient()
    tweets = api.fetch_recent_tweets(max_results=3)
    
    print("\n🐦 Latest Tweets from @milesdeutscher:")
    print("="*60)
    
    for i, tweet in enumerate(tweets, 1):
        print(f"\nTweet {i}:")
        print(tweet['text'])
        print(f"Engagement: {tweet['engagement_rate']:.2%} | Likes: {tweet['metrics']['likes']}")
        print("-"*60)

if __name__ == "__main__":
    # Test the connection
    if test_api_connection():
        # If successful, show latest tweets
        quick_fetch_latest()
        
        print("\n💡 Next Steps:")
        print("1. Run 'python continuous_learning.py' to start collecting data")
        print("2. Use 'python twitter_api_integration.py' to enhance your dataset")
        print("3. The system will now continuously learn from Miles's tweets!"