"""
Miles AI Simple Server - No dependencies required
Run this to start generating optimal tweets
"""
import http.server
import socketserver
import json
import urllib.parse
from datetime import datetime

# Import our Miles AI systems
from miles_optimal_tweet_generator_blind_test import MilesOptimalGenerator, ContextInput

# Initialize generator
generator = MilesOptimalGenerator()

# HTML Interface
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Miles AI - Tweet Generator</title>
    <style>
        body {
            font-family: -apple-system, system-ui, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #0a0a0a;
            color: white;
        }
        
        h1 {
            color: #1DA1F2;
            text-align: center;
            font-size: 3em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 40px;
        }
        
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        .card {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 30px;
        }
        
        h2 {
            color: #1DA1F2;
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            color: #1DA1F2;
            font-weight: bold;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 10px;
            background: #0a0a0a;
            border: 1px solid #333;
            color: white;
            border-radius: 5px;
            font-size: 16px;
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #1DA1F2;
        }
        
        button {
            background: #1DA1F2;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 18px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            font-weight: bold;
        }
        
        button:hover {
            background: #0e76a8;
        }
        
        #output {
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 20px;
            min-height: 150px;
            white-space: pre-wrap;
            line-height: 1.6;
            font-size: 18px;
        }
        
        #output.success {
            border-color: #1DA1F2;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        
        .metric {
            background: #0a0a0a;
            border: 1px solid #333;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 24px;
            color: #1DA1F2;
            font-weight: bold;
        }
        
        .metric-label {
            color: #888;
            font-size: 14px;
            margin-top: 5px;
        }
        
        .quick-buttons {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .quick-btn {
            background: #333;
            color: white;
            border: 1px solid #555;
            padding: 8px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .quick-btn:hover {
            border-color: #1DA1F2;
            color: #1DA1F2;
        }
        
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <h1>🚀 Miles AI</h1>
    <p class="subtitle">Optimal Tweet Generation - 90%+ Accuracy</p>
    
    <div class="container">
        <div class="card">
            <h2>Context Input</h2>
            <form id="tweetForm">
                <div class="form-group">
                    <label>Topic</label>
                    <input type="text" id="topic" placeholder="e.g., Bitcoin, DeFi, Market" required>
                </div>
                
                <div class="form-group">
                    <label>Market Condition</label>
                    <select id="market">
                        <option value="volatile">Volatile</option>
                        <option value="bearish">Bearish</option>
                        <option value="bullish">Bullish</option>
                        <option value="neutral">Neutral</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Urgency</label>
                    <select id="urgency">
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Sentiment</label>
                    <select id="sentiment">
                        <option value="fear">Fear</option>
                        <option value="greed">Greed</option>
                        <option value="confusion">Confusion</option>
                        <option value="neutral">Neutral</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Key Insight (Optional)</label>
                    <textarea id="insight" rows="3" placeholder="e.g., Smart money is accumulating"></textarea>
                </div>
                
                <button type="submit">Generate Optimal Tweet</button>
            </form>
            
            <div class="quick-buttons">
                <button class="quick-btn" onclick="setQuick('btc-fear')">BTC Fear</button>
                <button class="quick-btn" onclick="setQuick('alt-opp')">Alt Opportunity</button>
                <button class="quick-btn" onclick="setQuick('risk')">Risk Warning</button>
                <button class="quick-btn" onclick="setQuick('psych')">Psychology</button>
            </div>
        </div>
        
        <div class="card">
            <h2>Generated Tweet</h2>
            <div id="output">Your optimized tweet will appear here...</div>
            
            <div class="metrics" id="metrics" style="display:none;">
                <div class="metric">
                    <div class="metric-value" id="engagement">-</div>
                    <div class="metric-label">Predicted Engagement</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="score">-</div>
                    <div class="metric-label">Optimization Score</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="words">-</div>
                    <div class="metric-label">Word Count</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="pattern">-</div>
                    <div class="metric-label">Pattern</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('tweetForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const data = {
                topic: document.getElementById('topic').value,
                market: document.getElementById('market').value,
                urgency: document.getElementById('urgency').value,
                sentiment: document.getElementById('sentiment').value,
                insight: document.getElementById('insight').value
            };
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                document.getElementById('output').textContent = result.tweet;
                document.getElementById('output').className = 'success';
                
                document.getElementById('engagement').textContent = result.predicted_engagement.toLocaleString();
                document.getElementById('score').textContent = Math.round(result.optimization_score * 100) + '%';
                document.getElementById('words').textContent = result.word_count;
                document.getElementById('pattern').textContent = result.pattern.split('_')[0];
                
                document.getElementById('metrics').style.display = 'grid';
            } catch (error) {
                document.getElementById('output').textContent = 'Error: ' + error.message;
                document.getElementById('output').className = '';
            }
        });
        
        function setQuick(type) {
            const presets = {
                'btc-fear': {
                    topic: 'Bitcoin',
                    market: 'bearish',
                    urgency: 'high',
                    sentiment: 'fear',
                    insight: 'Smart money accumulating while retail panics'
                },
                'alt-opp': {
                    topic: 'Altcoins',
                    market: 'neutral',
                    urgency: 'medium',
                    sentiment: 'neutral',
                    insight: 'Rotation patterns emerging'
                },
                'risk': {
                    topic: 'Risk Management',
                    market: 'bullish',
                    urgency: 'high',
                    sentiment: 'greed',
                    insight: 'Euphoria marks tops'
                },
                'psych': {
                    topic: 'Market Psychology',
                    market: 'volatile',
                    urgency: 'medium',
                    sentiment: 'confusion',
                    insight: 'Emotions drive 90% of trading decisions'
                }
            };
            
            const preset = presets[type];
            if (preset) {
                document.getElementById('topic').value = preset.topic;
                document.getElementById('market').value = preset.market;
                document.getElementById('urgency').value = preset.urgency;
                document.getElementById('sentiment').value = preset.sentiment;
                document.getElementById('insight').value = preset.insight;
            }
        }
    </script>
</body>
</html>
"""

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Create context
            context = ContextInput(
                topic=data.get('topic', 'market'),
                market_condition=data.get('market', 'neutral'),
                urgency=data.get('urgency', 'medium'),
                target_audience='everyone',
                key_insight=data.get('insight', ''),
                current_sentiment=data.get('sentiment', 'neutral')
            )
            
            # Generate tweet
            result = generator.generate_optimal_tweet(context)
            
            # Send response
            response = {
                'tweet': result.text,
                'pattern': result.pattern_used,
                'predicted_engagement': result.predicted_engagement,
                'optimization_score': result.optimization_score,
                'word_count': result.word_count
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=8080):
    with socketserver.TCPServer(("", port), RequestHandler) as httpd:
        print(f"""
╔══════════════════════════════════════════════════════════╗
║               Miles AI Server - LIVE!                    ║
╚══════════════════════════════════════════════════════════╝

🚀 Server running at: http://localhost:{port}

📊 Features:
- Real-time optimal tweet generation
- 90%+ accuracy Miles style
- Predicted engagement scoring
- Pattern-based optimization

🎯 Quick Start:
1. Open your browser to http://localhost:{port}
2. Enter context (topic, market, urgency, sentiment)
3. Click "Generate Optimal Tweet"
4. Get instant Miles-style tweet with metrics

Press Ctrl+C to stop the server.
        """)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nShutting down server...")
            httpd.shutdown()

if __name__ == '__main__':
    run_server()