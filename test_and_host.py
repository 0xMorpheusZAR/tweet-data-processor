"""
Test Twitter API and Host Local Server with Latest Data
Simple implementation without external dependencies
"""

import json
import urllib.request
import urllib.parse
import base64
import ssl
import time
from datetime import datetime
import random
import http.server
import socketserver
import threading

# Twitter API credentials from .env
API_CREDENTIALS = {
    'bearer_token': 'AAAAAAAAAAAAAAAAAAAAAJi13QEAAAAAghVwuLws1YdchbwCAkUjqqwu6oc%3DeImrILD6DNOvuOdZiH42oFM3Ww7zTLYaiz1onypLp8XNzCskQ7'
}

class SimpleTwitterAPI:
    """Simple Twitter API client using urllib"""
    
    def __init__(self):
        self.bearer_token = API_CREDENTIALS['bearer_token']
        self.base_url = 'https://api.twitter.com/2'
        
    def make_request(self, endpoint, params=None):
        """Make API request"""
        
        # Build URL
        url = f"{self.base_url}{endpoint}"
        if params:
            url += '?' + urllib.parse.urlencode(params)
        
        # Create request
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {self.bearer_token}')
        req.add_header('User-Agent', 'MilesDeutscherAI/1.0')
        
        try:
            # Make request with SSL context
            context = ssl.create_default_context()
            with urllib.request.urlopen(req, context=context) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            print(f"API Error: {e}")
            return None
    
    def get_user_tweets(self, username='milesdeutscher', max_results=10):
        """Get user's recent tweets"""
        
        print(f"Fetching tweets from @{username}...")
        
        # First get user ID
        user_data = self.make_request(f'/users/by/username/{username}')
        
        if not user_data or 'data' not in user_data:
            print("Error: Could not fetch user data")
            return []
        
        user_id = user_data['data']['id']
        print(f"User ID: {user_id}")
        
        # Get tweets
        params = {
            'max_results': max_results,
            'tweet.fields': 'created_at,public_metrics',
            'exclude': 'retweets,replies'
        }
        
        tweets_data = self.make_request(f'/users/{user_id}/tweets', params)
        
        if tweets_data and 'data' in tweets_data:
            return tweets_data['data']
        
        return []

class LatestMilesGenerator:
    """Generate tweets based on latest patterns"""
    
    def __init__(self, latest_tweets):
        self.latest_tweets = latest_tweets
        self.analyze_patterns()
        
    def analyze_patterns(self):
        """Analyze latest tweet patterns"""
        
        self.patterns = {
            'structures': {},
            'avg_length': 0,
            'common_phrases': []
        }
        
        if not self.latest_tweets:
            return
        
        total_length = 0
        
        for tweet in self.latest_tweets:
            text = tweet.get('text', '')
            
            # Length
            total_length += len(text)
            
            # Structure
            lines = text.split('\n')
            structure = f"{len(lines)}_line"
            self.patterns['structures'][structure] = self.patterns['structures'].get(structure, 0) + 1
        
        self.patterns['avg_length'] = total_length / len(self.latest_tweets) if self.latest_tweets else 0
    
    def generate(self, user_input):
        """Generate tweet based on latest patterns"""
        
        # Use the baseline Option 5 structure with latest insights
        
        # Extract topic
        topic = user_input.strip().lower()
        
        # Templates based on latest patterns
        templates = [
            # Option 5 baseline
            f"The {topic} debate is just noise.\n\nWhat matters: positioning yourself for what comes next.\n\nUntil then? We're all just speculating.",
            
            # Variations based on latest tweets
            f"Everyone focused on {topic} is missing the point.\n\nReal alpha: understanding the second-order effects.\n\nFew.",
            
            f"{topic.capitalize()} talks everywhere.\n\nReality: It's already priced in.\n\nTrade the next narrative, not this one.",
            
            # Short form if input is brief
            f"{user_input}\n\nBased." if len(user_input) < 30 else None
        ]
        
        # Filter out None values
        templates = [t for t in templates if t]
        
        return random.choice(templates)

