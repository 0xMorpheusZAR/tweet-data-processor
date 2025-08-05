"""
Fetch Last 5000 Miles Tweets for Model Improvement
Uses X API to get comprehensive data without tampering with existing model
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import logging
from typing import Dict, List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our systems
from miles_x_data_fetcher import XProAPIClient, TweetMetrics
from miles_mega_framework_top100 import MilesMegaFramework
from miles_optimal_generation_system import MilesDataAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelImprovementAnalyzer:
    """Analyzes new tweets against existing model for improvements"""
    
    def __init__(self):
        self.api_client = XProAPIClient()
        self.mega_framework = MilesMegaFramework()
        self.data_analyzer = MilesDataAnalyzer()
        
        # Load existing data for comparison
        self.existing_patterns = self._load_existing_patterns()
        self.existing_performance = self._load_existing_performance()
        
    def _load_existing_patterns(self) -> Dict:
        """Load existing pattern data"""
        try:
            with open('miles_pattern_examples.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _load_existing_performance(self) -> Dict:
        """Load existing performance metrics"""
        try:
            with open('miles_mega_framework_results.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def fetch_latest_5000_tweets(self) -> List[Dict]:
        """Fetch last 5000 tweets from Miles"""
        logger.info("Fetching last 5000 tweets from @milesdeutscher...")
        
        all_tweets = []
        pagination_token = None
        
        while len(all_tweets) < 5000:
            try:
                tweets = self.api_client.fetch_user_tweets(
                    username="milesdeutscher",
                    count=100,
                    exclude_replies=True
                )
                
                if not tweets:
                    break
                    
                all_tweets.extend(tweets)
                logger.info(f"Fetched {len(all_tweets)} tweets so far...")
                
                # Rate limit handling
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error fetching tweets: {e}")
                break
        
        logger.info(f"Total tweets fetched: {len(all_tweets)}")
        return all_tweets[:5000]  # Ensure max 5000
    
    def analyze_new_patterns(self, tweets: List[Dict]) -> Dict:
        """Analyze new tweets for pattern improvements"""
        analysis = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_analyzed": len(tweets),
            "new_patterns_discovered": {},
            "pattern_evolution": {},
            "engagement_trends": {},
            "optimization_opportunities": []
        }
        
        # Group tweets by estimated pattern
        pattern_groups = {}
        
        for tweet in tweets:
            # Analyze tweet pattern
            text = tweet.get('text', '')
            metrics = tweet.get('public_metrics', {})
            
            # Calculate engagement
            engagement = (
                metrics.get('like_count', 0) +
                metrics.get('retweet_count', 0) * 2 +
                metrics.get('reply_count', 0) * 1.5 +
                metrics.get('quote_count', 0) * 3
            )
            
            # Pattern detection
            pattern = self._detect_pattern(text)
            
            if pattern not in pattern_groups:
                pattern_groups[pattern] = []
            
            pattern_groups[pattern].append({
                'text': text,
                'engagement': engagement,
                'metrics': metrics,
                'created_at': tweet.get('created_at', '')
            })
        
        # Analyze each pattern group
        for pattern, tweets_in_pattern in pattern_groups.items():
            if len(tweets_in_pattern) < 5:  # Need minimum samples
                continue
                
            avg_engagement = sum(t['engagement'] for t in tweets_in_pattern) / len(tweets_in_pattern)
            
            # Check if this is a new high-performing pattern
            if avg_engagement > 3000 and pattern not in self.existing_patterns:
                analysis["new_patterns_discovered"][pattern] = {
                    "sample_count": len(tweets_in_pattern),
                    "avg_engagement": avg_engagement,
                    "top_example": max(tweets_in_pattern, key=lambda x: x['engagement'])
                }
            
            # Track pattern evolution
            analysis["pattern_evolution"][pattern] = {
                "current_avg_engagement": avg_engagement,
                "sample_size": len(tweets_in_pattern),
                "engagement_range": {
                    "min": min(t['engagement'] for t in tweets_in_pattern),
                    "max": max(t['engagement'] for t in tweets_in_pattern)
                }
            }
        
        # Identify optimization opportunities
        analysis["optimization_opportunities"] = self._identify_optimizations(pattern_groups)
        
        return analysis
    
    def _detect_pattern(self, text: str) -> str:
        """Detect tweet pattern type"""
        # Check against known patterns
        if "?" in text and "Think about it" in text:
            return "question_hook"
        elif "situation:" in text.lower() and "position accordingly" in text.lower():
            return "situation_framework"
        elif "reality" in text.lower() and "most will miss" in text.lower():
            return "reality_check"
        elif text.count('\n') >= 4:
            return "multi_line_structured"
        elif len(text.split()) < 15:
            return "short_take"
        else:
            # Try to match with mega framework patterns
            for pattern_name, pattern in self.mega_framework.mega_patterns.items():
                score = self._calculate_pattern_similarity(text, pattern)
                if score > 0.7:
                    return pattern_name
            
            return "unclassified"
    
    def _calculate_pattern_similarity(self, text: str, pattern) -> float:
        """Calculate how similar a tweet is to a known pattern"""
        score = 0.0
        
        # Check power phrases
        for phrase in pattern.power_phrases:
            if phrase.lower() in text.lower():
                score += 0.2
        
        # Check word count
        word_count = len(text.split())
        if pattern.optimal_word_count[0] <= word_count <= pattern.optimal_word_count[1]:
            score += 0.1
        
        # Check structure
        if hasattr(pattern, 'structure_template'):
            if '\n\n' in pattern.structure_template and '\n\n' in text:
                score += 0.1
        
        return min(score, 1.0)
    
    def _identify_optimizations(self, pattern_groups: Dict) -> List[Dict]:
        """Identify specific optimization opportunities"""
        optimizations = []
        
        # Find underperforming patterns
        for pattern, tweets in pattern_groups.items():
            if len(tweets) < 10:
                continue
                
            avg_engagement = sum(t['engagement'] for t in tweets) / len(tweets)
            
            # If pattern is underperforming compared to known benchmarks
            if pattern in self.mega_framework.mega_patterns:
                expected_engagement = self.mega_framework.mega_patterns[pattern].avg_engagement
                
                if avg_engagement < expected_engagement * 0.7:  # 30% below expected
                    optimizations.append({
                        "pattern": pattern,
                        "issue": "underperforming",
                        "current_avg": avg_engagement,
                        "expected_avg": expected_engagement,
                        "recommendation": f"Review recent {pattern} tweets for quality issues"
                    })
        
        # Find emerging patterns
        for pattern, data in pattern_groups.items():
            if pattern == "unclassified" and len(data) > 20:
                high_performers = [t for t in data if t['engagement'] > 5000]
                if len(high_performers) > 5:
                    optimizations.append({
                        "pattern": "emerging",
                        "issue": "unclassified_success",
                        "sample_count": len(high_performers),
                        "avg_engagement": sum(t['engagement'] for t in high_performers) / len(high_performers),
                        "recommendation": "Analyze these tweets for new pattern identification"
                    })
        
        return optimizations
    
    def generate_improvement_report(self, analysis: Dict) -> Dict:
        """Generate comprehensive improvement report"""
        report = {
            "report_timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "tweets_analyzed": analysis["total_analyzed"],
                "new_patterns_found": len(analysis["new_patterns_discovered"]),
                "patterns_tracked": len(analysis["pattern_evolution"]),
                "optimization_opportunities": len(analysis["optimization_opportunities"])
            },
            "key_findings": [],
            "recommended_updates": [],
            "performance_comparison": {}
        }
        
        # Key findings
        if analysis["new_patterns_discovered"]:
            report["key_findings"].append({
                "type": "new_patterns",
                "description": f"Discovered {len(analysis['new_patterns_discovered'])} new high-performing patterns",
                "details": analysis["new_patterns_discovered"]
            })
        
        # Pattern performance comparison
        for pattern, evolution in analysis["pattern_evolution"].items():
            if pattern in self.mega_framework.mega_patterns:
                current_avg = evolution["current_avg_engagement"]
                historical_avg = self.mega_framework.mega_patterns[pattern].avg_engagement
                
                performance_ratio = current_avg / historical_avg if historical_avg > 0 else 1
                
                report["performance_comparison"][pattern] = {
                    "current_performance": current_avg,
                    "historical_benchmark": historical_avg,
                    "performance_ratio": performance_ratio,
                    "trend": "improving" if performance_ratio > 1.1 else "declining" if performance_ratio < 0.9 else "stable"
                }
        
        # Recommendations
        for optimization in analysis["optimization_opportunities"]:
            report["recommended_updates"].append({
                "priority": "high" if optimization.get("issue") == "underperforming" else "medium",
                "action": optimization.get("recommendation", "Review pattern performance"),
                "details": optimization
            })
        
        return report
    
    def save_analysis_results(self, tweets: List[Dict], analysis: Dict, report: Dict):
        """Save all results without tampering with existing model"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save raw tweet data
        tweets_file = f"miles_5000_tweets_{timestamp}.json"
        with open(tweets_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "collected_at": datetime.now(timezone.utc).isoformat(),
                    "total_tweets": len(tweets),
                    "source": "X API - Live Fetch"
                },
                "tweets": tweets
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved raw tweets to {tweets_file}")
        
        # Save analysis
        analysis_file = f"miles_pattern_analysis_{timestamp}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"Saved pattern analysis to {analysis_file}")
        
        # Save improvement report
        report_file = f"miles_improvement_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Saved improvement report to {report_file}")
        
        return tweets_file, analysis_file, report_file

