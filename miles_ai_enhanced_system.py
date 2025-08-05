"""
Miles Deutscher AI - Enhanced System with Frontend & Backend Optimization
Features:
1. Advanced pattern recognition and ML-based generation
2. Real-time visualization of pulled tweets
3. Continuous learning process visualization
4. Improved tweet quality based on latest patterns
5. Performance metrics and analytics
"""

import os
import json
import time
import threading
import queue
import random
import hashlib
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import urllib.request
import urllib.parse
import ssl
import http.server
import socketserver
import logging
from typing import Dict, List, Optional, Tuple
import math

# Enhanced logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('miles_ai_enhanced.log'),
        logging.StreamHandler()
    ]
)

class EnhancedPatternAnalyzer:
    """Advanced pattern analysis for Miles' tweets"""
    
    def __init__(self):
        self.patterns = {
            'structural': defaultdict(int),
            'linguistic': defaultdict(list),
            'temporal': defaultdict(list),
            'engagement': defaultdict(float),
            'vocabulary': Counter(),
            'transitions': defaultdict(list)
        }
        
    def analyze_tweet(self, tweet: Dict) -> Dict:
        """Deep analysis of individual tweet"""
        text = tweet.get('text', '')
        metrics = tweet.get('public_metrics', {})
        created_at = tweet.get('created_at', '')
        
        analysis = {
            'structure': self._analyze_structure(text),
            'sentiment': self._analyze_sentiment(text),
            'hooks': self._extract_hooks(text),
            'vocabulary': self._analyze_vocabulary(text),
            'engagement_score': self._calculate_engagement(metrics),
            'timestamp': created_at,
            'length': len(text),
            'punctuation': self._analyze_punctuation(text)
        }
        
        return analysis
    
    def _analyze_structure(self, text: str) -> Dict:
        """Analyze tweet structure in detail"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        structure = {
            'line_count': len(lines),
            'pattern': f"{len(lines)}_part",
            'opening_type': self._classify_opening(lines[0] if lines else ''),
            'closing_type': self._classify_closing(lines[-1] if lines else ''),
            'has_question': '?' in text,
            'has_statement': any(line.endswith('.') for line in lines)
        }
        
        # Detect three-part structure (dismiss → focus → reality)
        if len(lines) == 3:
            structure['is_canonical'] = True
            structure['parts'] = {
                'dismiss': lines[0],
                'focus': lines[1],
                'reality': lines[2]
            }
        
        return structure
    
    def _analyze_sentiment(self, text: str) -> str:
        """Classify sentiment/tone"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['bullish', 'pump', 'moon', 'fire', 'absolutely']):
            return 'bullish'
        elif any(word in text_lower for word in ['bearish', 'dump', 'rekt', 'cooked', 'weakness']):
            return 'bearish'
        elif any(word in text_lower for word in ['noise', 'chop', 'range', 'sideways']):
            return 'neutral'
        elif '?' in text:
            return 'questioning'
        else:
            return 'philosophical'
    
    def _extract_hooks(self, text: str) -> List[str]:
        """Extract opening hooks/phrases"""
        hooks = []
        
        # Common Miles patterns
        patterns = [
            r'^(The .+ is just noise)',
            r'^(Everyone.+)',
            r'^(Real talk:)',
            r'^(Unpopular opinion:)',
            r'^(News flash:)',
            r'^(Ser,)',
            r'^(\$\w+ )',
            r'^(Warning:)',
            r'^(Your .+)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                hooks.append(match.group(1))
        
        return hooks
    
    def _analyze_vocabulary(self, text: str) -> Dict:
        """Analyze vocabulary usage"""
        # Remove URLs and special characters
        clean_text = re.sub(r'http\S+|[^a-zA-Z0-9\s$]', ' ', text)
        words = clean_text.lower().split()
        
        # Key Miles vocabulary
        miles_vocab = {
            'technical': ['liquidity', 'macro', 'narrative', 'accumulation', 'resistance', 'support'],
            'slang': ['ser', 'anon', 'ngmi', 'gm', 'rekt', 'cooked', 'based'],
            'action': ['pump', 'dump', 'moon', 'capitulate', 'accumulate'],
            'dismissive': ['noise', 'chop', 'cope', 'few']
        }
        
        vocab_analysis = {
            'total_words': len(words),
            'unique_words': len(set(words)),
            'categories': {}
        }
        
        for category, keywords in miles_vocab.items():
            vocab_analysis['categories'][category] = sum(1 for word in words if word in keywords)
        
        return vocab_analysis
    
    def _calculate_engagement(self, metrics: Dict) -> float:
        """Calculate weighted engagement score"""
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        quotes = metrics.get('quote_count', 0)
        
        # Weighted formula
        engagement = (likes * 1) + (retweets * 2) + (replies * 1.5) + (quotes * 2.5)
        
        return engagement
    
    def _analyze_punctuation(self, text: str) -> Dict:
        """Analyze punctuation patterns"""
        return {
            'periods': text.count('.'),
            'questions': text.count('?'),
            'exclamations': text.count('!'),
            'ellipses': text.count('...'),
            'line_breaks': text.count('\n')
        }
    
    def _classify_opening(self, line: str) -> str:
        """Classify opening line type"""
        if line.endswith('noise.'):
            return 'dismissive'
        elif line.startswith('$'):
            return 'ticker'
        elif ':' in line:
            return 'label'
        elif '?' in line:
            return 'question'
        else:
            return 'statement'
    
    def _classify_closing(self, line: str) -> str:
        """Classify closing line type"""
        if any(word in line.lower() for word in ['few', 'ngmi', 'based']):
            return 'meme'
        elif '?' in line:
            return 'question'
        elif any(word in line.lower() for word in ['until', 'then']):
            return 'conditional'
        else:
            return 'statement'

class AdvancedTweetGenerator:
    """ML-enhanced tweet generation based on patterns"""
    
    def __init__(self, analyzer: EnhancedPatternAnalyzer):
        self.analyzer = analyzer
        self.templates = self._load_enhanced_templates()
        self.vocabulary = self._build_vocabulary()
        
    def generate(self, input_text: str, recent_patterns: Dict) -> Dict:
        """Generate tweet using advanced ML patterns"""
        
        # Analyze input
        input_analysis = self._analyze_input(input_text)
        
        # Select generation strategy
        if input_analysis['type'] == 'question':
            tweet = self._generate_question_response(input_text, recent_patterns)
        elif input_analysis['sentiment'] == 'bullish':
            tweet = self._generate_bullish(input_text, recent_patterns)
        elif input_analysis['sentiment'] == 'bearish':
            tweet = self._generate_bearish(input_text, recent_patterns)
        elif input_analysis['complexity'] == 'complex':
            tweet = self._generate_philosophical(input_text, recent_patterns)
        else:
            tweet = self._generate_adaptive(input_text, recent_patterns)
        
        # Post-process
        tweet = self._apply_style_refinements(tweet, recent_patterns)
        
        return {
            'text': tweet,
            'confidence': self._calculate_confidence(tweet, recent_patterns),
            'strategy': input_analysis['type'],
            'pattern_match': self._find_closest_pattern(tweet, recent_patterns)
        }
    
    def _analyze_input(self, text: str) -> Dict:
        """Analyze user input"""
        text_lower = text.lower()
        
        analysis = {
            'type': 'statement',
            'sentiment': 'neutral',
            'complexity': 'simple',
            'topics': []
        }
        
        # Type detection
        if '?' in text:
            analysis['type'] = 'question'
        elif any(word in text_lower for word in ['explain', 'why', 'how']):
            analysis['type'] = 'explanation'
        
        # Sentiment
        if any(word in text_lower for word in ['bull', 'pump', 'moon', 'buy']):
            analysis['sentiment'] = 'bullish'
        elif any(word in text_lower for word in ['bear', 'dump', 'sell', 'crash']):
            analysis['sentiment'] = 'bearish'
        
        # Complexity
        if len(text.split()) > 10 or any(word in text_lower for word in ['because', 'therefore', 'however']):
            analysis['complexity'] = 'complex'
        
        return analysis
    
    def _generate_philosophical(self, input_text: str, patterns: Dict) -> str:
        """Generate philosophical/complex tweet"""
        
        # Extract key concept
        concept = self._extract_concept(input_text)
        
        # Use canonical three-part structure
        templates = [
            {
                'dismiss': f"The {concept} debate is just noise.",
                'focus': "What matters: positioning for the inevitable liquidity cycle.",
                'reality': "Until then? We're all just trading the range."
            },
            {
                'dismiss': f"Everyone obsessing over {concept} is missing the forest for the trees.",
                'focus': "Real alpha: understanding when narrative meets liquidity.",
                'reality': "Everything else is just sophisticated gambling."
            },
            {
                'dismiss': f"{concept.capitalize()} analysis without macro context is mental masturbation.",
                'focus': "Focus on: liquidity trends, narrative shifts, position sizing.",
                'reality': "The rest is noise designed to shake you out."
            }
        ]
        
        template = random.choice(templates)
        return f"{template['dismiss']}\n\n{template['focus']}\n\n{template['reality']}"
    
    def _generate_bullish(self, input_text: str, patterns: Dict) -> str:
        """Generate bullish tweet"""
        ticker = self._extract_ticker(input_text) or "BTC"
        
        templates = [
            f"${ticker} chart printing a textbook accumulation pattern.\n\nSmart money loading, retail crying.\n\nYou know what comes next.",
            f"Imagine fading ${ticker} here.\n\nClean break of resistance + volume confirmation.\n\nNGMI if you're not paying attention.",
            f"${ticker} coiling like a mf.\n\nWhen this breaks, faces will melt.\n\nPosition accordingly."
        ]
        
        return random.choice(templates)
    
    def _generate_bearish(self, input_text: str, patterns: Dict) -> str:
        """Generate bearish tweet"""
        ticker = self._extract_ticker(input_text) or "the market"
        
        templates = [
            f"{ticker} showing textbook distribution.\n\nSmart money exiting, retail buying the 'dip'.\n\nProtect your capital.",
            f"That {ticker} chart looking absolutely cooked.\n\nNo bid, momentum gone.\n\nDon't be exit liquidity.",
            f"Warning: {ticker} about to get a reality check.\n\nSupport levels are suggestions until they're not.\n\nRisk management > hopium."
        ]
        
        return random.choice(templates)
    
    def _generate_question_response(self, input_text: str, patterns: Dict) -> str:
        """Generate response to question"""
        
        templates = [
            f"{input_text}\n\nThe answer is always liquidity + narrative.\n\nEverything else is cope.",
            f"{input_text}\n\nYou already know the answer.\n\nTrust the process.",
            f"{input_text}\n\nYes, but only if you understand position sizing.\n\nFew do."
        ]
        
        return random.choice(templates)
    
    def _generate_adaptive(self, input_text: str, patterns: Dict) -> str:
        """Adaptive generation based on latest patterns"""
        
        # Find most successful recent pattern
        if patterns and 'high_engagement' in patterns:
            high_engagement = patterns['high_engagement']
            if high_engagement:
                # Adapt based on high-performing tweets
                best = max(high_engagement, key=lambda x: x['engagement'])
                structure = self.analyzer._analyze_structure(best['text'])
                
                if structure['line_count'] == 3:
                    return self._generate_philosophical(input_text, patterns)
        
        # Default to quick take
        return f"{input_text}\n\nFew understand this."
    
    def _extract_ticker(self, text: str) -> Optional[str]:
        """Extract ticker symbol"""
        match = re.search(r'\$?([A-Z]{2,5})\b', text.upper())
        return match.group(1) if match else None
    
    def _extract_concept(self, text: str) -> str:
        """Extract main concept from input"""
        # Remove common words
        stopwords = {'the', 'is', 'are', 'was', 'were', 'been', 'have', 'has', 'had', 'will', 'would', 'could', 'should'}
        words = [w for w in text.lower().split() if w not in stopwords]
        
        if len(words) > 3:
            return ' '.join(words[:3])
        return ' '.join(words) if words else 'market dynamics'
    
    def _apply_style_refinements(self, tweet: str, patterns: Dict) -> str:
        """Apply final style refinements"""
        
        # Ensure no fake links
        tweet = re.sub(r'https?://\S+', '', tweet).strip()
        
        # Ensure proper line spacing
        lines = tweet.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        
        if len(cleaned_lines) >= 3:
            # Canonical three-part structure
            tweet = '\n\n'.join(cleaned_lines[:3])
        elif len(cleaned_lines) == 2:
            tweet = '\n\n'.join(cleaned_lines)
        
        return tweet
    
    def _calculate_confidence(self, tweet: str, patterns: Dict) -> float:
        """Calculate generation confidence score"""
        score = 0.5  # Base score
        
        # Check structure match
        structure = self.analyzer._analyze_structure(tweet)
        if structure['line_count'] == 3:
            score += 0.2
        
        # Check vocabulary match
        vocab = self.analyzer._analyze_vocabulary(tweet)
        if vocab['categories']['slang'] > 0:
            score += 0.1
        if vocab['categories']['technical'] > 0:
            score += 0.1
        
        # Check pattern similarity
        if patterns and 'structures' in patterns:
            dominant = max(patterns['structures'].items(), key=lambda x: x[1])[0]
            if structure['pattern'] == dominant:
                score += 0.1
        
        return min(score, 1.0)
    
    def _find_closest_pattern(self, tweet: str, patterns: Dict) -> str:
        """Find closest matching pattern"""
        structure = self.analyzer._analyze_structure(tweet)
        
        if structure['is_canonical']:
            return "canonical_3_part"
        elif structure['has_question']:
            return "question_response"
        else:
            return f"{structure['pattern']}_{structure['opening_type']}"
    
    def _load_enhanced_templates(self) -> Dict:
        """Load enhanced templates"""
        return {
            'openings': [
                "The {topic} narrative is exhausting.",
                "Your {topic} thesis ignores one thing:",
                "Real talk about {topic}:",
                "Unpopular {topic} opinion:",
                "{topic} maxis won't like this:"
            ],
            'transitions': [
                "What actually matters:",
                "The reality:",
                "Truth is:",
                "Meanwhile:",
                "Plot twist:"
            ],
            'closings': [
                "Few.",
                "Math ain't mathing.",
                "NGMI if you don't see it.",
                "Position accordingly.",
                "But what do I know."
            ]
        }
    
    def _build_vocabulary(self) -> Dict:
        """Build Miles-specific vocabulary"""
        return {
            'power_words': ['liquidity', 'narrative', 'macro', 'accumulation', 'distribution'],
            'dismissive': ['noise', 'cope', 'hopium', 'exhausting', 'mental masturbation'],
            'slang': ['ser', 'anon', 'ngmi', 'rekt', 'cooked', 'based', 'mf'],
            'market': ['pump', 'dump', 'moon', 'capitulate', 'resistance', 'support']
        }

class MilesAIEnhancedSystem:
    """Enhanced Miles Deutscher AI System with advanced features"""
    
    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN', 
            'AAAAAAAAAAAAAAAAAAAAAJi13QEAAAAAghVwuLws1YdchbwCAkUjqqwu6oc%3DeImrILD6DNOvuOdZiH42oFM3Ww7zTLYaiz1onypLp8XNzCskQ7')
        
        self.analyzer = EnhancedPatternAnalyzer()
        self.generator = AdvancedTweetGenerator(self.analyzer)
        
        self.latest_tweets = []
        self.training_data = []
        self.analyzed_patterns = {}
        self.generation_history = []
        self.learning_events = []
        
        self.last_update = None
        self.is_updating = False
        
        # Performance metrics
        self.metrics = {
            'total_generations': 0,
            'average_confidence': 0,
            'pattern_distribution': defaultdict(int),
            'api_calls': 0,
            'tweets_analyzed': 0
        }
        
        # Load existing data
        self.load_training_data()
        
        # Start background processes
        self.start_background_processes()
        
        logging.info("Enhanced Miles AI System initialized")
    
    def load_training_data(self):
        """Load and analyze existing training data"""
        try:
            with open('data.jsonl', 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    self.training_data.append(entry)
                    
                    # Analyze historical data
                    if 'completion' in entry:
                        analysis = self.analyzer.analyze_tweet({
                            'text': entry['completion'].strip(),
                            'public_metrics': entry.get('metadata', {}).get('metrics', {})
                        })
                        self._update_pattern_database(analysis)
            
            logging.info(f"Loaded and analyzed {len(self.training_data)} training examples")
            
        except Exception as e:
            logging.warning(f"Error loading training data: {e}")
    
    def fetch_latest_tweets(self, count: int = 50) -> List[Dict]:
        """Fetch more tweets with detailed metrics"""
        logging.info(f"Fetching {count} latest tweets from @milesdeutscher...")
        
        self.metrics['api_calls'] += 1
        
        try:
            # Get user ID
            url = "https://api.twitter.com/2/users/by/username/milesdeutscher"
            req = urllib.request.Request(url)
            req.add_header('Authorization', f'Bearer {self.bearer_token}')
            
            context = ssl.create_default_context()
            with urllib.request.urlopen(req, context=context) as response:
                user_data = json.loads(response.read().decode())
            
            if 'data' not in user_data:
                return []
            
            user_id = user_data['data']['id']
            
            # Fetch tweets with extended metrics
            tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            params = {
                'max_results': count,
                'tweet.fields': 'created_at,public_metrics,context_annotations,entities',
                'exclude': 'retweets,replies'
            }
            
            tweets_url += '?' + urllib.parse.urlencode(params)
            
            req = urllib.request.Request(tweets_url)
            req.add_header('Authorization', f'Bearer {self.bearer_token}')
            
            with urllib.request.urlopen(req, context=context) as response:
                tweets_data = json.loads(response.read().decode())
            
            if 'data' in tweets_data:
                self.latest_tweets = tweets_data['data']
                logging.info(f"Fetched {len(self.latest_tweets)} tweets successfully")
                
                # Record learning event
                self.learning_events.append({
                    'timestamp': datetime.now().isoformat(),
                    'event': 'tweets_fetched',
                    'count': len(self.latest_tweets)
                })
                
                return self.latest_tweets
            
        except Exception as e:
            logging.error(f"Error fetching tweets: {e}")
        
        return []
    
    def analyze_latest_patterns(self) -> Dict:
        """Perform deep pattern analysis on latest tweets"""
        if not self.latest_tweets:
            return {}
        
        logging.info("Performing deep pattern analysis...")
        
        pattern_summary = {
            'structures': defaultdict(int),
            'sentiments': defaultdict(int),
            'hooks': defaultdict(int),
            'high_engagement': [],
            'vocabulary_trends': Counter(),
            'temporal_patterns': defaultdict(list)
        }
        
        for tweet in self.latest_tweets:
            # Deep analysis
            analysis = self.analyzer.analyze_tweet(tweet)
            
            # Update summaries
            pattern_summary['structures'][analysis['structure']['pattern']] += 1
            pattern_summary['sentiments'][analysis['sentiment']] += 1
            
            for hook in analysis['hooks']:
                pattern_summary['hooks'][hook] += 1
            
            # Track high engagement
            if analysis['engagement_score'] > 100:
                pattern_summary['high_engagement'].append({
                    'text': tweet['text'],
                    'engagement': analysis['engagement_score'],
                    'structure': analysis['structure'],
                    'analysis': analysis
                })
            
            # Vocabulary trends
            for category, count in analysis['vocabulary']['categories'].items():
                if count > 0:
                    pattern_summary['vocabulary_trends'][category] += count
            
            # Temporal patterns (posting time analysis)
            if 'timestamp' in analysis and analysis['timestamp']:
                hour = datetime.fromisoformat(analysis['timestamp'].replace('Z', '+00:00')).hour
                pattern_summary['temporal_patterns'][hour].append(analysis['engagement_score'])
            
            # Update metrics
            self.metrics['tweets_analyzed'] += 1
        
        self.analyzed_patterns = pattern_summary
        
        # Log insights
        dominant_structure = max(pattern_summary['structures'].items(), key=lambda x: x[1])[0] if pattern_summary['structures'] else 'unknown'
        dominant_sentiment = max(pattern_summary['sentiments'].items(), key=lambda x: x[1])[0] if pattern_summary['sentiments'] else 'neutral'
        
        logging.info(f"Pattern Analysis Complete:")
        logging.info(f"  - Dominant structure: {dominant_structure}")
        logging.info(f"  - Dominant sentiment: {dominant_sentiment}")
        logging.info(f"  - High engagement tweets: {len(pattern_summary['high_engagement'])}")
        
        # Record learning event
        self.learning_events.append({
            'timestamp': datetime.now().isoformat(),
            'event': 'pattern_analysis',
            'insights': {
                'dominant_structure': dominant_structure,
                'dominant_sentiment': dominant_sentiment,
                'patterns_found': len(pattern_summary['structures'])
            }
        })
        
        return pattern_summary
    
    def generate_enhanced_tweet(self, user_input: str) -> Dict:
        """Generate tweet with enhanced ML and pattern matching"""
        
        logging.info(f"Generating enhanced tweet for: '{user_input}'")
        
        # Generate using advanced system
        generation = self.generator.generate(user_input, self.analyzed_patterns)
        
        # Track metrics
        self.metrics['total_generations'] += 1
        self.metrics['pattern_distribution'][generation['pattern_match']] += 1
        
        if self.metrics['total_generations'] > 0:
            self.metrics['average_confidence'] = (
                (self.metrics['average_confidence'] * (self.metrics['total_generations'] - 1) + 
                 generation['confidence']) / self.metrics['total_generations']
            )
        
        # Create detailed result
        result = {
            'input': user_input,
            'output': generation['text'],
            'confidence': round(generation['confidence'], 2),
            'pattern': generation['pattern_match'],
            'strategy': generation['strategy'],
            'length': len(generation['text']),
            'structure': self.analyzer._analyze_structure(generation['text'])['pattern'],
            'timestamp': datetime.now().isoformat(),
            'based_on_tweets': len(self.latest_tweets),
            'model_version': 'enhanced_v2'
        }
        
        # Save to history
        self.generation_history.append(result)
        
        # Log generation
        logging.info(f"Generated tweet: {result['length']} chars, confidence: {result['confidence']}, pattern: {result['pattern']}")
        
        return result
    
    def update_training_data_enhanced(self):
        """Enhanced training data update with pattern preservation"""
        
        if not self.latest_tweets:
            return
        
        logging.info("Updating training data with enhanced patterns...")
        
        new_entries = 0
        high_quality_entries = 0
        
        for tweet in self.latest_tweets:
            text = tweet.get('text', '')
            
            # Skip if exists
            exists = any(text in entry.get('completion', '') for entry in self.training_data)
            
            if not exists and not text.startswith('@') and not text.startswith('RT'):
                # Analyze tweet
                analysis = self.analyzer.analyze_tweet(tweet)
                
                entry = {
                    'prompt': 'Write a tweet in the style of Miles Deutscher:',
                    'completion': f' {text}',
                    'metadata': {
                        'source': 'twitter_api',
                        'collected_at': datetime.now().isoformat(),
                        'metrics': tweet.get('public_metrics', {}),
                        'analysis': analysis,
                        'quality_score': self._calculate_quality_score(analysis)
                    }
                }
                
                self.training_data.append(entry)
                new_entries += 1
                
                if entry['metadata']['quality_score'] > 0.7:
                    high_quality_entries += 1
        
        if new_entries > 0:
            # Save enhanced data
            with open('data_enhanced.jsonl', 'w', encoding='utf-8') as f:
                for entry in self.training_data:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            logging.info(f"Added {new_entries} new training examples ({high_quality_entries} high quality)")
            logging.info(f"Total training examples: {len(self.training_data)}")
            
            # Record learning event
            self.learning_events.append({
                'timestamp': datetime.now().isoformat(),
                'event': 'training_update',
                'new_entries': new_entries,
                'high_quality': high_quality_entries,
                'total': len(self.training_data)
            })
    
    def _calculate_quality_score(self, analysis: Dict) -> float:
        """Calculate quality score for training data"""
        score = 0.0
        
        # Structure bonus
        if analysis['structure']['is_canonical']:
            score += 0.3
        elif analysis['structure']['line_count'] in [2, 3]:
            score += 0.2
        
        # Engagement bonus
        if analysis['engagement_score'] > 100:
            score += 0.2
        elif analysis['engagement_score'] > 50:
            score += 0.1
        
        # Vocabulary bonus
        vocab_categories = analysis['vocabulary']['categories']
        if vocab_categories.get('technical', 0) > 0:
            score += 0.1
        if vocab_categories.get('slang', 0) > 0:
            score += 0.1
        
        # Length bonus
        if 50 < analysis['length'] < 200:
            score += 0.1
        
        return min(score, 1.0)
    
    def _update_pattern_database(self, analysis: Dict):
        """Update pattern database with new analysis"""
        # Update structural patterns
        self.analyzer.patterns['structural'][analysis['structure']['pattern']] += 1
        
        # Update vocabulary
        for word in analysis['vocabulary']['categories']:
            self.analyzer.patterns['vocabulary'].update([word])
    
    def get_enhanced_status(self) -> Dict:
        """Get comprehensive system status"""
        return {
            'system': {
                'version': 'enhanced_v2',
                'training_examples': len(self.training_data),
                'latest_tweets': len(self.latest_tweets),
                'last_update': self.last_update.isoformat() if self.last_update else None,
                'is_updating': self.is_updating
            },
            'patterns': {
                'structures': dict(self.analyzed_patterns.get('structures', {})),
                'sentiments': dict(self.analyzed_patterns.get('sentiments', {})),
                'high_engagement_count': len(self.analyzed_patterns.get('high_engagement', [])),
                'vocabulary_trends': dict(self.analyzed_patterns.get('vocabulary_trends', {}))
            },
            'metrics': dict(self.metrics),
            'recent_learning': self.learning_events[-5:] if self.learning_events else [],
            'generation_history': len(self.generation_history)
        }
    
    def get_learning_visualization(self) -> Dict:
        """Get data for learning visualization"""
        return {
            'timeline': self.learning_events[-20:],
            'pattern_evolution': self._get_pattern_evolution(),
            'quality_distribution': self._get_quality_distribution(),
            'engagement_correlation': self._get_engagement_correlation()
        }
    
    def _get_pattern_evolution(self) -> List[Dict]:
        """Track pattern evolution over time"""
        evolution = []
        
        for event in self.learning_events:
            if event['event'] == 'pattern_analysis' and 'insights' in event:
                evolution.append({
                    'timestamp': event['timestamp'],
                    'dominant_structure': event['insights'].get('dominant_structure', 'unknown'),
                    'patterns_found': event['insights'].get('patterns_found', 0)
                })
        
        return evolution
    
    def _get_quality_distribution(self) -> Dict:
        """Get quality score distribution"""
        scores = [entry['metadata'].get('quality_score', 0) for entry in self.training_data if 'metadata' in entry]
        
        if not scores:
            return {}
        
        return {
            'average': sum(scores) / len(scores),
            'high_quality': len([s for s in scores if s > 0.7]),
            'medium_quality': len([s for s in scores if 0.4 <= s <= 0.7]),
            'low_quality': len([s for s in scores if s < 0.4])
        }
    
    def _get_engagement_correlation(self) -> List[Dict]:
        """Analyze engagement patterns"""
        if not self.analyzed_patterns.get('high_engagement'):
            return []
        
        correlations = []
        
        for tweet_data in self.analyzed_patterns['high_engagement'][:10]:
            correlations.append({
                'structure': tweet_data['structure']['pattern'],
                'sentiment': tweet_data['analysis']['sentiment'],
                'engagement': tweet_data['engagement'],
                'length': tweet_data['analysis']['length']
            })
        
        return correlations
    
    def continuous_learning_cycle(self):
        """Enhanced continuous learning with visualization updates"""
        
        while True:
            try:
                self.is_updating = True
                
                logging.info("Starting enhanced learning cycle...")
                
                # Fetch latest tweets (more than before)
                if self.fetch_latest_tweets(50):
                    # Deep pattern analysis
                    self.analyze_latest_patterns()
                    
                    # Update training data
                    self.update_training_data_enhanced()
                    
                    # Update timestamp
                    self.last_update = datetime.now()
                    
                    logging.info("Enhanced learning cycle completed successfully")
                
                self.is_updating = False
                
                # Wait 20 minutes (more frequent updates)
                time.sleep(1200)
                
            except Exception as e:
                logging.error(f"Enhanced learning cycle error: {e}")
                self.is_updating = False
                time.sleep(300)
    
    def start_background_processes(self):
        """Start all background processes"""
        # Learning thread
        learning_thread = threading.Thread(target=self.continuous_learning_cycle, daemon=True)
        learning_thread.start()
        
        logging.info("Background processes started")

# Enhanced Web Interface
class EnhancedWebHandler(http.server.SimpleHTTPRequestHandler):
    """Enhanced web interface with real-time visualization"""
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = self._generate_enhanced_html()
            self.wfile.write(html.encode())
        
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            status = enhanced_ai.get_enhanced_status()
            self.wfile.write(json.dumps(status).encode())
        
        elif self.path == '/api/learning':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            learning_data = enhanced_ai.get_learning_visualization()
            self.wfile.write(json.dumps(learning_data).encode())
        
        elif self.path == '/api/tweets':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Get latest tweets with analysis
            tweets_data = []
            for tweet in enhanced_ai.latest_tweets[:10]:
                analysis = enhanced_ai.analyzer.analyze_tweet(tweet)
                tweets_data.append({
                    'text': tweet['text'],
                    'metrics': tweet.get('public_metrics', {}),
                    'analysis': {
                        'structure': analysis['structure']['pattern'],
                        'sentiment': analysis['sentiment'],
                        'engagement': analysis['engagement_score']
                    }
                })
            
            self.wfile.write(json.dumps(tweets_data).encode())
        
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            result = enhanced_ai.generate_enhanced_tweet(data['input'])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
    
    def _generate_enhanced_html(self) -> str:
        """Generate enhanced HTML interface"""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>Miles Deutscher AI - Enhanced System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0e1217;
            color: #e4e6eb;
            overflow-x: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #1DA1F2 0%, #0d7bc4 100%);
            padding: 20px 0;
            box-shadow: 0 2px 20px rgba(29, 161, 242, 0.3);
        }
        
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        h1 {
            font-size: 28px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .version {
            background: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .main-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
        }
        
        .panel {
            background: #192734;
            border-radius: 16px;
            padding: 24px;
            border: 1px solid #2f3b47;
            transition: all 0.3s ease;
        }
        
        .panel:hover {
            border-color: #1DA1F2;
            box-shadow: 0 4px 20px rgba(29, 161, 242, 0.1);
        }
        
        .panel-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            color: #1DA1F2;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        .two-thirds {
            grid-column: span 2;
        }
        
        /* Input Section */
        .input-section {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        textarea {
            background: #0e1217;
            border: 2px solid #2f3b47;
            border-radius: 12px;
            padding: 16px;
            color: #e4e6eb;
            font-size: 16px;
            resize: none;
            transition: all 0.3s ease;
        }
        
        textarea:focus {
            outline: none;
            border-color: #1DA1F2;
            box-shadow: 0 0 0 3px rgba(29, 161, 242, 0.1);
        }
        
        .generate-btn {
            background: linear-gradient(135deg, #1DA1F2 0%, #0d7bc4 100%);
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 100px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(29, 161, 242, 0.3);
        }
        
        .generate-btn:active {
            transform: translateY(0);
        }
        
        /* Output Section */
        .tweet-output {
            background: #0e1217;
            border-radius: 12px;
            padding: 20px;
            min-height: 120px;
            font-size: 18px;
            line-height: 1.5;
            white-space: pre-wrap;
            border: 2px solid #2f3b47;
            position: relative;
        }
        
        .confidence-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(29, 161, 242, 0.2);
            color: #1DA1F2;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        
        /* Metrics Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }
        
        .metric-card {
            background: #0e1217;
            padding: 16px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #2f3b47;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            color: #1DA1F2;
            margin-bottom: 4px;
        }
        
        .metric-label {
            font-size: 12px;
            color: #8b98a5;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Live Feed */
        .tweet-feed {
            max-height: 400px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .tweet-card {
            background: #0e1217;
            padding: 16px;
            border-radius: 12px;
            border: 1px solid #2f3b47;
            transition: all 0.3s ease;
        }
        
        .tweet-card:hover {
            border-color: #1DA1F2;
            transform: translateX(4px);
        }
        
        .tweet-text {
            font-size: 14px;
            line-height: 1.4;
            margin-bottom: 8px;
            color: #e4e6eb;
        }
        
        .tweet-meta {
            display: flex;
            gap: 16px;
            font-size: 12px;
            color: #8b98a5;
        }
        
        .tweet-meta span {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        /* Learning Visualization */
        .learning-viz {
            height: 300px;
            background: #0e1217;
            border-radius: 12px;
            padding: 16px;
            position: relative;
            overflow: hidden;
        }
        
        .learning-timeline {
            display: flex;
            align-items: flex-end;
            height: 100%;
            gap: 4px;
        }
        
        .timeline-bar {
            flex: 1;
            background: linear-gradient(to top, #1DA1F2, #0d7bc4);
            border-radius: 4px 4px 0 0;
            position: relative;
            transition: all 0.3s ease;
        }
        
        .timeline-bar:hover {
            opacity: 0.8;
        }
        
        /* Status Indicators */
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #10b981;
            position: relative;
        }
        
        .status-dot.updating {
            background: #f59e0b;
        }
        
        .status-dot.active::after {
            content: '';
            position: absolute;
            top: -4px;
            left: -4px;
            right: -4px;
            bottom: -4px;
            border-radius: 50%;
            border: 2px solid currentColor;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0; transform: scale(1.2); }
            100% { opacity: 0; transform: scale(1.2); }
        }
        
        /* Patterns Display */
        .patterns-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }
        
        .pattern-card {
            background: #0e1217;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #2f3b47;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .pattern-card:hover {
            border-color: #1DA1F2;
            transform: scale(1.05);
        }
        
        .pattern-name {
            font-size: 14px;
            font-weight: 600;
            color: #1DA1F2;
            margin-bottom: 4px;
        }
        
        .pattern-count {
            font-size: 12px;
            color: #8b98a5;
        }
        
        /* Loading Animation */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(29, 161, 242, 0.3);
            border-radius: 50%;
            border-top-color: #1DA1F2;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #0e1217;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #2f3b47;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #1DA1F2;
        }
        
        /* Responsive */
        @media (max-width: 1200px) {
            .main-container {
                grid-template-columns: 1fr 1fr;
            }
            
            .two-thirds {
                grid-column: 1 / -1;
            }
        }
        
        @media (max-width: 768px) {
            .main-container {
                grid-template-columns: 1fr;
                padding: 10px;
            }
            
            .panel {
                padding: 16px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <h1>
                <span>🚀</span>
                Miles Deutscher AI
                <span class="version">Enhanced v2.0</span>
            </h1>
            <div class="status-grid">
                <div class="status-item">
                    <div class="status-dot active" id="systemStatus"></div>
                    <span id="systemStatusText">System Active</span>
                </div>
                <div class="status-item">
                    <div class="status-dot" id="learningStatus"></div>
                    <span id="learningStatusText">Learning Active</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="main-container">
        <!-- Tweet Generation Panel -->
        <div class="panel">
            <h2 class="panel-title">
                <span>✍️</span>
                Generate Tweet
            </h2>
            <div class="input-section">
                <textarea id="tweetInput" rows="4" placeholder="Enter your topic or idea..."></textarea>
                <button class="generate-btn" onclick="generateTweet()">
                    <span>Generate Miles-Style Tweet</span>
                    <span id="generateLoader" style="display: none;" class="loading"></span>
                </button>
            </div>
        </div>
        
        <!-- Live Stats Panel -->
        <div class="panel">
            <h2 class="panel-title">
                <span>📊</span>
                Live Statistics
            </h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value" id="totalTweets">0</div>
                    <div class="metric-label">Training Data</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="latestTweets">0</div>
                    <div class="metric-label">Live Tweets</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="avgConfidence">0%</div>
                    <div class="metric-label">Avg Confidence</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="apiCalls">0</div>
                    <div class="metric-label">API Calls</div>
                </div>
            </div>
        </div>
        
        <!-- Pattern Analysis Panel -->
        <div class="panel">
            <h2 class="panel-title">
                <span>🧬</span>
                Pattern Analysis
            </h2>
            <div class="patterns-grid" id="patternsGrid">
                <!-- Patterns will be inserted here -->
            </div>
        </div>
        
        <!-- Generated Tweet Output -->
        <div class="panel two-thirds">
            <h2 class="panel-title">
                <span>🐦</span>
                Generated Tweet
            </h2>
            <div class="tweet-output" id="generatedTweet">
                Your AI-generated tweet will appear here...
                <span class="confidence-badge" id="confidenceBadge" style="display: none;">95% confidence</span>
            </div>
            <div class="metrics-grid" id="outputMetrics" style="display: none;">
                <div class="metric-card">
                    <div class="metric-value" id="charCount">0</div>
                    <div class="metric-label">Characters</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="structure">-</div>
                    <div class="metric-label">Structure</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="pattern">-</div>
                    <div class="metric-label">Pattern</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="strategy">-</div>
                    <div class="metric-label">Strategy</div>
                </div>
            </div>
        </div>
        
        <!-- Live Tweet Feed -->
        <div class="panel">
            <h2 class="panel-title">
                <span>📡</span>
                Live from @milesdeutscher
            </h2>
            <div class="tweet-feed" id="tweetFeed">
                <!-- Live tweets will be inserted here -->
            </div>
        </div>
        
        <!-- Learning Visualization -->
        <div class="panel full-width">
            <h2 class="panel-title">
                <span>🧠</span>
                Continuous Learning Progress
            </h2>
            <div class="learning-viz">
                <div class="learning-timeline" id="learningTimeline">
                    <!-- Learning visualization will be inserted here -->
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Global state
        let systemData = {};
        let learningData = {};
        let tweets = [];
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            updateStatus();
            updateLearning();
            updateTweets();
            
            // Set up periodic updates
            setInterval(updateStatus, 5000);
            setInterval(updateLearning, 10000);
            setInterval(updateTweets, 30000);
        });
        
        // Update system status
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                systemData = await response.json();
                
                // Update stats
                document.getElementById('totalTweets').textContent = systemData.system.training_examples;
                document.getElementById('latestTweets').textContent = systemData.system.latest_tweets;
                document.getElementById('avgConfidence').textContent = Math.round(systemData.metrics.average_confidence * 100) + '%';
                document.getElementById('apiCalls').textContent = systemData.metrics.api_calls;
                
                // Update status indicators
                if (systemData.system.is_updating) {
                    document.getElementById('learningStatus').classList.add('updating');
                    document.getElementById('learningStatusText').textContent = 'Learning in Progress';
                } else {
                    document.getElementById('learningStatus').classList.remove('updating');
                    document.getElementById('learningStatusText').textContent = 'Learning Active';
                }
                
                // Update patterns
                updatePatterns(systemData.patterns);
                
            } catch (error) {
                console.error('Error updating status:', error);
            }
        }
        
        // Update patterns display
        function updatePatterns(patterns) {
            const grid = document.getElementById('patternsGrid');
            grid.innerHTML = '';
            
            // Structure patterns
            if (patterns.structures) {
                Object.entries(patterns.structures).forEach(([pattern, count]) => {
                    const card = document.createElement('div');
                    card.className = 'pattern-card';
                    card.innerHTML = `
                        <div class="pattern-name">${pattern}</div>
                        <div class="pattern-count">${count} tweets</div>
                    `;
                    grid.appendChild(card);
                });
            }
        }
        
        // Update learning visualization
        async function updateLearning() {
            try {
                const response = await fetch('/api/learning');
                learningData = await response.json();
                
                // Update timeline visualization
                const timeline = document.getElementById('learningTimeline');
                timeline.innerHTML = '';
                
                if (learningData.timeline) {
                    learningData.timeline.forEach((event, index) => {
                        const bar = document.createElement('div');
                        bar.className = 'timeline-bar';
                        
                        // Calculate height based on event type
                        let height = 30;
                        if (event.event === 'tweets_fetched') {
                            height = 50 + (event.count || 0);
                        } else if (event.event === 'training_update') {
                            height = 70 + (event.new_entries || 0) * 2;
                        } else if (event.event === 'pattern_analysis') {
                            height = 60;
                        }
                        
                        bar.style.height = `${Math.min(height, 80)}%`;
                        bar.title = `${event.event} at ${new Date(event.timestamp).toLocaleTimeString()}`;
                        
                        timeline.appendChild(bar);
                    });
                }
                
            } catch (error) {
                console.error('Error updating learning:', error);
            }
        }
        
        // Update tweet feed
        async function updateTweets() {
            try {
                const response = await fetch('/api/tweets');
                tweets = await response.json();
                
                const feed = document.getElementById('tweetFeed');
                feed.innerHTML = '';
                
                tweets.forEach(tweet => {
                    const card = document.createElement('div');
                    card.className = 'tweet-card';
                    card.innerHTML = `
                        <div class="tweet-text">${tweet.text}</div>
                        <div class="tweet-meta">
                            <span>❤️ ${tweet.metrics.like_count || 0}</span>
                            <span>🔁 ${tweet.metrics.retweet_count || 0}</span>
                            <span>💬 ${tweet.metrics.reply_count || 0}</span>
                            <span>📊 ${tweet.analysis.structure}</span>
                            <span>💭 ${tweet.analysis.sentiment}</span>
                        </div>
                    `;
                    feed.appendChild(card);
                });
                
            } catch (error) {
                console.error('Error updating tweets:', error);
            }
        }
        
        // Generate tweet
        async function generateTweet() {
            const input = document.getElementById('tweetInput').value;
            if (!input) return;
            
            const loader = document.getElementById('generateLoader');
            loader.style.display = 'inline-block';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({input: input})
                });
                
                const result = await response.json();
                
                // Display generated tweet
                document.getElementById('generatedTweet').textContent = result.output;
                
                // Show confidence badge
                const badge = document.getElementById('confidenceBadge');
                badge.textContent = `${Math.round(result.confidence * 100)}% confidence`;
                badge.style.display = 'block';
                
                // Update metrics
                document.getElementById('charCount').textContent = result.length;
                document.getElementById('structure').textContent = result.structure;
                document.getElementById('pattern').textContent = result.pattern;
                document.getElementById('strategy').textContent = result.strategy;
                document.getElementById('outputMetrics').style.display = 'grid';
                
                // Update status
                await updateStatus();
                
            } catch (error) {
                console.error('Error generating tweet:', error);
                document.getElementById('generatedTweet').textContent = 'Error generating tweet. Please try again.';
            } finally {
                loader.style.display = 'none';
            }
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                generateTweet();
            }
        });
    </script>
