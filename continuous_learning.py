"""
Continuous Learning System for Miles Deutscher AI
Automatically improves model with fresh Twitter data
"""

import os
import json
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from twitter_api_integration import TwitterAPIClient, TwitterDataEnhancer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('continuous_learning.log'),
        logging.StreamHandler()
    ]
)

class ContinuousLearningPipeline:
    """
    Manages continuous learning from Twitter API data
    """
    
    def __init__(self, api_token: Optional[str] = None):
        self.api = TwitterAPIClient(bearer_token=api_token)
        self.enhancer = TwitterDataEnhancer(self.api)
        self.metrics_history = []
        
    def daily_update(self) -> Dict:
        """
        Daily update routine:
        1. Fetch new high-engagement tweets
        2. Analyze style trends
        3. Update training data
        4. Track performance metrics
        """
        
        logging.info("Starting daily update...")
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'new_tweets': 0,
            'style_insights': {},
            'errors': []
        }
        
        try:
            # 1. Fetch fresh high-engagement tweets
            logging.info("Fetching high-engagement tweets...")
            high_performers = self.api.fetch_high_engagement_tweets(
                days=7,  # Look at past week
                min_engagement_rate=0.05
            )
            
            results['new_tweets'] = len(high_performers)
            logging.info(f"Found {len(high_performers)} high-engagement tweets")
            
            # 2. Analyze current style trends
            logging.info("Analyzing style trends...")
            style_analysis = self.enhancer.analyze_style_evolution()
            results['style_insights'] = style_analysis
            
            # 3. Update training data
            logging.info("Updating training data...")
            enhanced_path = self.enhancer.update_training_data()
            
            # 4. Generate style report
            self._generate_style_report(style_analysis, high_performers)
            
            # 5. Update baseline style if significant changes detected
            if self._detect_style_shift(style_analysis):
                self._update_baseline_style(high_performers)
                results['baseline_updated'] = True
            
        except Exception as e:
            logging.error(f"Error in daily update: {e}")
            results['errors'].append(str(e))
        
        # Save metrics
        self.metrics_history.append(results)
        self._save_metrics()
        
        return results
    
    def _generate_style_report(self, analysis: Dict, tweets: List[Dict]) -> None:
        """Generate a report on current style trends"""
        
        report = {
            'date': datetime.utcnow().isoformat(),
            'summary': {
                'total_tweets_analyzed': len(tweets),
                'avg_engagement_rate': sum(t['engagement_rate'] for t in tweets) / len(tweets) if tweets else 0,
                'trending_structures': analysis.get('popular_structures', {}),
                'top_phrases': analysis.get('vocabulary_shifts', {}).get('top_phrases', [])
            },
            'insights': []
        }
        
        # Generate insights
        trends = analysis.get('current_trends', {})
        
        # Length trend
        avg_length = trends.get('avg_length', 0)
        if avg_length < 100:
            report['insights'].append("Trend: Shorter, punchier tweets performing well")
        elif avg_length > 200:
            report['insights'].append("Trend: Longer, detailed analysis gaining traction")
        
        # Question ratio
        question_ratio = trends.get('question_ratio', 0)
        if question_ratio > 0.3:
            report['insights'].append("Trend: Questions driving high engagement")
        
        # Structure preferences
        structures = analysis.get('popular_structures', {})
        if structures.get('three_part', 0) > 40:
            report['insights'].append("Trend: Three-part structure dominating (Option 5 baseline validated)")
        
        # Save report
        with open('style_report_latest.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logging.info("Style report generated: style_report_latest.json")
    
    def _detect_style_shift(self, analysis: Dict) -> bool:
        """Detect if Miles's style has significantly shifted"""
        
        # Check if three-part structure is still dominant
        structures = analysis.get('popular_structures', {})
        three_part_ratio = structures.get('three_part', 0)
        
        # Check if average length has changed significantly
        trends = analysis.get('current_trends', {})
        avg_length = trends.get('avg_length', 0)
        
        # Detect shift
        shift_detected = False
        
        if three_part_ratio < 30:  # Less than 30% three-part
            logging.warning("Style shift detected: Three-part structure declining")
            shift_detected = True
        
        if avg_length > 250 or avg_length < 80:
            logging.warning(f"Style shift detected: Average length {avg_length}")
            shift_detected = True
        
        return shift_detected
    
    def _update_baseline_style(self, tweets: List[Dict]) -> None:
        """Update baseline style template based on new patterns"""
        
        logging.info("Updating baseline style template...")
        
        # Find most successful recent tweets
        top_tweets = sorted(tweets, key=lambda x: x['total_engagement'], reverse=True)[:5]
        
        # Extract new patterns
        new_patterns = {
            'structures': [],
            'openings': [],
            'phrases': []
        }
        
        for tweet in top_tweets:
            text = tweet['text']
            lines = text.split('\n')
            
            # Analyze structure
            if len(lines) == 3:
                new_patterns['structures'].append({
                    'line1': lines[0][:30] + "...",
                    'line2': lines[1][:30] + "...",
                    'line3': lines[2][:30] + "..."
                })
            
            # Extract opening
            opening_words = text.split()[:3]
            new_patterns['openings'].append(' '.join(opening_words))
            
            # Extract key phrases
            features = tweet.get('style_features', {})
            phrases = features.get('uses_miles_phrases', [])
            new_patterns['phrases'].extend(phrases)
        
        # Save updated patterns
        with open('baseline_style_update.json', 'w') as f:
            json.dump({
                'updated_at': datetime.utcnow().isoformat(),
                'new_patterns': new_patterns,
                'top_examples': [t['text'] for t in top_tweets]
            }, f, indent=2)
        
        logging.info("Baseline style updated: baseline_style_update.json")
    
    def _save_metrics(self) -> None:
        """Save metrics history"""
        
        with open('learning_metrics.json', 'w') as f:
            json.dump(self.metrics_history[-100:], f, indent=2)  # Keep last 100 entries
    
    def run_continuous_learning(self) -> None:
        """Run continuous learning loop"""
        
        logging.info("Starting continuous learning pipeline...")
        
        # Schedule daily updates at 2 AM
        schedule.every().day.at("02:00").do(self.daily_update)
        
        # Also run immediately on start
        self.daily_update()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

class RealTimeStyleAdapter:
    """
    Adapts generation style based on recent performance data
    """
    
    def __init__(self):
        self.performance_cache = {}
        self.load_recent_insights()
    
    def load_recent_insights(self) -> None:
        """Load recent style insights"""
        
        try:
            with open('style_report_latest.json', 'r') as f:
                self.latest_report = json.load(f)
        except:
            self.latest_report = {}
    
    def adapt_generation_params(self, base_params: Dict) -> Dict:
        """
        Adapt generation parameters based on recent insights
        """
        
        adapted = base_params.copy()
        
        if not self.latest_report:
            return adapted
        
        insights = self.latest_report.get('insights', [])
        
        # Adapt based on insights
        for insight in insights:
            if "Shorter, punchier" in insight:
                adapted['max_tokens'] = min(adapted.get('max_tokens', 280), 150)
                adapted['length_penalty'] = 0.6  # Prefer shorter
                
            elif "Longer, detailed" in insight:
                adapted['max_tokens'] = 280
                adapted['length_penalty'] = 1.2  # Allow longer
                
            elif "Questions driving" in insight:
                adapted['question_probability'] = 0.4  # Increase question generation
        
        # Adapt temperature based on engagement trends
        summary = self.latest_report.get('summary', {})
        avg_engagement = summary.get('avg_engagement_rate', 0.03)
        
        if avg_engagement > 0.05:  # High engagement
            # Keep what's working
            adapted['temperature'] = 0.8
        else:
            # Try more variety
            adapted['temperature'] = 0.9
        
        return adapted
    
    def get_trending_patterns(self) -> Dict:
        """Get current trending patterns"""
        
        if not self.latest_report:
            return {}
        
        return {
            'structures': self.latest_report.get('summary', {}).get('trending_structures', {}),
            'phrases': self.latest_report.get('summary', {}).get('top_phrases', []),
            'insights': self.latest_report.get('insights', [])
        }

# Usage example
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║      Continuous Learning Pipeline for Miles AI       ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    print("\nOptions:")
    print("1. Run one-time update")
    print("2. Start continuous learning (runs daily)")
    print("3. View latest style report")
    
    # For testing - run one update
    print("\nRunning one-time update...")
    
    # Note: Requires TWITTER_BEARER_TOKEN to be set
    # pipeline = ContinuousLearningPipeline()
    # results = pipeline.daily_update()
    # print(f"\nUpdate complete: {results['new_tweets']} new tweets added")
    
    print("\nTo start continuous learning:")
    print("python continuous_learning.py --continuous")