"""
Miles AI Production Server
Real-time optimal tweet generation with web interface
"""
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json
import logging
from datetime import datetime
from pathlib import Path

# Import our Miles AI systems
from miles_optimal_tweet_generator_blind_test import MilesOptimalGenerator, ContextInput
from miles_mega_framework_top100 import MilesMegaFramework
from miles_optimal_generation_system import ProductionOptimizedSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Miles AI systems
optimal_generator = MilesOptimalGenerator()
mega_framework = MilesMegaFramework()
production_system = ProductionOptimizedSystem()

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Miles AI - Optimal Tweet Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: linear-gradient(135deg, #1DA1F2 0%, #0e76a8 100%);
            padding: 2rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(29, 161, 242, 0.3);
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            flex: 1;
        }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-top: 2rem;
        }
        
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
        
        .card {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 2rem;
            transition: all 0.3s ease;
        }
        
        .card:hover {
            border-color: #1DA1F2;
            box-shadow: 0 8px 32px rgba(29, 161, 242, 0.1);
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #1DA1F2;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 0.75rem 1rem;
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 8px;
            color: #ffffff;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #1DA1F2;
            box-shadow: 0 0 0 3px rgba(29, 161, 242, 0.1);
        }
        
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        .button {
            background: linear-gradient(135deg, #1DA1F2 0%, #0e76a8 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 1rem;
        }
        
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(29, 161, 242, 0.3);
        }
        
        .button:active {
            transform: translateY(0);
        }
        
        .output {
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 1.5rem;
            margin-top: 1.5rem;
            min-height: 150px;
            white-space: pre-wrap;
            line-height: 1.6;
            font-size: 1.1rem;
        }
        
        .output.success {
            border-color: #1DA1F2;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }
        
        .metric {
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }
        
        .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1DA1F2;
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #999;
            margin-top: 0.25rem;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin-top: 1rem;
        }
        
        .spinner {
            border: 3px solid #333;
            border-top: 3px solid #1DA1F2;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: #ff4444;
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            display: none;
        }
        
        .stats {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 2rem;
            margin-top: 2rem;
        }
        
        .stats h3 {
            color: #1DA1F2;
            margin-bottom: 1rem;
        }
        
        .quick-contexts {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        
        .quick-btn {
            background: #1a1a1a;
            border: 1px solid #333;
            color: #fff;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }
        
        .quick-btn:hover {
            border-color: #1DA1F2;
            color: #1DA1F2;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Miles AI</h1>
        <p>Optimal Tweet Generation System - 90%+ Accuracy</p>
    </div>
    
    <div class="container">
        <div class="grid">
            <div class="card">
                <h2>Context Input</h2>
                <form id="tweetForm">
                    <div class="form-group">
                        <label for="topic">Topic</label>
                        <input type="text" id="topic" name="topic" placeholder="e.g., Bitcoin, DeFi, Market Analysis" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="market">Market Condition</label>
                        <select id="market" name="market">
                            <option value="volatile">Volatile</option>
                            <option value="bearish">Bearish</option>
                            <option value="bullish">Bullish</option>
                            <option value="neutral">Neutral</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="urgency">Urgency Level</label>
                        <select id="urgency" name="urgency">
                            <option value="high">High</option>
                            <option value="medium">Medium</option>
                            <option value="low">Low</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="sentiment">Market Sentiment</label>
                        <select id="sentiment" name="sentiment">
                            <option value="fear">Fear</option>
                            <option value="greed">Greed</option>
                            <option value="confusion">Confusion</option>
                            <option value="neutral">Neutral</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="audience">Target Audience</label>
                        <select id="audience" name="audience">
                            <option value="everyone">Everyone</option>
                            <option value="traders">Traders</option>
                            <option value="beginners">Beginners</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="insight">Key Insight (Optional)</label>
                        <textarea id="insight" name="insight" placeholder="e.g., Smart money is accumulating, Market structure shifting"></textarea>
                    </div>
                    
                    <button type="submit" class="button">Generate Optimal Tweet</button>
                </form>
                
                <div class="quick-contexts">
                    <button class="quick-btn" onclick="setQuickContext('btc-fear')">BTC Fear Bottom</button>
                    <button class="quick-btn" onclick="setQuickContext('alt-opportunity')">Alt Opportunity</button>
                    <button class="quick-btn" onclick="setQuickContext('risk-warning')">Risk Warning</button>
                    <button class="quick-btn" onclick="setQuickContext('market-psychology')">Psychology</button>
                </div>
                
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Generating optimal tweet...</p>
                </div>
                
                <div class="error" id="error"></div>
            </div>
            
            <div class="card">
                <h2>Generated Tweet</h2>
                <div class="output" id="tweetOutput">
                    Your optimized tweet will appear here...
                </div>
                
                <div class="metrics" id="metrics" style="display: none;">
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
                        <div class="metric-label">Pattern Used</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="stats">
            <h3>System Statistics</h3>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value" id="totalGenerated">0</div>
                    <div class="metric-label">Total Generated</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="avgEngagement">-</div>
                    <div class="metric-label">Avg Engagement</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="accuracy">90%+</div>
                    <div class="metric-label">Accuracy</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="uptime">100%</div>
                    <div class="metric-label">Uptime</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let totalGenerated = 0;
        let totalEngagement = 0;
        
        document.getElementById('tweetForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const loading = document.querySelector('.loading');
            const error = document.getElementById('error');
            const output = document.getElementById('tweetOutput');
            const metrics = document.getElementById('metrics');
            
            loading.style.display = 'block';
            error.style.display = 'none';
            output.classList.remove('success');
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    output.textContent = result.tweet;
                    output.classList.add('success');
                    
                    document.getElementById('engagement').textContent = result.predicted_engagement.toLocaleString();
                    document.getElementById('score').textContent = (result.optimization_score * 100).toFixed(0) + '%';
                    document.getElementById('words').textContent = result.word_count;
                    document.getElementById('pattern').textContent = result.pattern;
                    
                    metrics.style.display = 'grid';
                    
                    // Update stats
                    totalGenerated++;
                    totalEngagement += result.predicted_engagement;
                    document.getElementById('totalGenerated').textContent = totalGenerated;
                    document.getElementById('avgEngagement').textContent = Math.round(totalEngagement / totalGenerated).toLocaleString();
                } else {
                    throw new Error(result.error || 'Generation failed');
                }
            } catch (err) {
                error.textContent = 'Error: ' + err.message;
                error.style.display = 'block';
            } finally {
                loading.style.display = 'none';
            }
        });
        
        function setQuickContext(type) {
            const contexts = {
                'btc-fear': {
                    topic: 'Bitcoin',
                    market: 'bearish',
                    urgency: 'high',
                    sentiment: 'fear',
                    insight: 'Smart money accumulating at these levels'
                },
                'alt-opportunity': {
                    topic: 'Altcoins',
                    market: 'neutral',
                    urgency: 'medium',
                    sentiment: 'neutral',
                    insight: 'Rotation patterns emerging'
                },
                'risk-warning': {
                    topic: 'Risk Management',
                    market: 'bullish',
                    urgency: 'high',
                    sentiment: 'greed',
                    insight: 'Euphoria marks tops'
                },
                'market-psychology': {
                    topic: 'Market Psychology',
                    market: 'volatile',
                    urgency: 'medium',
                    sentiment: 'confusion',
                    insight: 'Emotions drive 90% of decisions'
                }
            };
            
            const context = contexts[type];
            if (context) {
                document.getElementById('topic').value = context.topic;
                document.getElementById('market').value = context.market;
                document.getElementById('urgency').value = context.urgency;
                document.getElementById('sentiment').value = context.sentiment;
                document.getElementById('audience').value = 'everyone';
                document.getElementById('insight').value = context.insight;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate_tweet():
    """Generate optimal tweet based on context"""
    try:
        data = request.get_json()
        
        # Create context input
        context = ContextInput(
            topic=data.get('topic', 'market'),
            market_condition=data.get('market', 'neutral'),
            urgency=data.get('urgency', 'medium'),
            target_audience=data.get('audience', 'everyone'),
            key_insight=data.get('insight', ''),
            current_sentiment=data.get('sentiment', 'neutral')
        )
        
        # Generate tweet
        result = optimal_generator.generate_optimal_tweet(context)
        
        logger.info(f"Generated tweet: {result.text[:50]}... | Predicted: {result.predicted_engagement}")
        
        return jsonify({
            'success': True,
            'tweet': result.text,
            'pattern': result.pattern_used,
            'predicted_engagement': result.predicted_engagement,
            'optimization_score': result.optimization_score,
            'word_count': result.word_count,
            'structure': result.structure,
            'micro_patterns': result.micro_patterns,
            'rationale': result.rationale
        })
        
    except Exception as e:
        logger.error(f"Error generating tweet: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        stats = production_system.get_performance_metrics()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/patterns', methods=['GET'])
def get_patterns():
    """Get available patterns"""
    try:
        patterns = list(optimal_generator.viral_patterns.keys())
        return jsonify({
            'success': True,
            'patterns': patterns
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    logger.info("Starting Miles AI Server...")
    logger.info("Visit http://localhost:5000 to access the interface")
    
    # Run the server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Set to False in production
        threaded=True
    )