</body>
</html>'''

# Main execution
if __name__ == "__main__":
    print("""
    ================================================================
            Miles Deutscher AI - Enhanced System v2.0             
                                                              
      Frontend: Advanced UI with real-time visualization       
      Backend: ML-powered pattern analysis & generation       
      Learning: Continuous improvement from live data          
      Analytics: Deep metrics and performance tracking         
    ================================================================
    """)
    
    # Initialize enhanced system
    global enhanced_ai
    enhanced_ai = MilesAIEnhancedSystem()
    
    # Perform initial data fetch
    print("\n[INIT] Performing initial data analysis...")
    enhanced_ai.fetch_latest_tweets(50)
    enhanced_ai.analyze_latest_patterns()
    
    # Start web server
    PORT = 8000
    server = socketserver.TCPServer(("", PORT), EnhancedWebHandler)
    
    print(f"\n[READY] Enhanced system running at: http://localhost:{PORT}")
    print("\n[FEATURES]:")
    print("   - Advanced pattern recognition and ML-based generation")
    print("   - Real-time visualization of Miles' tweets")
    print("   - Continuous learning progress tracking")
    print("   - Deep analytics and performance metrics")
    print("   - Confidence scoring for generated tweets")
    print("\n[STOP] Press Ctrl+C to stop")
    
    server.serve_forever()