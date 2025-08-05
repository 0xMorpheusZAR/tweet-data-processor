# X/Twitter API Integration Setup Guide

## 🔑 Prerequisites

1. **Twitter Developer Account**
   - Go to https://developer.twitter.com
   - Apply for developer access
   - Create a new App in the Developer Portal

2. **Get Your Bearer Token**
   - In your app settings, go to "Keys and tokens"
   - Generate a Bearer Token
   - Copy and save it securely

## 🚀 Quick Setup

### 1. Set Environment Variable

**Windows (Command Prompt):**
```cmd
set TWITTER_BEARER_TOKEN=your_bearer_token_here
```

**Windows (PowerShell):**
```powershell
$env:TWITTER_BEARER_TOKEN = "your_bearer_token_here"
```

**Linux/Mac:**
```bash
export TWITTER_BEARER_TOKEN="your_bearer_token_here"
```

### 2. Install Dependencies
```bash
pip install tweepy pandas python-dotenv
```

### 3. Create .env File (Recommended)
```env
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

## 📊 Using the API Integration

### Basic Usage
```python
from twitter_api_integration import TwitterAPIClient, TwitterDataEnhancer

# Initialize API client
api = TwitterAPIClient()

# Fetch recent tweets
recent_tweets = api.fetch_recent_tweets(max_results=50)

# Get high-engagement tweets
high_performers = api.fetch_high_engagement_tweets(days=30)
```

### Enhance Training Data
```python
# Create data enhancer
enhancer = TwitterDataEnhancer(api)

# Update your training dataset with fresh tweets
enhanced_dataset = enhancer.update_training_data('data.jsonl')

# Analyze style evolution
style_analysis = enhancer.analyze_style_evolution()
```

## 🔄 Continuous Learning Pipeline

### Automated Data Collection
```python
import schedule
import time

def update_training_data():
    """Run daily to collect new high-performing tweets"""
    try:
        api = TwitterAPIClient()
        enhancer = TwitterDataEnhancer(api)
        
        # Fetch and add new tweets
        enhanced_path = enhancer.update_training_data()
        
        # Re-process for fine-tuning
        process_tweets_for_training(enhanced_path)
        
        print(f"Training data updated: {datetime.now()}")
    except Exception as e:
        print(f"Error updating data: {e}")

# Schedule daily updates
schedule.every().day.at("02:00").do(update_training_data)

# Keep running
while True:
    schedule.run_pending()
    time.sleep(60)
```

## 📈 Benefits of API Integration

### 1. **Real-Time Style Learning**
- Captures Miles's latest tweets automatically
- Adapts to evolving writing patterns
- Learns from high-engagement content

### 2. **Enhanced Training Data**
- Adds engagement metrics to training examples
- Filters for quality content (high engagement)
- Provides style feature extraction

### 3. **Continuous Improvement**
- Daily updates keep model current
- Tracks style evolution over time
- Identifies trending patterns

## 🎯 API Data Features

### Tweet Metrics Collected:
- **Engagement**: Likes, retweets, replies, quotes
- **Reach**: Impressions (if available)
- **Structure**: Line count, length, formatting
- **Style**: Opening patterns, phrases, structure type

### Style Features Extracted:
```json
{
  "length": 164,
  "line_count": 3,
  "has_question": false,
  "has_ticker": true,
  "structure": "three_part",
  "opening_style": "statement",
  "uses_miles_phrases": ["just noise", "what matters", "until then"]
}
```

## 🛡️ Rate Limits

Twitter API v2 Rate Limits:
- **Recent tweets**: 75 requests per 15 minutes
- **User lookup**: 300 requests per 15 minutes

The integration handles rate limits automatically with built-in delays.

## 🔧 Troubleshooting

### "Bearer token not found"
- Ensure environment variable is set correctly
- Check .env file is in the project root
- Verify token hasn't expired

### "User not found" 
- Check internet connection
- Verify API access level (Essential/Elevated)

### "No tweets returned"
- Miles may not have tweeted recently
- Check exclude filters (retweets/replies)

## 📊 Monitoring Performance

Track model improvements:
```python
# Before API enhancement
baseline_performance = test_model_accuracy('data.jsonl')

# After API enhancement  
enhanced_performance = test_model_accuracy('data_enhanced.jsonl')

improvement = enhanced_performance - baseline_performance
print(f"Performance improvement: {improvement:.2%}")
```

---

With X/Twitter API integration, your Miles AI will continuously learn and improve from real-time data! 🚀