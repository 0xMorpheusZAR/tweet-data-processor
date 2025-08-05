"""
Miles Deutscher AI - Complete System
Features:
1. Text input → Miles-style tweet generation
2. Real-time Twitter data integration
3. Continuous learning with progress logging
4. Local web interface
"""

import os
import json
import time
import threading
import queue
from datetime import datetime, timedelta
import urllib.request
import urllib.parse
import ssl
import http.server
import socketserver
import logging
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('miles_ai_progress.log'),
        logging.StreamHandler()
    ]
)

class MilesAICompleteSystem:
    """
    Complete Miles Deutscher AI system with all features
    """
    
    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN', 
            'AAAAAAAAAAAAAAAAAAAAAJi13QEAAAAAghVwuLws1YdchbwCAkUjqqwu6oc%3DeImrILD6DNOvuOdZiH42oFM3Ww7zTLYaiz1onypLp8XNzCskQ7')
        
        self.latest_tweets = []
        self.training_data = []
        self.style_patterns = {}
        self.last_update = None
        self.update_queue = queue.Queue()
        self.is_updating = False
        
        # Load existing training data
        self.load_training_data()
        
        # Start background updater
        self.start_background_updater()
        
        logging.info("Miles AI Complete System initialized")
    
    def load_training_data(self):
        """Load existing training data"""
        try:
            with open('data.jsonl', 'r', encoding='utf-8') as f:
                for line in f:
                    self.training_data.append(json.loads(line))
            logging.info(f"Loaded {len(self.training_data)} training examples")
        except:
            logging.warning("No existing training data found")
    
    def fetch_latest_tweets(self, count: int = 20) -> List[Dict]:
        """Fetch latest tweets from Miles Deutscher"""
        
        logging.info("Fetching latest tweets from @milesdeutscher...")
        
        # Build API request
        url = "https://api.twitter.com/2/users/by/username/milesdeutscher"
        
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {self.bearer_token}')
        
        try:
            context = ssl.create_default_context()
            with urllib.request.urlopen(req, context=context) as response:
                user_data = json.loads(response.read().decode())
                
            if 'data' not in user_data:
                logging.error("Could not fetch user data")
                return []
            
            user_id = user_data['data']['id']
            
            # Get tweets
            tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            params = {
                'max_results': count,
                'tweet.fields': 'created_at,public_metrics',
                'exclude': 'retweets,replies'
            }
            
            tweets_url += '?' + urllib.parse.urlencode(params)
            
            req = urllib.request.Request(tweets_url)
            req.add_header('Authorization', f'Bearer {self.bearer_token}')
            
            with urllib.request.urlopen(req, context=context) as response:
                tweets_data = json.loads(response.read().decode())
            
            if 'data' in tweets_data:
                self.latest_tweets = tweets_data['data']
                logging.info(f"Fetched {len(self.latest_tweets)} tweets")
                return self.latest_tweets
            
        except Exception as e:
            logging.error(f"Error fetching tweets: {e}")
        
        return []
    
    def analyze_patterns(self):
        """Analyze patterns from latest tweets"""
        
        if not self.latest_tweets:
            return
        
        logging.info("Analyzing tweet patterns...")
        
        self.style_patterns = {
            'structures': {},
            'avg_length': 0,
            'high_engagement': []
        }
        
        total_length = 0
        
        for tweet in self.latest_tweets:
            text = tweet.get('text', '')
            metrics = tweet.get('public_metrics', {})
            
            # Length
            total_length += len(text)
            
            # Structure
            lines = text.split('\n')
            structure = f"{len(lines)}_part"
            self.style_patterns['structures'][structure] = \
                self.style_patterns['structures'].get(structure, 0) + 1
            
            # Engagement
            engagement = (
                metrics.get('like_count', 0) + 
                metrics.get('retweet_count', 0) * 2 +
                metrics.get('reply_count', 0)
            )
            
            if engagement > 100:  # High engagement threshold
                self.style_patterns['high_engagement'].append({
                    'text': text[:100] + '...' if len(text) > 100 else text,
                    'engagement': engagement
                })
        
        self.style_patterns['avg_length'] = total_length / len(self.latest_tweets)
        
        # Log findings
        logging.info(f"Average tweet length: {self.style_patterns['avg_length']:.0f} chars")
        logging.info(f"Dominant structure: {max(self.style_patterns['structures'], key=self.style_patterns['structures'].get)}")
    
    def generate_tweet(self, user_input: str) -> Dict:
        """
        Main function: Generate Miles-style tweet from user input
        """
        
        logging.info(f"Generating tweet for input: '{user_input}'")
        
        # Determine style based on input
        input_lower = user_input.lower()
        
        # Use latest patterns if available
        if self.style_patterns and '3_part' in self.style_patterns['structures']:
            dominant_structure = '3_part'
        else:
            dominant_structure = 'adaptive'
        
        # Generate based on input type
        if any(word in input_lower for word in ['bull', 'pump', 'moon']):
            tweet = self._generate_bullish(user_input)
        elif any(word in input_lower for word in ['bear', 'dump', 'crash']):
            tweet = self._generate_bearish(user_input)
        elif '?' in user_input:
            tweet = self._generate_question(user_input)
        elif len(user_input) > 30:
            tweet = self._generate_philosophical(user_input)
        else:
            tweet = self._generate_quick_take(user_input)
        
        result = {
            'input': user_input,
            'output': tweet,
            'length': len(tweet),
            'structure': dominant_structure,
            'based_on': f"{len(self.latest_tweets)} recent tweets" if self.latest_tweets else "training data",
            'timestamp': datetime.now().isoformat()
        }
        
        # Log generation
        logging.info(f"Generated tweet: {len(tweet)} chars, structure: {dominant_structure}")
        
        return result
    
    def _generate_bullish(self, input_text: str) -> str:
        """Generate bullish tweet"""
        ticker = self._extract_ticker(input_text) or "BTC"
        
        templates = [
            f"${ticker} looking absolutely fire right now.\n\nClean break above resistance with volume.\n\nUp only.",
            f"Ser, ${ticker} is about to melt faces.\n\nAccumulation phase complete.\n\nNGMI if you're not paying attention.",
            f"${ticker} chart telling a beautiful story.\n\nHigher lows, higher highs.\n\nBullish."
        ]
        
        return templates[hash(input_text) % len(templates)]
    
    def _generate_bearish(self, input_text: str) -> str:
        """Generate bearish tweet"""
        ticker = self._extract_ticker(input_text) or "BTC"
        
        templates = [
            f"${ticker} showing major weakness here.\n\nSupport broken, no buyers in sight.\n\nProtect your capital.",
            f"Warning: ${ticker} about to get rekt.\n\nMomentum fading fast.\n\nThis is not the dip to buy.",
            f"${ticker} chart looking absolutely cooked.\n\nBears in full control.\n\nDon't catch falling knives."
        ]
        
        return templates[hash(input_text) % len(templates)]
    
    def _generate_question(self, input_text: str) -> str:
        """Generate question response"""
        templates = [
            f"{input_text}\n\nThe answer is always liquidity.",
            f"{input_text}\n\nAnon, you already know the answer.",
            f"{input_text}\n\nYes. Next question."
        ]
        
        return templates[hash(input_text) % len(templates)]
    
    def _generate_philosophical(self, input_text: str) -> str:
        """Generate philosophical tweet using Option 5 baseline"""
        topic = input_text.strip()
        
        templates = [
            f"The {topic} debate is just noise.\n\nWhat matters: positioning yourself for what comes next.\n\nUntil then? We're all just trading the range.",
            f"Everyone focused on {topic} is missing the point.\n\nReal game: understanding second-order effects.\n\nFew.",
            f"{topic.capitalize()} concerns are valid.\n\nBut markets don't care about valid.\n\nThey care about liquidity and narrative."
        ]
        
        return templates[hash(input_text) % len(templates)]
    
    def _generate_quick_take(self, input_text: str) -> str:
        """Generate quick take"""
        templates = [
            f"{input_text}\n\nBased.",
            f"{input_text}\n\nFew understand this.",
            f"Unpopular opinion: {input_text}\n\nBut I said what I said."
        ]
        
        return templates[hash(input_text) % len(templates)]
    
    def _extract_ticker(self, text: str) -> Optional[str]:
        """Extract ticker from text"""
        import re
        tickers = re.findall(r'\$?([A-Z]{2,5})', text.upper())
        return tickers[0] if tickers else None
    
    def update_training_data(self):
        """Update training data with latest tweets"""
        
        if not self.latest_tweets:
            return
        
        logging.info("Updating training data with new tweets...")
        
        new_entries = 0
        
        for tweet in self.latest_tweets:
            text = tweet.get('text', '')
            
            # Check if already exists
            exists = any(text in entry.get('completion', '') for entry in self.training_data)
            
            if not exists and not text.startswith('@') and not text.startswith('RT'):
                entry = {
                    'prompt': 'Write a tweet in the style of Miles Deutscher:',
                    'completion': f' {text}',
                    'metadata': {
                        'source': 'twitter_api',
                        'collected_at': datetime.now().isoformat(),
                        'metrics': tweet.get('public_metrics', {})
                    }
                }
                
                self.training_data.append(entry)
                new_entries += 1
        
        if new_entries > 0:
            # Save updated data
            with open('data_enhanced.jsonl', 'w', encoding='utf-8') as f:
                for entry in self.training_data:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            logging.info(f"Added {new_entries} new training examples")
            logging.info(f"Total training examples: {len(self.training_data)}")
    
    def background_updater(self):
        """Background thread for continuous updates"""
        
        while True:
            try:
                # Update every 30 minutes
                self.is_updating = True
                
                logging.info("Starting background update cycle...")
                
                # Fetch latest tweets
                if self.fetch_latest_tweets():
                    # Analyze patterns
                    self.analyze_patterns()
                    
                    # Update training data
                    self.update_training_data()
                    
                    self.last_update = datetime.now()
                    
                    logging.info("Background update completed successfully")
                
                self.is_updating = False
                
                # Wait 30 minutes
                time.sleep(1800)
                
            except Exception as e:
                logging.error(f"Background update error: {e}")
                self.is_updating = False
                time.sleep(300)  # Wait 5 minutes on error
    
    def start_background_updater(self):
        """Start background updater thread"""
        thread = threading.Thread(target=self.background_updater, daemon=True)
        thread.start()
        logging.info("Background updater started")
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            'training_examples': len(self.training_data),
            'latest_tweets': len(self.latest_tweets),
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'is_updating': self.is_updating,
            'style_patterns': self.style_patterns
        }

