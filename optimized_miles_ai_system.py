"""
Miles Deutscher AI - Optimized High-Performance System
Performance Improvements:
1. Redis caching for sub-100ms response times
2. Asynchronous processing with asyncio
3. Connection pooling and optimized database queries
4. API request batching and intelligent rate limiting
5. Memory-efficient pattern analysis with memoization
6. Background processing queue system
7. Real-time performance monitoring
"""

import os
import json
import time
import asyncio
import aiohttp
import aioredis
import threading
from datetime import datetime, timedelta
from collections import defaultdict, Counter, deque
from typing import Dict, List, Optional, Tuple, Set
import hashlib
import logging
from functools import lru_cache, wraps
import sqlite3
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import weakref
import gc
import psutil
from dataclasses import dataclass, asdict
import pickle
from contextlib import asynccontextmanager

# Enhanced logging with performance metrics
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(process)d] %(message)s',
    handlers=[
        logging.FileHandler('optimized_miles_ai.log'),
        logging.StreamHandler()
    ]
)

# Performance monitoring decorator
def monitor_performance(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            duration = (time.perf_counter() - start_time) * 1000
            logging.info(f"{func.__name__}: {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logging.error(f"{func.__name__} failed after {duration:.2f}ms: {e}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            duration = (time.perf_counter() - start_time) * 1000
            logging.info(f"{func.__name__}: {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logging.error(f"{func.__name__} failed after {duration:.2f}ms: {e}")
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper

@dataclass
class TweetData:
    """Optimized tweet data structure"""
    id: str
    text: str
    created_at: str
    metrics: Dict[str, int]
    analysis_hash: str = None
    
    def __post_init__(self):
        if not self.analysis_hash:
            self.analysis_hash = hashlib.sha256(self.text.encode()).hexdigest()[:16]

class OptimizedCache:
    """High-performance caching layer with Redis fallback"""
    
    def __init__(self):
        self.memory_cache = {}
        self.cache_stats = {'hits': 0, 'misses': 0}
        self.max_memory_items = 1000
        self.redis_client = None
        
    async def init_redis(self):
        """Initialize Redis connection with connection pooling"""
        try:
            self.redis_client = aioredis.from_url(
                "redis://localhost", 
                encoding="utf-8", 
                decode_responses=True,
                max_connections=20
            )
            await self.redis_client.ping()
            logging.info("Redis cache initialized successfully")
        except Exception as e:
            logging.warning(f"Redis unavailable, using memory cache only: {e}")
    
    @monitor_performance
    async def get(self, key: str) -> Optional[any]:
        """Get from cache with memory-first strategy"""
        # Check memory cache first (fastest)
        if key in self.memory_cache:
            self.cache_stats['hits'] += 1
            return self.memory_cache[key]
        
        # Check Redis cache
        if self.redis_client:
            try:
                cached = await self.redis_client.get(f"miles_ai:{key}")
                if cached:
                    value = json.loads(cached)
                    # Store in memory cache for next access
                    self._store_memory(key, value)
                    self.cache_stats['hits'] += 1
                    return value
            except Exception as e:
                logging.warning(f"Redis get error: {e}")
        
        self.cache_stats['misses'] += 1
        return None
    
    @monitor_performance
    async def set(self, key: str, value: any, expire_seconds: int = 3600):
        """Set in both memory and Redis cache"""
        # Store in memory cache
        self._store_memory(key, value)
        
        # Store in Redis with expiration
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"miles_ai:{key}", 
                    expire_seconds, 
                    json.dumps(value, default=str)
                )
            except Exception as e:
                logging.warning(f"Redis set error: {e}")
    
    def _store_memory(self, key: str, value: any):
        """Store in memory cache with size management"""
        if len(self.memory_cache) >= self.max_memory_items:
            # Remove oldest items (simple FIFO)
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = value
    
    def get_stats(self) -> Dict:
        """Get cache performance statistics"""
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total * 100) if total > 0 else 0
        
        return {
            'hit_rate': round(hit_rate, 2),
            'memory_items': len(self.memory_cache),
            'redis_connected': self.redis_client is not None
        }

class OptimizedDatabaseManager:
    """High-performance database operations with connection pooling"""
    
    def __init__(self, db_path: str = "miles_ai_optimized.db"):
        self.db_path = db_path
        self.connection_pool = []
        self.pool_size = 10
        self._init_database()
    
    def _init_database(self):
        """Initialize database with optimized schema and indexes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Optimized schema with indexes
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS tweets (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                metrics TEXT NOT NULL,
                analysis_hash TEXT NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_tweets_created_at ON tweets(created_at);
            CREATE INDEX IF NOT EXISTS idx_tweets_analysis_hash ON tweets(analysis_hash);
            CREATE INDEX IF NOT EXISTS idx_tweets_processed_at ON tweets(processed_at);
            
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);
            CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON patterns(confidence);
            
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=NORMAL;
            PRAGMA cache_size=10000;
            PRAGMA temp_store=MEMORY;
        """)
        
        conn.commit()
        conn.close()
        
        # Initialize connection pool
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.connection_pool.append(conn)
        
        logging.info(f"Database initialized with {self.pool_size} connections")
    
    @monitor_performance
    def get_connection(self):
        """Get connection from pool"""
        if self.connection_pool:
            return self.connection_pool.pop()
        else:
            # Create new connection if pool is empty
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
    
    def return_connection(self, conn):
        """Return connection to pool"""
        if len(self.connection_pool) < self.pool_size:
            self.connection_pool.append(conn)
        else:
            conn.close()
    
    @monitor_performance
    def batch_insert_tweets(self, tweets: List[TweetData]) -> int:
        """Batch insert tweets for optimal performance"""
        if not tweets:
            return 0
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Prepare batch data
            tweet_data = []
            for tweet in tweets:
                tweet_data.append((
                    tweet.id,
                    tweet.text,
                    tweet.created_at,
                    json.dumps(tweet.metrics),
                    tweet.analysis_hash
                ))
            
            # Batch insert with ON CONFLICT IGNORE for duplicates
            cursor.executemany("""
                INSERT OR IGNORE INTO tweets 
                (id, text, created_at, metrics, analysis_hash)
                VALUES (?, ?, ?, ?, ?)
            """, tweet_data)
            
            rows_inserted = cursor.rowcount
            conn.commit()
            
            logging.info(f"Batch inserted {rows_inserted} tweets")
            return rows_inserted
            
        finally:
            self.return_connection(conn)
    
    @monitor_performance
    def get_recent_tweets(self, limit: int = 100) -> List[Dict]:
        """Get recent tweets with optimized query"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tweets 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            tweets = [dict(row) for row in cursor.fetchall()]
            return tweets
            
        finally:
            self.return_connection(conn)

class OptimizedRateLimiter:
    """Intelligent rate limiter with exponential backoff"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_times = deque()
        self.backoff_until = None
        self.backoff_factor = 1.5
        self.max_backoff = 300  # 5 minutes
    
    async def acquire(self):
        """Acquire permission to make request with intelligent backoff"""
        now = time.time()
        
        # Check if we're in backoff period
        if self.backoff_until and now < self.backoff_until:
            wait_time = self.backoff_until - now
            logging.info(f"Rate limit backoff: waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        
        # Clean old requests (older than 1 minute)
        while self.request_times and now - self.request_times[0] > 60:
            self.request_times.popleft()
        
        # Check if we can make request
        if len(self.request_times) >= self.requests_per_minute:
            # Calculate wait time
            oldest_request = self.request_times[0]
            wait_time = 60 - (now - oldest_request)
            
            if wait_time > 0:
                logging.info(f"Rate limit: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        # Add current request
        self.request_times.append(now)
    
    def set_backoff(self, seconds: int):
        """Set backoff period for rate limit errors"""
        backoff_time = min(seconds * self.backoff_factor, self.max_backoff)
        self.backoff_until = time.time() + backoff_time
        logging.warning(f"Rate limit hit, backing off for {backoff_time:.1f}s")

class OptimizedPatternAnalyzer:
    """High-performance pattern analysis with memoization"""
    
    def __init__(self):
        self.pattern_cache = {}
        self.analysis_stats = defaultdict(int)
        self.weak_refs = weakref.WeakValueDictionary()
    
    @lru_cache(maxsize=1000)
    def _analyze_structure_cached(self, text_hash: str, text: str) -> Dict:
        """Cached structure analysis"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        structure = {
            'line_count': len(lines),
            'pattern': f"{len(lines)}_part",
            'has_question': '?' in text,
            'has_statement': any(line.endswith('.') for line in lines),
            'avg_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0
        }
        
        # Detect canonical patterns
        if len(lines) == 3:
            structure['is_canonical'] = True
            structure['canonical_type'] = 'dismiss_focus_reality'
        
        return structure
    
    @lru_cache(maxsize=500)
    def _analyze_sentiment_cached(self, text_hash: str, text: str) -> str:
        """Cached sentiment analysis"""
        text_lower = text.lower()
        
        bullish_words = {'bullish', 'pump', 'moon', 'fire', 'based', 'up', 'bull'}
        bearish_words = {'bearish', 'dump', 'rekt', 'cooked', 'down', 'bear', 'crash'}
        neutral_words = {'noise', 'chop', 'range', 'sideways'}
        
        bullish_count = sum(1 for word in bullish_words if word in text_lower)
        bearish_count = sum(1 for word in bearish_words if word in text_lower)
        neutral_count = sum(1 for word in neutral_words if word in text_lower)
        
        if '?' in text:
            return 'questioning'
        elif bullish_count > bearish_count and bullish_count > neutral_count:
            return 'bullish'
        elif bearish_count > bullish_count and bearish_count > neutral_count:
            return 'bearish'
        elif neutral_count > 0:
            return 'neutral'
        else:
            return 'philosophical'
    
    @monitor_performance
    def analyze_tweet_batch(self, tweets: List[TweetData]) -> List[Dict]:
        """Batch analyze tweets for optimal performance"""
        results = []
        cache_hits = 0
        
        for tweet in tweets:
            # Check cache first
            cache_key = f"analysis_{tweet.analysis_hash}"
            if cache_key in self.pattern_cache:
                results.append(self.pattern_cache[cache_key])
                cache_hits += 1
                continue
            
            # Perform analysis
            analysis = {
                'structure': self._analyze_structure_cached(tweet.analysis_hash, tweet.text),
                'sentiment': self._analyze_sentiment_cached(tweet.analysis_hash, tweet.text),
                'length': len(tweet.text),
                'engagement_score': self._calculate_engagement(tweet.metrics),
                'vocabulary': self._analyze_vocabulary(tweet.text),
                'timestamp': tweet.created_at
            }
            
            # Cache result
            self.pattern_cache[cache_key] = analysis
            results.append(analysis)
        
        # Update stats
        self.analysis_stats['total_analyzed'] += len(tweets)
        self.analysis_stats['cache_hits'] += cache_hits
        
        logging.info(f"Analyzed {len(tweets)} tweets, {cache_hits} cache hits")
        return results
    
    def _calculate_engagement(self, metrics: Dict) -> float:
        """Calculate weighted engagement score"""
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        quotes = metrics.get('quote_count', 0)
        
        return (likes * 1) + (retweets * 2.5) + (replies * 1.5) + (quotes * 3)
    
    @lru_cache(maxsize=200)
    def _analyze_vocabulary(self, text: str) -> Dict:
        """Cached vocabulary analysis"""
        words = text.lower().split()
        
        # Miles-specific vocabulary categories
        categories = {
            'technical': ['liquidity', 'macro', 'narrative', 'accumulation', 'resistance'],
            'slang': ['ser', 'anon', 'ngmi', 'gm', 'rekt', 'cooked', 'based'],
            'action': ['pump', 'dump', 'moon', 'capitulate', 'accumulate'],
            'dismissive': ['noise', 'chop', 'cope', 'few']
        }
        
        vocab_analysis = {
            'total_words': len(words),
            'unique_words': len(set(words)),
            'categories': {}
        }
        
        for category, keywords in categories.items():
            vocab_analysis['categories'][category] = sum(1 for word in words if word in keywords)
        
        return vocab_analysis
    
    def get_stats(self) -> Dict:
        """Get analyzer performance statistics"""
        return dict(self.analysis_stats)

class OptimizedTwitterClient:
    """High-performance Twitter API client with async requests and batching"""
    
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token
        self.rate_limiter = OptimizedRateLimiter(requests_per_minute=50)  # Conservative limit
        self.session = None
    
    async def init_session(self):
        """Initialize aiohttp session with optimized settings"""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=10,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={'Authorization': f'Bearer {self.bearer_token}'}
        )
        
        logging.info("Twitter API session initialized")
    
    @monitor_performance
    async def fetch_user_tweets_batch(self, username: str, count: int = 50) -> List[TweetData]:
        """Fetch tweets with optimized batching and error handling"""
        if not self.session:
            await self.init_session()
        
        try:
            # Rate limiting
            await self.rate_limiter.acquire()
            
            # Get user ID first
            user_url = f"https://api.twitter.com/2/users/by/username/{username}"
            
            async with self.session.get(user_url) as response:
                if response.status == 429:
                    self.rate_limiter.set_backoff(60)
                    raise Exception("Rate limit exceeded")
                
                response.raise_for_status()
                user_data = await response.json()
            
            if 'data' not in user_data:
                raise Exception(f"User {username} not found")
            
            user_id = user_data['data']['id']
            
            # Fetch tweets with comprehensive fields
            await self.rate_limiter.acquire()
            
            tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            params = {
                'max_results': min(count, 100),  # API limit
                'tweet.fields': 'created_at,public_metrics,context_annotations,entities,author_id',
                'exclude': 'retweets,replies',
                'expansions': 'author_id'
            }
            
            async with self.session.get(tweets_url, params=params) as response:
                if response.status == 429:
                    self.rate_limiter.set_backoff(60)
                    raise Exception("Rate limit exceeded")
                
                response.raise_for_status()
                tweets_data = await response.json()
            
            if 'data' not in tweets_data:
                return []
            
            # Convert to optimized data structures
            tweets = []
            for tweet_raw in tweets_data['data']:
                tweet = TweetData(
                    id=tweet_raw['id'],
                    text=tweet_raw['text'],
                    created_at=tweet_raw['created_at'],
                    metrics=tweet_raw.get('public_metrics', {})
                )
                tweets.append(tweet)
            
            logging.info(f"Fetched {len(tweets)} tweets for @{username}")
            return tweets
        
        except Exception as e:
            logging.error(f"Error fetching tweets for @{username}: {e}")
            return []
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()

class OptimizedTweetGenerator:
    """High-performance tweet generation with pattern optimization"""
    
    def __init__(self):
        self.generation_cache = {}
        self.template_weights = defaultdict(float)
        self.pattern_templates = self._load_optimized_templates()
    
    @monitor_performance
    def generate_optimized(self, input_text: str, patterns: Dict) -> Dict:
        """Generate tweet with optimized pattern matching"""
        # Cache key for similar inputs
        input_hash = hashlib.sha256(input_text.encode()).hexdigest()[:16]
        cache_key = f"gen_{input_hash}_{len(patterns)}"
        
        if cache_key in self.generation_cache:
            cached = self.generation_cache[cache_key].copy()
            cached['from_cache'] = True
            return cached
        
        # Analyze input for generation strategy
        strategy = self._determine_strategy(input_text, patterns)
        
        # Generate based on strategy
        if strategy == 'philosophical':
            tweet = self._generate_philosophical_optimized(input_text, patterns)
        elif strategy == 'bullish':
            tweet = self._generate_market_optimized(input_text, patterns, 'bullish')
        elif strategy == 'bearish':
            tweet = self._generate_market_optimized(input_text, patterns, 'bearish')
        elif strategy == 'question':
            tweet = self._generate_question_optimized(input_text, patterns)
        else:
            tweet = self._generate_adaptive_optimized(input_text, patterns)
        
        # Calculate confidence score
        confidence = self._calculate_generation_confidence(tweet, patterns)
        
        result = {
            'text': tweet,
            'strategy': strategy,
            'confidence': confidence,
            'length': len(tweet),
            'pattern_match': self._identify_pattern(tweet),
            'generation_time': time.time(),
            'from_cache': False
        }
        
        # Cache result
        self.generation_cache[cache_key] = result.copy()
        
        return result
    
    def _determine_strategy(self, input_text: str, patterns: Dict) -> str:
        """Determine optimal generation strategy"""
        text_lower = input_text.lower()
        
        # Strategy priority based on patterns
        if '?' in input_text:
            return 'question'
        elif any(word in text_lower for word in ['bull', 'pump', 'moon', 'up']):
            return 'bullish'
        elif any(word in text_lower for word in ['bear', 'dump', 'crash', 'down']):
            return 'bearish'
        elif len(input_text) > 30:
            return 'philosophical'
        else:
            return 'adaptive'
    
    def _generate_philosophical_optimized(self, input_text: str, patterns: Dict) -> str:
        """Generate philosophical tweet with pattern optimization"""
        concept = self._extract_key_concept(input_text)
        
        # Use high-performing patterns if available
        if patterns and patterns.get('high_engagement'):
            # Base on successful patterns
            successful_structures = [t for t in patterns['high_engagement'] 
                                   if t.get('structure', {}).get('line_count') == 3]
            
            if successful_structures:
                template = self._adapt_successful_pattern(successful_structures[0], concept)
                return template
        
        # Default optimized templates
        templates = [
            f"The {concept} narrative is exhausting.\n\nWhat matters: positioning for the next cycle.\n\nUntil then? We trade the range.",
            f"Everyone obsessing over {concept} misses the point.\n\nReal alpha: understanding liquidity flows.\n\nFew get this.",
            f"{concept.capitalize()} debates are noise.\n\nFocus: macro trends, positioning, risk management.\n\nEverything else is distraction."
        ]
        
        return templates[hash(input_text) % len(templates)]
    
    def _generate_market_optimized(self, input_text: str, patterns: Dict, sentiment: str) -> str:
        """Generate market sentiment tweet with optimization"""
        ticker = self._extract_ticker(input_text) or "the market"
        
        if sentiment == 'bullish':
            templates = [
                f"{ticker} looking absolutely fire.\n\nClean break, volume confirmation.\n\nThis is it.",
                f"Ser, {ticker} about to melt faces.\n\nAccumulation complete.\n\nPosition accordingly.",
                f"{ticker} chart telling a story.\n\nHigher lows, building momentum.\n\nUp only."
            ]
        else:  # bearish
            templates = [
                f"{ticker} showing major weakness.\n\nSupport broken, no buyers.\n\nProtect capital.",
                f"Warning: {ticker} looking cooked.\n\nMomentum fading fast.\n\nThis isn't the dip.",
                f"{ticker} about to get rekt.\n\nBears in control.\n\nDon't catch knives."
            ]
        
        return templates[hash(input_text) % len(templates)]
    
    def _generate_question_optimized(self, input_text: str, patterns: Dict) -> str:
        """Generate optimized question response"""
        templates = [
            f"{input_text}\n\nThe answer is always liquidity.",
            f"{input_text}\n\nAnon, you already know.",
            f"{input_text}\n\nYes, but timing matters."
        ]
        
        return templates[hash(input_text) % len(templates)]
    
    def _generate_adaptive_optimized(self, input_text: str, patterns: Dict) -> str:
        """Generate adaptive tweet based on current patterns"""
        if patterns and patterns.get('structures'):
            dominant_pattern = max(patterns['structures'].items(), key=lambda x: x[1])[0]
            
            if '3_part' in dominant_pattern:
                return self._generate_philosophical_optimized(input_text, patterns)
        
        # Default quick response
        return f"{input_text}\n\nFew understand this."
    
    def _extract_key_concept(self, text: str) -> str:
        """Extract key concept for template generation"""
        # Remove common words and extract meaningful concept
        stopwords = {'the', 'is', 'are', 'was', 'were', 'been', 'have', 'has', 'had'}
        words = [w for w in text.lower().split() if w not in stopwords and len(w) > 2]
        
        if len(words) >= 2:
            return ' '.join(words[:2])
        elif words:
            return words[0]
        else:
            return 'market dynamics'
    
    def _extract_ticker(self, text: str) -> Optional[str]:
        """Extract ticker symbol"""
        import re
        match = re.search(r'\$?([A-Z]{2,5})\b', text.upper())
        return f"${match.group(1)}" if match else None
    
    def _calculate_generation_confidence(self, tweet: str, patterns: Dict) -> float:
        """Calculate confidence score for generated tweet"""
        confidence = 0.6  # Base confidence
        
        # Length bonus
        if 50 <= len(tweet) <= 250:
            confidence += 0.1
        
        # Structure bonus
        lines = tweet.split('\n')
        if len(lines) == 3:
            confidence += 0.15
        
        # Pattern alignment bonus
        if patterns and patterns.get('structures'):
            dominant = max(patterns['structures'].items(), key=lambda x: x[1])[0]
            if f"{len(lines)}_part" == dominant:
                confidence += 0.1
        
        # Vocabulary bonus
        miles_words = ['liquidity', 'narrative', 'few', 'ser', 'anon', 'ngmi', 'based']
        word_count = sum(1 for word in miles_words if word.lower() in tweet.lower())
        confidence += min(word_count * 0.05, 0.15)
        
        return min(confidence, 1.0)
    
    def _identify_pattern(self, tweet: str) -> str:
        """Identify the pattern used in generated tweet"""
        lines = tweet.split('\n')
        line_count = len([line for line in lines if line.strip()])
        
        if line_count == 3:
            return "canonical_3_part"
        elif line_count == 2:
            return "two_part"
        elif '?' in tweet:
            return "question_response"
        else:
            return f"{line_count}_part_custom"
    
    def _load_optimized_templates(self) -> Dict:
        """Load optimized template patterns"""
        return {
            'philosophical': {
                'openings': [
                    "The {concept} debate is exhausting.",
                    "Everyone focused on {concept} misses the point.",
                    "{concept} concerns are valid, but..."
                ],
                'middles': [
                    "What matters: positioning for what's next.",
                    "Real alpha: understanding second-order effects.",
                    "Focus: macro trends and liquidity flows."
                ],
                'closings': [
                    "Until then? We trade the range.",
                    "Few get this.",
                    "Everything else is noise."
                ]
            }
        }

class OptimizedMilesAISystem:
    """Main optimized system with <100ms response times"""
    
    def __init__(self):
        # Core components
        self.cache = OptimizedCache()
        self.db = OptimizedDatabaseManager()
        self.twitter_client = OptimizedTwitterClient(
            os.getenv('TWITTER_BEARER_TOKEN', 
                     'AAAAAAAAAAAAAAAAAAAAAJi13QEAAAAAghVwuLws1YdchbwCAkUjqqwu6oc%3DeImrILD6DNOvuOdZiH42oFM3Ww7zTLYaiz1onypLp8XNzCskQ7')
        )
        self.analyzer = OptimizedPatternAnalyzer()
        self.generator = OptimizedTweetGenerator()
        
        # Performance monitoring
        self.performance_metrics = {
            'total_requests': 0,
            'avg_response_time': 0,
            'cache_hit_rate': 0,
            'memory_usage': 0,
            'active_connections': 0
        }
        
        # Background processing
        self.background_queue = asyncio.Queue()
        self.is_running = True
        
        # Initialize async components
        asyncio.create_task(self._initialize_async_components())
        
        logging.info("Optimized Miles AI System initialized")
    
    async def _initialize_async_components(self):
        """Initialize async components"""
        await self.cache.init_redis()
        await self.twitter_client.init_session()
        
        # Start background processors
        asyncio.create_task(self._background_processor())
        asyncio.create_task(self._performance_monitor())
        
        logging.info("Async components initialized")
    
    @monitor_performance
    async def generate_tweet_fast(self, input_text: str) -> Dict:
        """Generate tweet with <100ms target response time"""
        start_time = time.perf_counter()
        
        try:
            # Check cache first (should be <10ms)
            cache_key = f"tweet_gen_{hashlib.sha256(input_text.encode()).hexdigest()[:16]}"
            cached_result = await self.cache.get(cache_key)
            
            if cached_result:
                cached_result['from_cache'] = True
                cached_result['response_time'] = (time.perf_counter() - start_time) * 1000
                return cached_result
            
            # Get recent patterns from cache (should be <20ms)
            patterns_key = "recent_patterns"
            patterns = await self.cache.get(patterns_key)
            
            if not patterns:
                # Fallback to basic patterns if cache miss
                patterns = {'structures': {'3_part': 10}, 'high_engagement': []}
            
            # Generate tweet (should be <50ms)
            result = self.generator.generate_optimized(input_text, patterns)
            
            # Cache result for future requests
            await self.cache.set(cache_key, result, expire_seconds=1800)  # 30 minutes
            
            # Add timing info
            result['response_time'] = (time.perf_counter() - start_time) * 1000
            
            # Update performance metrics
            self.performance_metrics['total_requests'] += 1
            
            return result
            
        except Exception as e:
            logging.error(f"Fast generation error: {e}")
            # Return fallback response
            return {
                'text': f"{input_text}\n\nFew understand this.",
                'strategy': 'fallback',
                'confidence': 0.5,
                'error': str(e),
                'response_time': (time.perf_counter() - start_time) * 1000
            }
    
    @monitor_performance
    async def update_patterns_optimized(self):
        """Update patterns with optimized processing"""
        try:
            # Fetch latest tweets in background
            tweets = await self.twitter_client.fetch_user_tweets_batch('milesdeutscher', 50)
            
            if not tweets:
                return
            
            # Batch insert to database
            self.db.batch_insert_tweets(tweets)
            
            # Batch analyze patterns
            analyses = self.analyzer.analyze_tweet_batch(tweets)
            
            # Process patterns
            patterns = self._process_pattern_batch(analyses)
            
            # Cache patterns
            await self.cache.set("recent_patterns", patterns, expire_seconds=3600)
            
            logging.info(f"Updated patterns from {len(tweets)} tweets")
            
        except Exception as e:
            logging.error(f"Pattern update error: {e}")
    
    def _process_pattern_batch(self, analyses: List[Dict]) -> Dict:
        """Process analyses into pattern summary"""
        patterns = {
            'structures': defaultdict(int),
            'sentiments': defaultdict(int),
            'high_engagement': [],
            'avg_confidence': 0
        }
        
        total_confidence = 0
        
        for analysis in analyses:
            # Structure patterns
            pattern = analysis['structure']['pattern']
            patterns['structures'][pattern] += 1
            
            # Sentiment patterns
            sentiment = analysis['sentiment']
            patterns['sentiments'][sentiment] += 1
            
            # High engagement tweets
            if analysis['engagement_score'] > 100:
                patterns['high_engagement'].append({
                    'engagement': analysis['engagement_score'],
                    'structure': analysis['structure'],
                    'sentiment': sentiment
                })
            
            total_confidence += analysis.get('confidence', 0.5)
        
        patterns['avg_confidence'] = total_confidence / len(analyses) if analyses else 0
        
        # Convert defaultdicts to regular dicts for JSON serialization
        patterns['structures'] = dict(patterns['structures'])
        patterns['sentiments'] = dict(patterns['sentiments'])
        
        return patterns
    
    async def _background_processor(self):
        """Background processing for non-critical updates"""
        while self.is_running:
            try:
                # Update patterns every 10 minutes
                await self.update_patterns_optimized()
                
                # Cleanup old cache entries
                await self._cleanup_cache()
                
                # Wait before next cycle
                await asyncio.sleep(600)  # 10 minutes
                
            except Exception as e:
                logging.error(f"Background processor error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _performance_monitor(self):
        """Monitor system performance"""
        while self.is_running:
            try:
                # Update performance metrics
                process = psutil.Process()
                
                self.performance_metrics.update({
                    'memory_usage': process.memory_info().rss / 1024 / 1024,  # MB
                    'cache_hit_rate': self.cache.get_stats()['hit_rate'],
                    'analyzer_stats': self.analyzer.get_stats()
                })
                
                # Log performance summary every 5 minutes
                logging.info(f"Performance: "
                           f"Memory: {self.performance_metrics['memory_usage']:.1f}MB, "
                           f"Cache: {self.performance_metrics['cache_hit_rate']:.1f}%, "
                           f"Requests: {self.performance_metrics['total_requests']}")
                
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logging.error(f"Performance monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_cache(self):
        """Cleanup old cache entries to prevent memory bloat"""
        # Trigger garbage collection
        gc.collect()
        
        # Clear old pattern cache entries
        current_time = time.time()
        old_keys = []
        
        for key, entry in self.generator.generation_cache.items():
            if current_time - entry.get('generation_time', 0) > 3600:  # 1 hour
                old_keys.append(key)
        
        for key in old_keys:
            del self.generator.generation_cache[key]
        
        if old_keys:
            logging.info(f"Cleaned up {len(old_keys)} old cache entries")
    
    async def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        return {
            'performance': self.performance_metrics,
            'cache_stats': self.cache.get_stats(),
            'analyzer_stats': self.analyzer.get_stats(),
            'uptime': time.time(),
            'system_ready': True
        }
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.is_running = False
        await self.twitter_client.close()
        logging.info("System shutdown complete")

# High-performance web interface
class OptimizedWebHandler:
    """Optimized web handler with async support"""
    
    def __init__(self, ai_system: OptimizedMilesAISystem):
        self.ai_system = ai_system
    
    async def handle_generate(self, request_data: Dict) -> Dict:
        """Handle tweet generation request"""
        input_text = request_data.get('input', '').strip()
        
        if not input_text:
            return {'error': 'Input text required'}
        
        try:
            result = await self.ai_system.generate_tweet_fast(input_text)
            return result
        except Exception as e:
            logging.error(f"Generation request error: {e}")
            return {'error': str(e)}
    
    async def handle_status(self) -> Dict:
        """Handle status request"""
        try:
            return await self.ai_system.get_system_status()
        except Exception as e:
            logging.error(f"Status request error: {e}")
            return {'error': str(e)}

# Main execution
async def main():
    """Main async execution"""
    print("""
    ================================================================
        Miles Deutscher AI - Optimized High-Performance System     
                                                              
      🚀 Sub-100ms Response Times with Redis Caching          
      ⚡ Asynchronous Processing & Connection Pooling          
      🧠 Intelligent Pattern Analysis & Memoization           
      📊 Real-time Performance Monitoring                     
      🔄 Background Processing Queue System                   
    ================================================================
    """)
    
    # Initialize optimized system
    ai_system = OptimizedMilesAISystem()
    
    # Wait for initialization
    await asyncio.sleep(2)
    
    # Perform initial data fetch
    print("\n[INIT] Performing initial optimized data analysis...")
    await ai_system.update_patterns_optimized()
    
    print("\n[READY] Optimized system initialized!")
    print("\n[PERFORMANCE TARGETS]:")
    print("   - Tweet Generation: <100ms response time")
    print("   - API Requests: Batched with intelligent rate limiting")
    print("   - Memory Usage: <500MB with 994 tweet dataset")
    print("   - Cache Hit Rate: >85% for repeat requests")
    print("   - Background Processing: Non-blocking updates")
    
    # Keep system running
    try:
        while True:
            await asyncio.sleep(60)
            status = await ai_system.get_system_status()
            print(f"\n[STATUS] Memory: {status['performance']['memory_usage']:.1f}MB, "
                  f"Cache Hit Rate: {status['cache_stats']['hit_rate']:.1f}%, "
                  f"Total Requests: {status['performance']['total_requests']}")
    
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Gracefully shutting down...")
        await ai_system.shutdown()

if __name__ == "__main__":
    asyncio.run(main())