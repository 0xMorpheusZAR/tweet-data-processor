"""
Production Data Pipeline for Miles AI
Integrates with X Pro API for continuous learning and optimization
"""
import asyncio
import json
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import requests
import pandas as pd
from dataclasses import dataclass, asdict
from collections import defaultdict
import hashlib

# Import our systems
from config.credentials import credential_manager
from miles_optimal_generation_system import ProductionOptimizedSystem, MilesDataAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TweetMetrics:
    """Comprehensive tweet metrics for optimization"""
    tweet_id: str
    text: str
    created_at: str
    public_metrics: Dict[str, int]
    engagement_rate: float
    viral_score: float
    quality_score: float
    pattern_type: str
    optimization_features: Dict[str, Any]

class XProAPIClient:
    """Enhanced X Pro API client for Miles data collection"""
    
    def __init__(self):
        self.credentials = credential_manager.credentials
        self.base_url = "https://api.twitter.com/2"
        self.headers = self.credentials.get_headers()
        self.rate_limits = {
            "user_tweets": {"remaining": 300, "reset": 0},
            "tweet_lookup": {"remaining": 300, "reset": 0}
        }
        
    def _handle_rate_limit(self, endpoint: str):
        """Handle rate limiting"""
        if endpoint in self.rate_limits:
            limit_info = self.rate_limits[endpoint]
            if limit_info["remaining"] <= 1:
                sleep_time = max(0, limit_info["reset"] - time.time())
                if sleep_time > 0:
                    logger.info(f"Rate limit reached for {endpoint}. Sleeping {sleep_time:.0f}s")
                    time.sleep(sleep_time + 1)
    
    def _update_rate_limits(self, response: requests.Response, endpoint: str):
        """Update rate limit tracking"""
        remaining = response.headers.get('x-rate-limit-remaining')
        reset = response.headers.get('x-rate-limit-reset')
        
        if remaining and reset:
            self.rate_limits[endpoint] = {
                "remaining": int(remaining),
                "reset": int(reset)
            }
    
    def fetch_user_tweets(self, 
                         username: str = "milesdeutscher",
                         count: int = 100,
                         exclude_replies: bool = True) -> List[Dict]:
        """Fetch tweets from Miles Deutscher with comprehensive metrics"""
        
        # Get user ID first
        user_url = f"{self.base_url}/users/by/username/{username}"
        user_response = requests.get(user_url, headers=self.headers)
        
        if user_response.status_code != 200:
            raise Exception(f"Failed to get user ID: {user_response.text}")
        
        user_id = user_response.json()["data"]["id"]
        
        # Fetch tweets
        self._handle_rate_limit("user_tweets")
        
        tweets_url = f"{self.base_url}/users/{user_id}/tweets"
        params = {
            "max_results": min(count, 100),
            "tweet.fields": ",".join([
                "id", "text", "created_at", "author_id", "conversation_id",
                "public_metrics", "context_annotations", "entities",
                "lang", "possibly_sensitive", "referenced_tweets"
            ]),
            "expansions": "referenced_tweets.id",
            "exclude": "replies" if exclude_replies else ""
        }
        
        response = requests.get(tweets_url, headers=self.headers, params=params)
        self._update_rate_limits(response, "user_tweets")
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch tweets: {response.text}")
        
        return response.json().get("data", [])
    
    def get_tweet_details(self, tweet_ids: List[str]) -> Dict[str, Dict]:
        """Get detailed metrics for specific tweets"""
        if not tweet_ids:
            return {}
        
        self._handle_rate_limit("tweet_lookup")
        
        # Batch tweet lookup
        ids_str = ",".join(tweet_ids[:100])  # API limit
        url = f"{self.base_url}/tweets"
        params = {
            "ids": ids_str,
            "tweet.fields": ",".join([
                "public_metrics", "created_at", "context_annotations",
                "entities", "lang", "referenced_tweets"
            ])
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        self._update_rate_limits(response, "tweet_lookup")
        
        if response.status_code != 200:
            logger.error(f"Failed to get tweet details: {response.text}")
            return {}
        
        data = response.json().get("data", [])
        return {tweet["id"]: tweet for tweet in data}

class ContinuousLearningEngine:
    """Engine for continuous learning and model improvement"""
    
    def __init__(self, api_client: XProAPIClient):
        self.api_client = api_client
        self.analyzer = MilesDataAnalyzer()
        self.learning_data = []
        self.performance_trends = defaultdict(list)
        
    def collect_fresh_data(self, hours_back: int = 24) -> List[TweetMetrics]:
        """Collect fresh tweet data for learning"""
        logger.info(f"Collecting tweets from last {hours_back} hours...")
        
        # Fetch recent tweets
        tweets = self.api_client.fetch_user_tweets(count=100)
        
        # Filter by time
        cutoff_time = datetime.now(timezone.utc).timestamp() - (hours_back * 3600)
        recent_tweets = []
        
        for tweet in tweets:
            created_at = datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00"))
            if created_at.timestamp() > cutoff_time:
                recent_tweets.append(tweet)
        
        # Convert to TweetMetrics
        metrics_list = []
        for tweet in recent_tweets:
            metrics = self._analyze_tweet_performance(tweet)
            if metrics:
                metrics_list.append(metrics)
        
        logger.info(f"Collected {len(metrics_list)} recent tweets for analysis")
        return metrics_list
    
    def _analyze_tweet_performance(self, tweet: Dict) -> Optional[TweetMetrics]:
        """Analyze individual tweet performance"""
        try:
            text = tweet.get("text", "")
            public_metrics = tweet.get("public_metrics", {})
            
            if not text or not public_metrics:
                return None
            
            # Calculate engagement metrics
            likes = public_metrics.get("like_count", 0)
            retweets = public_metrics.get("retweet_count", 0)
            replies = public_metrics.get("reply_count", 0)
            quotes = public_metrics.get("quote_count", 0)
            impressions = public_metrics.get("impression_count", 0)
            
            # Engagement rate calculation
            total_engagement = likes + retweets + replies + quotes
            engagement_rate = total_engagement / impressions if impressions > 0 else 0
            
            # Viral score (normalized)
            viral_score = min((total_engagement / 10000), 1.0)
            
            # Pattern analysis
            pattern_analysis = self.analyzer.analyze_tweet(text) if hasattr(self.analyzer, 'analyze_tweet') else {}
            pattern_type = pattern_analysis.get("pattern_type", "unknown")
            
            # Quality score estimation
            quality_score = self._estimate_quality_score(text, public_metrics)
            
            # Optimization features
            optimization_features = {
                "word_count": len(text.split()),
                "char_count": len(text),
                "has_emoji": bool(re.search(r'[\U0001F300-\U0001F9FF]', text)),
                "has_numbers": bool(re.search(r'\d', text)),
                "has_question": text.strip().endswith("?"),
                "has_hashtags": bool(re.search(r'#\w+', text)),
                "mentions_count": len(re.findall(r'@\w+', text)),
                "url_count": len(re.findall(r'http[s]?://\S+', text))
            }
            
            return TweetMetrics(
                tweet_id=tweet["id"],
                text=text,
                created_at=tweet["created_at"],
                public_metrics=public_metrics,
                engagement_rate=engagement_rate,
                viral_score=viral_score,
                quality_score=quality_score,
                pattern_type=pattern_type,
                optimization_features=optimization_features
            )
            
        except Exception as e:
            logger.error(f"Error analyzing tweet: {e}")
            return None
    
    def _estimate_quality_score(self, text: str, metrics: Dict) -> float:
        """Estimate quality score based on performance"""
        base_score = 0.5
        
        # Engagement-based scoring
        total_engagement = sum(metrics.get(key, 0) for key in 
                             ["like_count", "retweet_count", "reply_count", "quote_count"])
        
        if total_engagement > 1000:
            base_score += 0.3
        elif total_engagement > 100:
            base_score += 0.2
        elif total_engagement > 10:
            base_score += 0.1
        
        # Content quality indicators
        if any(phrase in text.lower() for phrase in ["accordingly", "situation", "position"]):
            base_score += 0.1
        
        if re.search(r'\d+\.', text):  # Numbered lists
            base_score += 0.05
        
        if len(text.split()) > 15:  # Substantial content
            base_score += 0.05
        
        return min(base_score, 1.0)
    
    def update_optimization_weights(self, metrics_data: List[TweetMetrics]):
        """Update optimization weights based on performance data"""
        logger.info("Updating optimization weights based on performance...")
        
        # Analyze what features correlate with high performance
        feature_performance = defaultdict(list)
        
        for metric in metrics_data:
            for feature, value in metric.optimization_features.items():
                feature_performance[feature].append({
                    "value": value,
                    "engagement": metric.engagement_rate,
                    "viral_score": metric.viral_score
                })
        
        # Calculate correlations and update weights
        optimization_insights = {}
        
        for feature, data_points in feature_performance.items():
            if len(data_points) < 5:  # Need minimum data
                continue
            
            # Simple correlation analysis
            values = [dp["value"] for dp in data_points]
            engagements = [dp["engagement"] for dp in data_points]
            
            if all(isinstance(v, (int, float)) for v in values):
                correlation = self._calculate_correlation(values, engagements)
                optimization_insights[feature] = {
                    "correlation": correlation,
                    "avg_performance": sum(engagements) / len(engagements),
                    "sample_size": len(data_points)
                }
        
        # Save insights
        self._save_optimization_insights(optimization_insights)
        
        return optimization_insights
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Simple correlation calculation"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y[i] ** 2 for i in range(n))
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _save_optimization_insights(self, insights: Dict):
        """Save optimization insights to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"optimization_insights_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.utcnow().isoformat(),
                "insights": insights,
                "recommendations": self._generate_recommendations(insights)
            }, f, indent=2)
        
        logger.info(f"Optimization insights saved to {filename}")
    
    def _generate_recommendations(self, insights: Dict) -> Dict[str, str]:
        """Generate optimization recommendations"""
        recommendations = {}
        
        for feature, data in insights.items():
            correlation = data["correlation"]
            
            if abs(correlation) > 0.3:  # Significant correlation
                if correlation > 0:
                    recommendations[feature] = f"Increase {feature} (positive correlation: {correlation:.3f})"
                else:
                    recommendations[feature] = f"Decrease {feature} (negative correlation: {correlation:.3f})"
        
        return recommendations

class ProductionPipeline:
    """Main production pipeline integrating all components"""
    
    def __init__(self):
        logger.info("Initializing Production Pipeline...")
        
        self.api_client = XProAPIClient()
        self.learning_engine = ContinuousLearningEngine(self.api_client)
        self.generation_system = ProductionOptimizedSystem()
        
        # Pipeline configuration
        self.config = {
            "learning_interval_hours": 6,
            "min_data_points": 10,
            "quality_threshold": 0.90,
            "continuous_learning": True
        }
        
        logger.info("Production Pipeline initialized successfully!")
    
    async def run_continuous_optimization(self):
        """Run continuous optimization loop"""
        logger.info("Starting continuous optimization...")
        
        while self.config["continuous_learning"]:
            try:
                # Collect fresh data
                fresh_metrics = self.learning_engine.collect_fresh_data(
                    hours_back=self.config["learning_interval_hours"]
                )
                
                if len(fresh_metrics) >= self.config["min_data_points"]:
                    # Update optimization weights
                    insights = self.learning_engine.update_optimization_weights(fresh_metrics)
                    logger.info(f"Updated optimization weights based on {len(fresh_metrics)} tweets")
                    
                    # Generate optimization report
                    self._generate_optimization_report(fresh_metrics, insights)
                
                # Sleep until next optimization cycle
                sleep_duration = self.config["learning_interval_hours"] * 3600
                logger.info(f"Sleeping for {sleep_duration/3600:.1f} hours until next optimization...")
                await asyncio.sleep(sleep_duration)
                
            except Exception as e:
                logger.error(f"Error in continuous optimization: {e}")
                await asyncio.sleep(3600)  # Sleep 1 hour on error
    
    def _generate_optimization_report(self, metrics: List[TweetMetrics], insights: Dict):
        """Generate comprehensive optimization report"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "data_summary": {
                "total_tweets_analyzed": len(metrics),
                "avg_engagement_rate": sum(m.engagement_rate for m in metrics) / len(metrics),
                "avg_viral_score": sum(m.viral_score for m in metrics) / len(metrics),
                "pattern_distribution": defaultdict(int)
            },
            "performance_insights": insights,
            "top_performing_tweets": [],
            "optimization_recommendations": []
        }
        
        # Pattern distribution
        for metric in metrics:
            report["data_summary"]["pattern_distribution"][metric.pattern_type] += 1
        
        # Top performing tweets
        sorted_metrics = sorted(metrics, key=lambda m: m.viral_score, reverse=True)[:5]
        for metric in sorted_metrics:
            report["top_performing_tweets"].append({
                "text": metric.text[:100] + "..." if len(metric.text) > 100 else metric.text,
                "viral_score": metric.viral_score,
                "engagement_rate": metric.engagement_rate,
                "pattern_type": metric.pattern_type
            })
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"optimization_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Optimization report saved to {filename}")
    
    def generate_optimized_tweet(self, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate tweet with latest optimizations"""
        return self.generation_system.generate_tweet(
            context=context,
            quality_threshold=self.config["quality_threshold"]
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "pipeline_status": "running",
            "generation_system": self.generation_system.get_performance_metrics(),
            "api_rate_limits": self.api_client.rate_limits,
            "config": self.config,
            "last_update": datetime.utcnow().isoformat()
        }

def main():
    """Main execution function"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║              Production Data Pipeline v1.0               ║
    ║        Continuous Learning & Optimization System         ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    pipeline = ProductionPipeline()
    
    # Test data collection
    print("\\n=== Testing Data Collection ===")
    
    try:
        fresh_metrics = pipeline.learning_engine.collect_fresh_data(hours_back=72)
        print(f"✓ Collected {len(fresh_metrics)} tweets for analysis")
        
        if fresh_metrics:
            avg_engagement = sum(m.engagement_rate for m in fresh_metrics) / len(fresh_metrics)
            avg_viral = sum(m.viral_score for m in fresh_metrics) / len(fresh_metrics)
            
            print(f"✓ Average engagement rate: {avg_engagement:.4f}")
            print(f"✓ Average viral score: {avg_viral:.4f}")
            
            # Update optimization weights
            insights = pipeline.learning_engine.update_optimization_weights(fresh_metrics)
            print(f"✓ Generated {len(insights)} optimization insights")
    
    except Exception as e:
        logger.error(f"Data collection test failed: {e}")
    
    # Test tweet generation
    print("\\n=== Testing Optimized Generation ===")
    
    test_contexts = [
        {"topic": "Bitcoin", "target_engagement": "high"},
        {"topic": "market analysis", "content_type": "educational"},
        {"topic": "DeFi", "urgency": "breaking"}
    ]
    
    for context in test_contexts:
        try:
            result = pipeline.generate_optimized_tweet(context)
            print(f"\\nContext: {context}")
            print(f"Generated: {result['tweet']}")
            print(f"Quality: {result['quality_score']:.3f}")
            print(f"Pattern: {result['pattern']}")
        except Exception as e:
            logger.error(f"Generation test failed: {e}")
    
    # System status
    print("\\n=== System Status ===")
    status = pipeline.get_system_status()
    print(json.dumps(status, indent=2, default=str))
    
    print("\\n=== Ready for Production ===")
    print("Pipeline is ready for continuous optimization.")
    print("Run with '--continuous' flag for 24/7 operation.")

if __name__ == "__main__":
    import sys
    
    if "--continuous" in sys.argv:
        pipeline = ProductionPipeline()
        asyncio.run(pipeline.run_continuous_optimization())
    else:
        main()