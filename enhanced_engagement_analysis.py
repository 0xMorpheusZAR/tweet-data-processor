#!/usr/bin/env python3
"""
Enhanced Tweet Engagement Analysis
Deep dive analysis with time patterns, emoji usage, CTA effectiveness, and controversial content analysis.
"""

import json
import os
import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Any, Tuple
import statistics

class EnhancedTweetAnalyzer:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.all_tweets = []
        self.top_100_tweets = []
        
    def load_and_process_all_data(self):
        """Load and process all JSON files comprehensively"""
        json_files = [
            'miles_pattern_examples.json',
            'miles_final_data_model.json', 
            'miles_5000_tweets_structured.json',
            'miles_tweets_live.json',
            'miles_final_model_with_live.json'
        ]
        
        for filename in json_files:
            file_path = os.path.join(self.base_dir, filename)
            if os.path.exists(file_path):
                try:
                    print(f"Processing {filename}...")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.extract_tweets_from_data(data, filename)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    
    def extract_tweets_from_data(self, data: Any, source_file: str):
        """Extract all tweets from various data structures"""
        def process_tweet_obj(tweet_obj, context=""):
            if isinstance(tweet_obj, dict) and 'text' in tweet_obj:
                metrics = tweet_obj.get('metrics', {})
                engagement = self.calculate_engagement_score(metrics)
                
                enhanced_tweet = {
                    'text': tweet_obj['text'],
                    'engagement_score': engagement,
                    'metrics': metrics,
                    'source_file': source_file,
                    'context': context,
                    'quality_score': tweet_obj.get('quality_score', 0),
                    'created_at': tweet_obj.get('created_at', tweet_obj.get('timestamp', '')),
                    'word_count': len(tweet_obj['text'].split()),
                    'character_count': len(tweet_obj['text']),
                    'hashtag_count': len(re.findall(r'#\w+', tweet_obj['text'])),
                    'mention_count': len(re.findall(r'@\w+', tweet_obj['text'])),
                    'url_count': len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet_obj['text'])),
                    'emoji_count': len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', tweet_obj['text'])),
                    'question_marks': tweet_obj['text'].count('?'),
                    'exclamation_marks': tweet_obj['text'].count('!'),
                    'line_breaks': tweet_obj['text'].count('\n'),
                    'has_ellipsis': '...' in tweet_obj['text'],
                    'has_caps_words': bool(re.search(r'\b[A-Z]{2,}\b', tweet_obj['text'])),
                    'has_numbers': bool(re.search(r'\d', tweet_obj['text'])),
                    'sentiment_words': self.count_sentiment_words(tweet_obj['text']),
                    'power_words': self.count_power_words(tweet_obj['text']),
                }
                
                self.all_tweets.append(enhanced_tweet)
        
        # Recursively extract tweets from nested structures
        def extract_recursive(obj, context=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == 'text' and isinstance(obj, dict):
                        process_tweet_obj(obj, f"{context}_{key}" if context else key)
                    elif isinstance(value, (dict, list)):
                        extract_recursive(value, f"{context}_{key}" if context else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, dict) and 'text' in item:
                        process_tweet_obj(item, f"{context}[{i}]" if context else f"item_{i}")
                    elif isinstance(item, (dict, list)):
                        extract_recursive(item, f"{context}[{i}]" if context else f"item_{i}")
        
        extract_recursive(data)
        
    def calculate_engagement_score(self, metrics: Dict) -> float:
        """Enhanced engagement score calculation"""
        if not metrics:
            return 0
            
        likes = metrics.get('likes', 0)
        retweets = metrics.get('retweets', 0) 
        replies = metrics.get('replies', 0)
        quotes = metrics.get('quotes', 0)
        impressions = metrics.get('impressions', 0)
        
        # Weighted engagement score (retweets and quotes have higher weight)
        engagement = (likes * 1.0) + (retweets * 3.0) + (replies * 2.0) + (quotes * 2.5)
        
        # Bonus for high engagement rate
        if impressions > 0:
            engagement_rate = engagement / impressions
            return engagement + (engagement_rate * 1000)
        
        return engagement
        
    def count_sentiment_words(self, text: str) -> Dict[str, int]:
        """Count sentiment-bearing words"""
        positive_words = ['amazing', 'incredible', 'fantastic', 'brilliant', 'excellent', 'perfect', 'outstanding', 'phenomenal']
        negative_words = ['terrible', 'awful', 'horrible', 'disgusting', 'pathetic', 'useless', 'worthless', 'disaster']
        neutral_words = ['okay', 'fine', 'average', 'normal', 'typical', 'standard', 'regular', 'basic']
        
        text_lower = text.lower()
        return {
            'positive': sum(1 for word in positive_words if word in text_lower),
            'negative': sum(1 for word in negative_words if word in text_lower),
            'neutral': sum(1 for word in neutral_words if word in text_lower)
        }
        
    def count_power_words(self, text: str) -> int:
        """Count power/action words that drive engagement"""
        power_words = [
            'secret', 'proven', 'guaranteed', 'exclusive', 'limited', 'urgent', 'breakthrough',
            'revolutionary', 'insider', 'hidden', 'revealed', 'exposed', 'shocking', 'amazing',
            'incredible', 'powerful', 'ultimate', 'essential', 'critical', 'vital', 'important'
        ]
        
        text_lower = text.lower()
        return sum(1 for word in power_words if word in text_lower)
        
    def analyze_emoji_patterns(self, top_tweets: List[Dict]) -> Dict:
        """Analyze emoji usage patterns and optimal placement"""
        emoji_analysis = {
            'usage_stats': {},
            'placement_analysis': {},
            'performance_correlation': {}
        }
        
        # Common emoji categories
        emoji_categories = {
            'fire': ['🔥'],
            'rocket': ['🚀'],
            'money': ['💰', '💵', '💸', '💳'],
            'chart': ['📈', '📉', '📊'],
            'warning': ['⚠️', '🚨'],
            'thinking': ['🤔', '💭'],
            'celebration': ['🎉', '🥳', '🎊'],
            'eyes': ['👀', '👁️'],
            'hands': ['👋', '👍', '👎', '🙌', '👏'],
            'crypto': ['₿', '⚡']
        }
        
        tweets_with_emojis = [t for t in top_tweets if t['emoji_count'] > 0]
        tweets_without_emojis = [t for t in top_tweets if t['emoji_count'] == 0]
        
        emoji_analysis['usage_stats'] = {
            'tweets_with_emojis': len(tweets_with_emojis),
            'tweets_without_emojis': len(tweets_without_emojis),
            'avg_engagement_with_emojis': statistics.mean([t['engagement_score'] for t in tweets_with_emojis]) if tweets_with_emojis else 0,
            'avg_engagement_without_emojis': statistics.mean([t['engagement_score'] for t in tweets_without_emojis]) if tweets_without_emojis else 0,
        }
        
        # Analyze emoji placement (beginning, middle, end)
        for tweet in tweets_with_emojis:
            text = tweet['text']
            first_third = len(text) // 3
            last_third = 2 * len(text) // 3
            
            emoji_positions = []
            for match in re.finditer(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text):
                pos = match.start()
                if pos < first_third:
                    emoji_positions.append('beginning')
                elif pos > last_third:
                    emoji_positions.append('end')
                else:
                    emoji_positions.append('middle')
                    
            for position in emoji_positions:
                if position not in emoji_analysis['placement_analysis']:
                    emoji_analysis['placement_analysis'][position] = []
                emoji_analysis['placement_analysis'][position].append(tweet['engagement_score'])
        
        return emoji_analysis
        
    def analyze_cta_variations(self, top_tweets: List[Dict]) -> Dict:
        """Analyze call-to-action variations and effectiveness"""
        cta_patterns = {
            'think_about_it': r'think about it',
            'position_accordingly': r'position accordingly',
            'simple_as_that': r'simple as that',
            'this_is_the_way': r'this is the way',
            'few_understand': r'few understand',
            'most_will_miss': r'most will miss',
            'remember_this': r'remember this',
            'focus_on': r'focus on',
            'pay_attention': r'pay attention',
            'dont_miss': r'don\'t miss',
            'act_now': r'act now',
            'do_this': r'do this',
            'try_this': r'try this',
            'follow_me': r'follow me',
            'retweet_if': r'retweet if',
            'like_if': r'like if',
            'comment_below': r'comment below',
            'what_do_you_think': r'what do you think',
            'let_me_know': r'let me know',
            'share_your_thoughts': r'share your thoughts'
        }
        
        cta_analysis = {}
        
        for cta_name, pattern in cta_patterns.items():
            matching_tweets = []
            for tweet in top_tweets:
                if re.search(pattern, tweet['text'], re.IGNORECASE):
                    matching_tweets.append(tweet)
                    
            if matching_tweets:
                cta_analysis[cta_name] = {
                    'count': len(matching_tweets),
                    'avg_engagement': statistics.mean([t['engagement_score'] for t in matching_tweets]),
                    'engagement_range': [
                        min([t['engagement_score'] for t in matching_tweets]),
                        max([t['engagement_score'] for t in matching_tweets])
                    ],
                    'best_example': max(matching_tweets, key=lambda x: x['engagement_score'])
                }
                
        return cta_analysis
        
    def analyze_controversial_vs_safe(self, top_tweets: List[Dict]) -> Dict:
        """Analyze controversial vs safe content performance"""
        controversial_indicators = [
            'scam', 'fake', 'lie', 'wrong', 'stupid', 'idiots', 'morons', 'fools',
            'garbage', 'trash', 'bullshit', 'bs', 'ridiculous', 'insane', 'crazy',
            'unpopular opinion', 'controversial', 'against the grain', 'contrarian'
        ]
        
        safe_indicators = [
            'good', 'nice', 'great', 'awesome', 'fantastic', 'excellent',
            'agree', 'correct', 'right', 'smart', 'wise', 'brilliant',
            'helpful', 'useful', 'valuable', 'important', 'educational'
        ]
        
        controversial_tweets = []
        safe_tweets = []
        neutral_tweets = []
        
        for tweet in top_tweets:
            text_lower = tweet['text'].lower()
            
            is_controversial = any(indicator in text_lower for indicator in controversial_indicators)
            is_safe = any(indicator in text_lower for indicator in safe_indicators)
            
            if is_controversial:
                controversial_tweets.append(tweet)
            elif is_safe:
                safe_tweets.append(tweet)
            else:
                neutral_tweets.append(tweet)
                
        return {
            'controversial': {
                'count': len(controversial_tweets),
                'avg_engagement': statistics.mean([t['engagement_score'] for t in controversial_tweets]) if controversial_tweets else 0,
                'top_examples': sorted(controversial_tweets, key=lambda x: x['engagement_score'], reverse=True)[:3]
            },
            'safe': {
                'count': len(safe_tweets),
                'avg_engagement': statistics.mean([t['engagement_score'] for t in safe_tweets]) if safe_tweets else 0,
                'top_examples': sorted(safe_tweets, key=lambda x: x['engagement_score'], reverse=True)[:3]
            },
            'neutral': {
                'count': len(neutral_tweets),
                'avg_engagement': statistics.mean([t['engagement_score'] for t in neutral_tweets]) if neutral_tweets else 0,
                'top_examples': sorted(neutral_tweets, key=lambda x: x['engagement_score'], reverse=True)[:3]
            }
        }
        
    def analyze_time_patterns(self, top_tweets: List[Dict]) -> Dict:
        """Analyze posting time patterns (when available)"""
        time_analysis = {
            'has_timestamp_data': False,
            'patterns': {}
        }
        
        tweets_with_time = [t for t in top_tweets if t.get('created_at')]
        
        if tweets_with_time:
            time_analysis['has_timestamp_data'] = True
            time_analysis['sample_size'] = len(tweets_with_time)
            
            # Basic time analysis if timestamp data is available
            # This would need actual timestamp parsing based on the data format
            
        return time_analysis
        
    def identify_advanced_patterns(self, top_tweets: List[Dict]) -> Dict:
        """Identify advanced structural and content patterns"""
        advanced_patterns = {
            'paradox_statements': [],
            'contrarian_takes': [],
            'authority_positioning': [],
            'social_proof': [],
            'scarcity_urgency': [],
            'storytelling_elements': [],
            'data_driven': [],
            'emotional_hooks': []
        }
        
        for tweet in top_tweets:
            text = tweet['text']
            text_lower = text.lower()
            
            # Paradox statements
            if any(combo in text_lower for combo in ['less is more', 'slow to go fast', 'lose to win']):
                advanced_patterns['paradox_statements'].append(tweet)
                
            # Contrarian takes
            if any(phrase in text_lower for phrase in ['everyone thinks', 'most people believe', 'conventional wisdom', 'opposite']):
                advanced_patterns['contrarian_takes'].append(tweet)
                
            # Authority positioning
            if any(phrase in text_lower for phrase in ['i\'ve learned', 'in my experience', 'after years of', 'i\'ve seen']):
                advanced_patterns['authority_positioning'].append(tweet)
                
            # Social proof
            if any(phrase in text_lower for phrase in ['everyone is', 'most successful', 'top traders', 'smart money']):
                advanced_patterns['social_proof'].append(tweet)
                
            # Scarcity/urgency
            if any(phrase in text_lower for phrase in ['limited time', 'last chance', 'running out', 'few people know']):
                advanced_patterns['scarcity_urgency'].append(tweet)
                
            # Data-driven
            if re.search(r'\d+%|\d+x|\$\d+|statistics|data shows|research', text_lower):
                advanced_patterns['data_driven'].append(tweet)
                
            # Emotional hooks
            if any(emotion in text_lower for emotion in ['fear', 'greed', 'panic', 'excitement', 'frustration']):
                advanced_patterns['emotional_hooks'].append(tweet)
                
        return advanced_patterns
        
    def generate_comprehensive_analysis(self):
        """Generate the complete analysis report"""
        print("="*80)
        print("ENHANCED TWEET ENGAGEMENT ANALYSIS REPORT")
        print("="*80)
        
        # Load and process data
        self.load_and_process_all_data()
        
        # Remove duplicates based on text content
        unique_tweets = []
        seen_texts = set()
        for tweet in self.all_tweets:
            if tweet['text'] not in seen_texts:
                unique_tweets.append(tweet)
                seen_texts.add(tweet['text'])
        
        self.all_tweets = unique_tweets
        
        # Get top 100 by engagement
        top_100 = sorted(self.all_tweets, key=lambda x: x['engagement_score'], reverse=True)[:100]
        
        print(f"\nDATA OVERVIEW:")
        print(f"Total unique tweets analyzed: {len(self.all_tweets)}")
        print(f"Top 100 tweets by engagement score")
        if top_100:
            print(f"Average engagement score (top 100): {statistics.mean([t['engagement_score'] for t in top_100]):.2f}")
            print(f"Engagement score range: {min([t['engagement_score'] for t in top_100]):.2f} - {max([t['engagement_score'] for t in top_100]):.2f}")
        
        # Advanced Pattern Analysis
        print(f"\n{'='*60}")
        print("ADVANCED STRUCTURAL PATTERNS")
        print(f"{'='*60}")
        
        advanced_patterns = self.identify_advanced_patterns(top_100)
        for pattern_name, tweets in advanced_patterns.items():
            if tweets:
                avg_engagement = statistics.mean([t['engagement_score'] for t in tweets])
                print(f"\n{pattern_name.upper().replace('_', ' ')}:")
                print(f"  Count: {len(tweets)}")
                print(f"  Avg Engagement: {avg_engagement:.2f}")
                print(f"  Best Example: {tweets[0]['text'][:100]}...")
        
        # CTA Analysis
        print(f"\n{'='*60}")
        print("CALL-TO-ACTION EFFECTIVENESS")
        print(f"{'='*60}")
        
        cta_analysis = self.analyze_cta_variations(top_100)
        for cta_name, data in sorted(cta_analysis.items(), key=lambda x: x[1]['avg_engagement'], reverse=True):
            print(f"\nCTA: '{cta_name.replace('_', ' ').title()}'")
            print(f"  Usage Count: {data['count']}")
            print(f"  Avg Engagement: {data['avg_engagement']:.2f}")
            print(f"  Range: {data['engagement_range'][0]:.2f} - {data['engagement_range'][1]:.2f}")
            print(f"  Best Example: {data['best_example']['text'][:80]}...")
        
        # Emoji Analysis
        print(f"\n{'='*60}")
        print("EMOJI USAGE PATTERNS & OPTIMAL PLACEMENT")
        print(f"{'='*60}")
        
        emoji_analysis = self.analyze_emoji_patterns(top_100)
        print(f"Tweets with emojis: {emoji_analysis['usage_stats']['tweets_with_emojis']}/100")
        print(f"Avg engagement with emojis: {emoji_analysis['usage_stats']['avg_engagement_with_emojis']:.2f}")
        print(f"Avg engagement without emojis: {emoji_analysis['usage_stats']['avg_engagement_without_emojis']:.2f}")
        
        print(f"\nEmoji Placement Analysis:")
        for position, scores in emoji_analysis['placement_analysis'].items():
            if scores:
                print(f"  {position.title()}: {len(scores)} instances, Avg engagement: {statistics.mean(scores):.2f}")
        
        # Controversial vs Safe Content
        print(f"\n{'='*60}")
        print("CONTROVERSIAL VS SAFE CONTENT PERFORMANCE")
        print(f"{'='*60}")
        
        controversy_analysis = self.analyze_controversial_vs_safe(top_100)
        for content_type, data in controversy_analysis.items():
            print(f"\n{content_type.upper()} CONTENT:")
            print(f"  Count: {data['count']}")
            print(f"  Avg Engagement: {data['avg_engagement']:.2f}")
            if data['top_examples']:
                print(f"  Top Example: {data['top_examples'][0]['text'][:80]}...")
        
        # Top Performing Tweets with Details
        print(f"\n{'='*60}")
        print("TOP 20 HIGHEST PERFORMING TWEETS - DETAILED ANALYSIS")
        print(f"{'='*60}")
        
        for i, tweet in enumerate(top_100[:20], 1):
            print(f"\n#{i} - Engagement Score: {tweet['engagement_score']:.2f}")
            print(f"Text: {tweet['text']}")
            print(f"Metrics: Likes: {tweet['metrics'].get('likes', 0)}, RTs: {tweet['metrics'].get('retweets', 0)}, Replies: {tweet['metrics'].get('replies', 0)}")
            print(f"Features: {tweet['word_count']} words, {tweet['character_count']} chars, {tweet['emoji_count']} emojis, {tweet['question_marks']} questions")
            print(f"Power words: {tweet['power_words']}, Line breaks: {tweet['line_breaks']}")
            print("-" * 50)
        
        # Final Insights Summary
        print(f"\n{'='*60}")
        print("KEY INSIGHTS & RECOMMENDATIONS")
        print(f"{'='*60}")
        
        # Content length analysis
        word_counts = [t['word_count'] for t in top_100]
        char_counts = [t['character_count'] for t in top_100]
        
        print(f"\nOPTIMAL CONTENT LENGTH:")
        print(f"  Average words in top tweets: {statistics.mean(word_counts):.1f}")
        print(f"  Sweet spot range: {min(word_counts)} - {max(word_counts)} words")
        print(f"  Average characters: {statistics.mean(char_counts):.1f}")
        
        # Engagement patterns
        question_tweets = [t for t in top_100 if t['question_marks'] > 0]
        print(f"\nQUESTION EFFECTIVENESS:")
        print(f"  Questions in top 100: {len(question_tweets)}")
        if question_tweets:
            print(f"  Avg engagement with questions: {statistics.mean([t['engagement_score'] for t in question_tweets]):.2f}")
        
        # Power word effectiveness
        power_word_tweets = [t for t in top_100 if t['power_words'] > 0]
        print(f"\nPOWER WORD USAGE:")
        print(f"  Tweets with power words: {len(power_word_tweets)}")
        if power_word_tweets:
            print(f"  Avg engagement with power words: {statistics.mean([t['engagement_score'] for t in power_word_tweets]):.2f}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    analyzer = EnhancedTweetAnalyzer(base_dir)
    analyzer.generate_comprehensive_analysis()