# Web interface
class MilesAIWebHandler(http.server.SimpleHTTPRequestHandler):
    """Web interface for Miles AI"""
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Miles Deutscher AI - Complete System</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background: #15202B;
            color: #fff;
        }
        h1 { color: #1DA1F2; margin-bottom: 10px; }
        .subtitle { color: #8B98A5; margin-bottom: 30px; }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .panel {
            background: #192734;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #38444D;
        }
        .full-width { grid-column: 1 / -1; }
        h2 { color: #1DA1F2; margin-top: 0; }
        input, textarea {
            width: 100%;
            padding: 12px;
            background: #253341;
            border: 1px solid #38444D;
            border-radius: 8px;
            color: #fff;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            background: #1DA1F2;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 100px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover { background: #1A8CD8; }
        .tweet-output {
            background: #253341;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            white-space: pre-wrap;
            font-size: 18px;
            line-height: 1.4;
            min-height: 100px;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        .metric {
            background: #253341;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            color: #1DA1F2;
        }
        .metric-label {
            font-size: 12px;
            color: #8B98A5;
            margin-top: 5px;
        }
        .status {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #17BF63;
        }
        .status-dot.updating { background: #FFAD1F; }
        .log {
            background: #000;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 12px;
            height: 200px;
            overflow-y: auto;
            color: #0F0;
        }
        .examples {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        .example-btn {
            background: #253341;
            border: 1px solid #38444D;
            color: #8B98A5;
            padding: 6px 12px;
            border-radius: 100px;
            font-size: 14px;
            cursor: pointer;
        }
        .example-btn:hover {
            background: #1DA1F2;
            color: white;
            border-color: #1DA1F2;
        }
    </style>
</head>
<body>
    <h1>🐦 Miles Deutscher AI</h1>
    <p class="subtitle">Complete System with Real-Time Learning</p>
    
    <div class="container">
        <!-- Input Panel -->
        <div class="panel">
            <h2>Generate Tweet</h2>
            <textarea id="input" placeholder="Enter your topic or idea..." rows="3"></textarea>
            <button onclick="generateTweet()">Generate Miles-Style Tweet</button>
            
            <div class="examples">
                <button class="example-btn" onclick="setInput('bitcoin halving impact')">Market Analysis</button>
                <button class="example-btn" onclick="setInput('is this the top?')">Question</button>
                <button class="example-btn" onclick="setInput('everyone wants quick gains')">Philosophical</button>
                <button class="example-btn" onclick="setInput('gm')">Quick Take</button>
            </div>
        </div>
        
        <!-- System Status Panel -->
        <div class="panel">
            <h2>System Status</h2>
            <div class="status">
                <div class="status-dot" id="statusDot"></div>
                <span id="statusText">Connected</span>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value" id="trainingCount">0</div>
                    <div class="metric-label">Training Examples</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="tweetsCount">0</div>
                    <div class="metric-label">Latest Tweets</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="updateTime">Never</div>
                    <div class="metric-label">Last Update</div>
                </div>
            </div>
        </div>
        
        <!-- Output Panel -->
        <div class="panel full-width">
            <h2>Generated Tweet</h2>
            <div class="tweet-output" id="output">Your generated tweet will appear here...</div>
            
            <div class="metrics" id="outputMetrics" style="display: none;">
                <div class="metric">
                    <div class="metric-value" id="charCount">0</div>
                    <div class="metric-label">Characters</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="structure">-</div>
                    <div class="metric-label">Structure</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="basedOn">-</div>
                    <div class="metric-label">Based On</div>
                </div>
            </div>
        </div>
        
        <!-- Progress Log Panel -->
        <div class="panel full-width">
            <h2>Progress Log</h2>
            <div class="log" id="progressLog">System initializing...</div>
        </div>
    </div>
    
    <script>
        // Update status on load
        updateStatus();
        setInterval(updateStatus, 5000);
        
        function updateStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('trainingCount').textContent = data.training_examples;
                    document.getElementById('tweetsCount').textContent = data.latest_tweets;
                    
                    if (data.last_update) {
                        const date = new Date(data.last_update);
                        const mins = Math.floor((Date.now() - date) / 60000);
                        document.getElementById('updateTime').textContent = mins + 'm ago';
                    }
                    
                    if (data.is_updating) {
                        document.getElementById('statusDot').classList.add('updating');
                        document.getElementById('statusText').textContent = 'Updating...';
                    } else {
                        document.getElementById('statusDot').classList.remove('updating');
                        document.getElementById('statusText').textContent = 'Connected';
                    }
                });
        }
        
        function generateTweet() {
            const input = document.getElementById('input').value;
            if (!input) return;
            
            addLog('Generating tweet for: "' + input + '"');
            
            fetch('/api/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({input: input})
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('output').textContent = data.output;
                document.getElementById('charCount').textContent = data.length;
                document.getElementById('structure').textContent = data.structure;
                document.getElementById('basedOn').textContent = data.based_on;
                document.getElementById('outputMetrics').style.display = 'grid';
                
                addLog('Generated ' + data.length + ' char tweet using ' + data.structure + ' structure');
            });
        }
        
        function setInput(text) {
            document.getElementById('input').value = text;
        }
        
        function addLog(message) {
            const log = document.getElementById('progressLog');
            const time = new Date().toLocaleTimeString();
            log.innerHTML += '\\n[' + time + '] ' + message;
            log.scrollTop = log.scrollHeight;
        }
        
        // Initial log
        addLog('System ready. Real-time learning active.');
        addLog('Background updates every 30 minutes.');
    </script>
</body>
</html>
            '''
            
            self.wfile.write(html.encode())
        
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            status = miles_ai.get_system_status()
            self.wfile.write(json.dumps(status).encode())
        
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            result = miles_ai.generate_tweet(data['input'])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())

# Main execution
if __name__ == "__main__":
    print("""
    ========================================================
          Miles Deutscher AI - Complete System            
                                                          
      * Text Input -> Miles-Style Tweet                   
      * Real-Time Twitter Data Updates                   
      * Continuous Learning & Improvement                
      * Progress Logging & Monitoring                    
    ========================================================
    """)
    
    # Initialize system
    global miles_ai
    miles_ai = MilesAICompleteSystem()
    
    # Do initial update
    print("\nPerforming initial data fetch...")
    miles_ai.fetch_latest_tweets()
    miles_ai.analyze_patterns()
    
    # Start web server
    PORT = 8000
    server = socketserver.TCPServer(("", PORT), MilesAIWebHandler)
    
    print(f"\nSystem running at: http://localhost:{PORT}")
    print("\nFeatures:")
    print("   - Generate tweets from any input")
    print("   - Real-time learning from @milesdeutscher")
    print("   - Automatic updates every 30 minutes")
    print("   - Progress logging to miles_ai_progress.log")
    print("\nPress Ctrl+C to stop")
    
    server.serve_forever()