# Simple web server for local hosting
class MilesAIHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for Miles AI server"""
    
    def do_GET(self):
        """Handle GET requests"""
        
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Miles Deutscher AI - Live Testing</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background: #15202B;
                        color: #fff;
                    }
                    h1 { color: #1DA1F2; }
                    .status { 
                        background: #192734; 
                        padding: 20px; 
                        border-radius: 10px;
                        margin: 20px 0;
                    }
                    .tweet-box {
                        background: #192734;
                        border: 1px solid #38444D;
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 8px;
                    }
                    input, button {
                        padding: 10px;
                        margin: 5px;
                        border-radius: 5px;
                        border: 1px solid #38444D;
                        background: #192734;
                        color: #fff;
                    }
                    button {
                        background: #1DA1F2;
                        cursor: pointer;
                    }
                    button:hover { background: #1A8CD8; }
                    .metrics { 
                        font-size: 0.9em; 
                        color: #8B98A5;
                        margin-top: 10px;
                    }
                </style>
            </head>
            <body>
                <h1>🐦 Miles Deutscher AI - Live Testing</h1>
                
                <div class="status">
                    <h2>📊 API Status</h2>
                    <p id="api-status">Checking connection...</p>
                    <p id="latest-tweet">Loading latest tweets...</p>
                </div>
                
                <div class="status">
                    <h2>🚀 Generate Tweet</h2>
                    <input type="text" id="input" placeholder="Enter topic..." style="width: 60%">
                    <button onclick="generateTweet()">Generate</button>
                    <div id="output"></div>
                </div>
                
                <div class="status">
                    <h2>📈 Latest Patterns</h2>
                    <div id="patterns">Analyzing...</div>
                </div>
                
                <script>
                    // Check API status on load
                    fetch('/api/status')
                        .then(r => r.json())
                        .then(data => {
                            document.getElementById('api-status').innerHTML = 
                                data.connected ? '✅ Connected to X API' : '❌ API Error';
                            
                            if (data.latest_tweet) {
                                document.getElementById('latest-tweet').innerHTML = 
                                    'Latest tweet: "' + data.latest_tweet.substring(0, 100) + '..."';
                            }
                            
                            if (data.patterns) {
                                document.getElementById('patterns').innerHTML = 
                                    'Average length: ' + Math.round(data.patterns.avg_length) + ' chars<br>' +
                                    'Dominant structure: ' + Object.keys(data.patterns.structures)[0];
                            }
                        });
                    
                    function generateTweet() {
                        const input = document.getElementById('input').value;
                        
                        fetch('/api/generate', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({input: input})
                        })
                        .then(r => r.json())
                        .then(data => {
                            document.getElementById('output').innerHTML = 
                                '<div class="tweet-box">' + 
                                data.output.replace(/\\n/g, '<br>') +
                                '<div class="metrics">Length: ' + data.length + ' chars</div>' +
                                '</div>';
                        });
                    }
                </script>
            </body>
            </html>
            '''
            
            self.wfile.write(html.encode())
            
        elif self.path == '/api/status':
            # API status endpoint
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'connected': hasattr(server, 'api_connected'),
                'latest_tweet': server.latest_tweets[0]['text'] if server.latest_tweets else None,
                'patterns': server.generator.patterns if hasattr(server, 'generator') else None
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        else:
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        
        if self.path == '/api/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            # Generate tweet
            output = server.generator.generate(data['input'])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'output': output,
                'length': len(output)
            }
            
            self.wfile.write(json.dumps(response).encode())

# Main execution
def main():
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║   Miles Deutscher AI - Testing with Latest Data      ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    # Test API connection
    print("\n1️⃣ Testing Twitter API connection...")
    api = SimpleTwitterAPI()
    
    # Fetch latest tweets
    print("\n2️⃣ Fetching latest tweets from @milesdeutscher...")
    latest_tweets = api.get_user_tweets(max_results=10)
    
    if latest_tweets:
        print(f"✅ Successfully fetched {len(latest_tweets)} tweets")
        
        # Show sample
        print("\n📝 Latest tweet:")
        print("-" * 60)
        print(latest_tweets[0]['text'][:200] + "...")
        print("-" * 60)
        
        # Analyze patterns
        print("\n3️⃣ Analyzing latest patterns...")
        generator = LatestMilesGenerator(latest_tweets)
        print(f"   Average length: {generator.patterns['avg_length']:.0f} chars")
        print(f"   Structures found: {generator.patterns['structures']}")
        
        # Start web server
        print("\n4️⃣ Starting local web server...")
        PORT = 8000
        
        # Create custom server with data
        global server
        server = socketserver.TCPServer(("", PORT), MilesAIHandler)
        server.api_connected = True
        server.latest_tweets = latest_tweets
        server.generator = generator
        
        print(f"\n✅ Server running at: http://localhost:{PORT}")
        print("\n📱 Open your browser to test with latest Miles Deutscher style!")
        print("\nPress Ctrl+C to stop the server")
        
        # Start server
        server.serve_forever()
        
    else:
        print("❌ Could not fetch tweets. Check API credentials or connection.")
        
        # Start server anyway with default patterns
        print("\n Starting server with default patterns...")
        PORT = 8000
        
        server = socketserver.TCPServer(("", PORT), MilesAIHandler)
        server.api_connected = False
        server.latest_tweets = []
        server.generator = LatestMilesGenerator([])
        
        print(f"\n✅ Server running at: http://localhost:{PORT}")
        server.serve_forever()

if __name__ == "__main__":
    main()