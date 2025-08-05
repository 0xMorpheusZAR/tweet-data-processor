#!/usr/bin/env python3
"""
Comprehensive Tweet Engagement Analysis
Analyzes JSON files to extract top 100 tweets by engagement score and identifies patterns.
"""

import json
import os
import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Any, Tuple
import statistics

class TweetAnalyzer:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.all_tweets = []
        self.top_100_tweets = []
        
        # Pattern categories
        self.structural_patterns = defaultdict(list)
        self.micro_patterns = defaultdict(list)
        self.emotional_triggers = defaultdict(list)
        self.linguistic_devices = defaultdict(list)
        self.content_themes = defaultdict(list)
        self.emoji_patterns = defaultdict(list)
        self.cta_patterns = defaultdict(list)
        
    def load_json_files(self):
        """Load all relevant JSON files"""
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
                    print(f"Loading {filename}...")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.process_json_data(data, filename)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    
    def process_json_data(self, data: Any, source_file: str):
        """Process JSON data and extract tweet information"""
        if isinstance(data, dict):
            # Handle pattern examples format
            if any(key in data for key in ['5_part', '3_part_classic', '7_part', 'question', 'short_take']):
                for pattern_type, tweets in data.items():
                    if isinstance(tweets, list):
                        for tweet in tweets:
                            self.process_tweet(tweet, source_file, pattern_type)
            else:
                # Handle other dict formats
                for key, value in data.items():
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict) and 'text' in item:
                                self.process_tweet(item, source_file, key)
                    elif isinstance(value, dict) and 'text' in value:
                        self.process_tweet(value, source_file, key)
                        
        elif isinstance(data, list):
            # Handle list format
            for item in data:
                if isinstance(item, dict) and 'text' in item:
                    self.process_tweet(item, source_file)
                    
    def process_tweet(self, tweet: Dict, source_file: str, pattern_type: str = None):
        """Process individual tweet and calculate engagement score"""
        if not isinstance(tweet, dict) or 'text' not in tweet:
            return
            
        # Calculate engagement score
        metrics = tweet.get('metrics', {})
        engagement_score = self.calculate_engagement_score(metrics)
        
        # Enhanced tweet object
        enhanced_tweet = {
            'text': tweet['text'],
            'engagement_score': engagement_score,
            'metrics': metrics,
            'source_file': source_file,
            'pattern_type': pattern_type,
            'quality_score': tweet.get('quality_score', 0),
            'word_count': len(tweet['text'].split()),
            'character_count': len(tweet['text']),
            'hashtag_count': len(re.findall(r'#\w+', tweet['text'])),
            'mention_count': len(re.findall(r'@\w+', tweet['text'])),
            'url_count': len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet['text'])),
            'emoji_count': len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', tweet['text'])),
            'question_marks': tweet['text'].count('?'),
            'exclamation_marks': tweet['text'].count('!'),
            'line_breaks': tweet['text'].count('\n'),
            'has_thread_indicator': bool(re.search(r'\d+/', tweet['text'])),
            'posting_time': tweet.get('created_at', tweet.get('timestamp', '')),
        }
        
        self.all_tweets.append(enhanced_tweet)
        
    def calculate_engagement_score(self, metrics: Dict) -> float:
        """Calculate weighted engagement score"""
        if not metrics:
            return 0
            
        likes = metrics.get('likes', 0)
        retweets = metrics.get('retweets', 0) 
        replies = metrics.get('replies', 0)
        quotes = metrics.get('quotes', 0)
        impressions = metrics.get('impressions', 0)
        
        # Weighted engagement score
        engagement = (likes * 1.0) + (retweets * 3.0) + (replies * 2.0) + (quotes * 2.5)
        
        # Normalize by impressions if available
        if impressions > 0:
            engagement_rate = engagement / impressions
            return engagement + (engagement_rate * 1000)  # Boost for high engagement rate
        
        return engagement
        
    def get_top_100_tweets(self):
        """Get top 100 tweets by engagement score"""
        sorted_tweets = sorted(self.all_tweets, key=lambda x: x['engagement_score'], reverse=True)
        self.top_100_tweets = sorted_tweets[:100]
        return self.top_100_tweets
        
    def analyze_structural_patterns(self):
        """Analyze structural patterns beyond basic 5"""
        patterns = {
            'numbered_list': [],
            'bullet_points': [],
            'question_hook': [],
            'thesis_evidence_conclusion': [],
            'problem_solution': [],
            'before_after': [],
            'comparison': [],
            'story_arc': [],
            'thread_structure': [],
            'single_line_power': []
        }
        
        for tweet in self.top_100_tweets:
            text = tweet['text']
            
            # Numbered lists
            if re.search(r'\d+\.\s', text):
                patterns['numbered_list'].append(tweet)
                
            # Question hooks
            if text.startswith(('What if', 'Why', 'How', 'When', 'Where')):
                patterns['question_hook'].append(tweet)
                
            # Thread indicators  
            if tweet['has_thread_indicator'] or tweet['line_breaks'] > 2:
                patterns['thread_structure'].append(tweet)
                
            # Single line power statements
            if tweet['line_breaks'] == 0 and tweet['word_count'] < 10:
                patterns['single_line_power'].append(tweet)
                
            # Problem-solution pattern
            if any(word in text.lower() for word in ['problem', 'solution', 'issue', 'fix']):
                patterns['problem_solution'].append(tweet)
                
            # Comparison pattern
            if any(word in text.lower() for word in ['vs', 'versus', 'compared to', 'better than']):
                patterns['comparison'].append(tweet)
                
        return patterns
        
    def analyze_micro_patterns(self):
        """Analyze specific word combinations that drive engagement"""
        micro_patterns = defaultdict(list)
        
        # Common high-engagement word combinations
        patterns_to_check = [
            r'think about it',
            r'few understand',
            r'most will miss',
            r'simple as that',
            r'this is the way',
            r'position accordingly',
            r'the real game',
            r'everyone\'s focused on',
            r'what if.*\?',
            r'flashing (red|green)',
            r'beats .* every time',
            r'looking (ready|coiled)',
            r'narrative shifts?',
            r'breaking? out here',
            r'the .* situation',
        ]
        
        for pattern in patterns_to_check:
            matching_tweets = []
            for tweet in self.top_100_tweets:
                if re.search(pattern, tweet['text'], re.IGNORECASE):
                    matching_tweets.append(tweet)
            
            if matching_tweets:
                avg_engagement = statistics.mean([t['engagement_score'] for t in matching_tweets])
                micro_patterns[pattern] = {
                    'tweets': matching_tweets,
                    'count': len(matching_tweets),
                    'avg_engagement': avg_engagement,
                    'examples': [t['text'] for t in matching_tweets[:3]]
                }
                
        return dict(micro_patterns)
        
    def analyze_emotional_triggers(self):
        """Analyze emotional triggers and their correlation with virality"""
        emotional_categories = {
            'fear': ['crash', 'dump', 'panic', 'fear', 'scary', 'danger', 'risk', 'loss'],
            'greed': ['moon', 'pump', 'gains', 'profit', 'rich', 'money', 'wealth'],
            'fomo': ['missing', 'last chance', 'opportunity', 'limited', 'exclusive'],
            'confidence': ['strong', 'bullish', 'confident', 'certain', 'guaranteed'],
            'uncertainty': ['maybe', 'perhaps', 'might', 'could', 'what if'],
            'urgency': ['now', 'today', 'immediately', 'urgent', 'quick'],
            'exclusivity': ['insider', 'secret', 'hidden', 'few know', 'exclusive'],
            'controversy': ['wrong', 'scam', 'fake', 'lie', 'misleading'],
        }
        
        trigger_analysis = {}
        
        for emotion, keywords in emotional_categories.items():
            matching_tweets = []
            for tweet in self.top_100_tweets:
                text_lower = tweet['text'].lower()
                if any(keyword in text_lower for keyword in keywords):
                    matching_tweets.append(tweet)
                    
            if matching_tweets:
                avg_engagement = statistics.mean([t['engagement_score'] for t in matching_tweets])
                trigger_analysis[emotion] = {
                    'count': len(matching_tweets),
                    'avg_engagement': avg_engagement,
                    'top_examples': sorted(matching_tweets, key=lambda x: x['engagement_score'], reverse=True)[:3]
                }
                
        return trigger_analysis
        
    def analyze_content_themes(self):
        """Analyze content themes and their performance"""
        themes = {
            'trading_advice': ['trade', 'position', 'entry', 'exit', 'buy', 'sell'],
            'market_analysis': ['market', 'trend', 'chart', 'technical', 'analysis'],
            'cryptocurrency': ['bitcoin', 'eth', 'crypto', 'altcoin', 'defi'],
            'psychology': ['mindset', 'emotion', 'psychology', 'discipline', 'patience'],
            'education': ['learn', 'understand', 'teach', 'explain', 'knowledge'],
            'predictions': ['predict', 'forecast', 'expect', 'will', 'going to'],
            'motivation': ['success', 'focus', 'goal', 'achieve', 'win'],
            'contrarian': ['everyone wrong', 'opposite', 'different', 'against'],
        }
        
        theme_analysis = {}
        
        for theme, keywords in themes.items():
            matching_tweets = []
            for tweet in self.top_100_tweets:
                text_lower = tweet['text'].lower()
                if any(keyword in text_lower for keyword in keywords):
                    matching_tweets.append(tweet)
                    
            if matching_tweets:
                avg_engagement = statistics.mean([t['engagement_score'] for t in matching_tweets])
                theme_analysis[theme] = {
                    'count': len(matching_tweets),
                    'avg_engagement': avg_engagement,
                    'engagement_range': [min([t['engagement_score'] for t in matching_tweets]),
                                       max([t['engagement_score'] for t in matching_tweets])],
                    'top_example': max(matching_tweets, key=lambda x: x['engagement_score'])
                }
                
        return theme_analysis
        
    def analyze_linguistic_devices(self):
        """Analyze linguistic devices and their effectiveness"""
        devices = {
            'questions': [],
            'paradoxes': [],
            'lists': [],
            'repetition': [],
            'alliteration': [],
            'contrast': [],
            'metaphors': [],
            'imperatives': []
        }
        
        for tweet in self.top_100_tweets:
            text = tweet['text']
            
            # Questions
            if '?' in text:
                devices['questions'].append(tweet)
                
            # Lists (numbered or bullet)
            if re.search(r'\d+\.|\n-|\n•', text):
                devices['lists'].append(tweet)
                
            # Repetition (same word appears multiple times)
            words = text.lower().split()
            word_counts = Counter(words)
            if any(count > 2 for word, count in word_counts.items() if len(word) > 3):
                devices['repetition'].append(tweet)
                
            # Contrast words
            if any(word in text.lower() for word in ['but', 'however', 'vs', 'while', 'although']):
                devices['contrast'].append(tweet)
                
            # Imperatives (command words)
            if any(text.lower().startswith(word) for word in ['think', 'focus', 'position', 'remember', 'understand']):
                devices['imperatives'].append(tweet)
                
        # Calculate effectiveness for each device
        device_analysis = {}
        for device, tweets in devices.items():
            if tweets:
                avg_engagement = statistics.mean([t['engagement_score'] for t in tweets])
                device_analysis[device] = {
                    'count': len(tweets),
                    'avg_engagement': avg_engagement,
                    'effectiveness_score': avg_engagement / len(tweets) if tweets else 0,
                    'top_example': max(tweets, key=lambda x: x['engagement_score'])
                }
                
        return device_analysis
        
    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        print("="*80)
        print("COMPREHENSIVE TWEET ENGAGEMENT ANALYSIS REPORT")
        print("="*80)
        
        # Load data and get top 100
        self.load_json_files()
        top_100 = self.get_top_100_tweets()
        
        print(f"\nDATA OVERVIEW:")
        print(f"Total tweets analyzed: {len(self.all_tweets)}")
        print(f"Top 100 tweets by engagement score")
        print(f"Average engagement score (top 100): {statistics.mean([t['engagement_score'] for t in top_100]):.2f}")
        print(f"Engagement score range: {min([t['engagement_score'] for t in top_100]):.2f} - {max([t['engagement_score'] for t in top_100]):.2f}")
        
        # 1. Structural Patterns Analysis
        print(f"\n{'='*50}")
        print("1. STRUCTURAL PATTERNS BEYOND BASIC 5")
        print(f"{'='*50}")
        
        structural = self.analyze_structural_patterns()
        for pattern, tweets in structural.items():
            if tweets:
                avg_engagement = statistics.mean([t['engagement_score'] for t in tweets])
                print(f"\n{pattern.upper().replace('_', ' ')}:")
                print(f"  Count: {len(tweets)}")
                print(f"  Avg Engagement: {avg_engagement:.2f}")
                print(f"  Top Example: {tweets[0]['text'][:100]}...")
                
        # 2. Micro-patterns Analysis
        print(f"\n{'='*50}")
        print("2. MICRO-PATTERNS (Word Combinations)")
        print(f"{'='*50}")
        
        micro = self.analyze_micro_patterns()
        for pattern, data in sorted(micro.items(), key=lambda x: x[1]['avg_engagement'], reverse=True):
            print(f"\nPattern: '{pattern}'")
            print(f"  Occurrences: {data['count']}")
            print(f"  Avg Engagement: {data['avg_engagement']:.2f}")
            print(f"  Example: {data['examples'][0] if data['examples'] else 'N/A'}")
            
        # 3. Emotional Triggers Analysis
        print(f"\n{'='*50}")
        print("3. EMOTIONAL TRIGGERS & VIRALITY CORRELATION") 
        print(f"{'='*50}")
        
        emotional = self.analyze_emotional_triggers()
        for emotion, data in sorted(emotional.items(), key=lambda x: x[1]['avg_engagement'], reverse=True):
            print(f"\n{emotion.upper()}:")
            print(f"  Count: {data['count']}")
            print(f"  Avg Engagement: {data['avg_engagement']:.2f}")
            if data['top_examples']:
                print(f"  Top Example: {data['top_examples'][0]['text'][:100]}...")
                print(f"  Engagement: {data['top_examples'][0]['engagement_score']:.2f}")
                
        # 4. Content Themes Analysis
        print(f"\n{'='*50}")
        print("4. CONTENT THEMES & PERFORMANCE")
        print(f"{'='*50}")
        
        themes = self.analyze_content_themes()
        for theme, data in sorted(themes.items(), key=lambda x: x[1]['avg_engagement'], reverse=True):
            print(f"\n{theme.upper().replace('_', ' ')}:")
            print(f"  Count: {data['count']}")
            print(f"  Avg Engagement: {data['avg_engagement']:.2f}")
            print(f"  Range: {data['engagement_range'][0]:.2f} - {data['engagement_range'][1]:.2f}")
            print(f"  Best Example: {data['top_example']['text'][:100]}...")
            
        # 5. Linguistic Devices Analysis
        print(f"\n{'='*50}")
        print("5. LINGUISTIC DEVICES EFFECTIVENESS")
        print(f"{'='*50}")
        
        devices = self.analyze_linguistic_devices()
        for device, data in sorted(devices.items(), key=lambda x: x[1]['avg_engagement'], reverse=True):
            print(f"\n{device.upper()}:")
            print(f"  Count: {data['count']}")
            print(f"  Avg Engagement: {data['avg_engagement']:.2f}")
            print(f"  Effectiveness Score: {data['effectiveness_score']:.2f}")
            print(f"  Best Example: {data['top_example']['text'][:100]}...")
            
        # 6. Top 10 Highest Performing Tweets
        print(f"\n{'='*50}")
        print("6. TOP 10 HIGHEST PERFORMING TWEETS")
        print(f"{'='*50}")
        
        for i, tweet in enumerate(top_100[:10], 1):
            print(f"\n#{i} - Engagement Score: {tweet['engagement_score']:.2f}")
            print(f"Text: {tweet['text']}")
            print(f"Metrics: {tweet['metrics']}")
            print(f"Pattern: {tweet.get('pattern_type', 'N/A')}")
            print("-" * 40)
            
        # 7. Summary Statistics
        print(f"\n{'='*50}")
        print("7. SUMMARY INSIGHTS")
        print(f"{'='*50}")
        
        # Word count analysis
        word_counts = [t['word_count'] for t in top_100]
        print(f"\nWord Count Analysis:")
        print(f"  Average words: {statistics.mean(word_counts):.1f}")
        print(f"  Range: {min(word_counts)} - {max(word_counts)} words")
        
        # Character count analysis  
        char_counts = [t['character_count'] for t in top_100]
        print(f"\nCharacter Count Analysis:")
        print(f"  Average characters: {statistics.mean(char_counts):.1f}")
        print(f"  Range: {min(char_counts)} - {max(char_counts)} characters")
        
        # Question usage
        question_tweets = [t for t in top_100 if t['question_marks'] > 0]
        print(f"\nQuestion Usage:")
        print(f"  Tweets with questions: {len(question_tweets)}/100 ({len(question_tweets)}%)")
        if question_tweets:
            print(f"  Avg engagement (with questions): {statistics.mean([t['engagement_score'] for t in question_tweets]):.2f}")
            
        # Thread vs standalone
        thread_tweets = [t for t in top_100 if t['line_breaks'] > 2 or t['has_thread_indicator']]
        standalone_tweets = [t for t in top_100 if t not in thread_tweets]
        print(f"\nThread vs Standalone:")
        print(f"  Thread-style tweets: {len(thread_tweets)}")
        print(f"  Standalone tweets: {len(standalone_tweets)}")
        if thread_tweets:
            print(f"  Avg engagement (threads): {statistics.mean([t['engagement_score'] for t in thread_tweets]):.2f}")
        if standalone_tweets:
            print(f"  Avg engagement (standalone): {statistics.mean([t['engagement_score'] for t in standalone_tweets]):.2f}")

if __name__ == "__main__":
    # Set base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Initialize analyzer
    analyzer = TweetAnalyzer(base_dir)
    
    # Generate comprehensive report
    analyzer.generate_comprehensive_report()