def main():
    """Main execution function"""
    print("=" * 60)
    print("FETCHING LAST 5000 MILES TWEETS FOR MODEL IMPROVEMENT")
    print("=" * 60)
    
    analyzer = ModelImprovementAnalyzer()
    
    try:
        # Fetch tweets
        print("\nFetching tweets from X API...")
        tweets = analyzer.fetch_latest_5000_tweets()
        
        if not tweets:
            print("No tweets fetched. Check API credentials.")
            return
        
        print(f"\nSuccessfully fetched {len(tweets)} tweets")
        
        # Analyze patterns
        print("\nAnalyzing tweet patterns...")
        analysis = analyzer.analyze_new_patterns(tweets)
        
        # Generate report
        print("\nGenerating improvement report...")
        report = analyzer.generate_improvement_report(analysis)
        
        # Save results
        print("\nSaving analysis results...")
        tweets_file, analysis_file, report_file = analyzer.save_analysis_results(
            tweets, analysis, report
        )
        
        # Display summary
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        
        print(f"\nTweets Analyzed: {len(tweets)}")
        print(f"New Patterns Discovered: {len(analysis['new_patterns_discovered'])}")
        print(f"Optimization Opportunities: {len(analysis['optimization_opportunities'])}")
        
        if analysis['new_patterns_discovered']:
            print("\nNew High-Performing Patterns:")
            for pattern, data in list(analysis['new_patterns_discovered'].items())[:3]:
                print(f"  - {pattern}: {data['avg_engagement']:.0f} avg engagement")
        
        print(f"\nFiles saved:")
        print(f"  - Raw tweets: {tweets_file}")
        print(f"  - Pattern analysis: {analysis_file}")
        print(f"  - Improvement report: {report_file}")
        
        print("\nModel improvement analysis complete!")
        print("Existing model remains unchanged - all new data saved separately.")
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise

if __name__ == "__main__":
    main()