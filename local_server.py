"""
Miles Deutscher AI - Local Testing Server
Complete system for testing input/output dynamics
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import random
import re
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

class MilesAISimulator:
    """
    Simulates Miles AI responses for testing without requiring model deployment
    Uses pattern matching and templates based on analyzed tweet data
    """
    
    def __init__(self):
        self.load_training_data()
        self.patterns = self.extract_patterns()
        
    def load_training_data(self):
        """Load original tweets for pattern matching"""
        self.tweets = []
        if os.path.exists('data.jsonl'):
            with open('data.jsonl', 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line)
                    self.tweets.append(data['completion'].strip())
        
    def extract_patterns(self):
        """Extract Miles's tweet patterns"""
        return {
            "market_bullish": [
                "$TICKER looking absolutely fire right now.\n\nTECHNICAL_REASON\n\nUp only 🚀",
                "TICKER chart is telling a beautiful story.\n\nDETAIL\n\nBullish.",
                "Ser, TICKER is about to melt faces.\n\nREASON\n\nNGMI if you're not paying attention.",
                "TICKER absolutely sending it.\n\nChart speaks for itself.\n\nUp only sers."
            ],
            "market_bearish": [
                "TICKER showing major weakness here.\n\nREASON\n\nProtect your capital.",
                "Warning: TICKER looks ready to dump.\n\nTECHNICAL\n\nNot the dip to buy.",
                "TICKER about to get rekt.\n\nREASON\n\nYou've been warned.",
                "TICKER support broken.\n\nNo buyers in sight.\n\nDown we go."
            ],
            "philosophical": [
                "This is the best time in history to ACTION.\n\nIt's also the worst time to OPPOSITE.\n\nThe choice is yours.",
                "Everyone wants DESIRE.\n\nNobody wants to WORK.\n\nBe nobody.",
                "The market rewards POSITIVE_TRAIT.\n\nIt punishes NEGATIVE_TRAIT.\n\nPosition yourself accordingly."
            ],
            "question_response": [
                "QUESTION\n\nSHORT_ANSWER\n\nELABORATION",
                "QUESTION\n\nThe answer is always liquidity.",
                "QUESTION\n\nAnon, you already know the answer."
            ],
            "quick_take": [
                "STATEMENT\n\nBased.",
                "OBSERVATION\n\nFew understand this.",
                "FACT\n\nThat's the alpha right there.",
                "STATEMENT\n\nThat's the tweet.",
                "OBSERVATION\n\nFew understand this.\n\nUp only."
            ]
        }
    
    def generate_response(self, user_input):
        """Generate Miles-style response based on input"""
        
        input_lower = user_input.lower()
        
        # Detect tickers
        tickers = re.findall(r'\$?([A-Z]{2,5})', user_input.upper())
        ticker = tickers[0] if tickers else "BTC"
        
        # Determine sentiment and type
        if any(word in input_lower for word in ['bull', 'moon', 'pump', 'up']):
            templates = self.patterns['market_bullish']
            sentiment = 'bullish'
        elif any(word in input_lower for word in ['bear', 'dump', 'down', 'crash']):
            templates = self.patterns['market_bearish']
            sentiment = 'bearish'
        elif '?' in user_input:
            templates = self.patterns['question_response']
            sentiment = 'neutral'
        elif any(word in input_lower for word in ['best', 'worst', 'everyone', 'nobody']):
            templates = self.patterns['philosophical']
            sentiment = 'philosophical'
        else:
            templates = self.patterns['quick_take']
            sentiment = 'neutral'
        
        # Generate variations
        responses = []
        
        for template in random.sample(templates, min(3, len(templates))):
            response = template
            response = response.replace('TICKER', f'${ticker}')
            response = response.replace('QUESTION', user_input.strip())
            response = response.replace('STATEMENT', user_input.strip())
            response = response.replace('OBSERVATION', user_input.strip())
            
            # Fill in placeholders with contextual content
            if 'TECHNICAL_REASON' in response:
                reasons = ["Clean break above resistance", "Volume confirming the move", "RSI reset and ready"]
                response = response.replace('TECHNICAL_REASON', random.choice(reasons))
            
            if 'REASON' in response:
                if sentiment == 'bullish':
                    reasons = ["Accumulation phase complete", "Smart money flowing in", "Chart structure intact"]
                else:
                    reasons = ["Support broken with volume", "No buyers in sight", "Momentum fading fast"]
                response = response.replace('REASON', random.choice(reasons))
            
            if 'ACTION' in response:
                actions = ["build in crypto", "be a high agency individual", "take calculated risks"]
                response = response.replace('ACTION', random.choice(actions))
                response = response.replace('OPPOSITE', "wait for perfect conditions")
            
            responses.append(response)
        
        return responses

# Initialize simulator
simulator = MilesAISimulator()

@app.route('/')
def index():
    """Serve the main testing interface"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate Miles-style tweets from input"""
    
    data = request.json
    user_input = data.get('input', '')
    
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    
    # Generate responses
    responses = simulator.generate_response(user_input)
    
    # Calculate metrics
    metrics = []
    for response in responses:
        metric = {
            'length': len(response),
            'has_ticker': '$' in response,
            'has_emoji': any(char in response for char in '🚀🔥💎👇📈📉'),
            'line_breaks': response.count('\n'),
            'engagement_score': calculate_engagement_score(response)
        }
        metrics.append(metric)
    
    return jsonify({
        'input': user_input,
        'outputs': responses,
        'metrics': metrics,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze a tweet for Miles-style compliance"""
    
    data = request.json
    tweet = data.get('tweet', '')
    
    analysis = {
        'length': len(tweet),
        'within_limit': len(tweet) <= 280,
        'structure': analyze_structure(tweet),
        'style_score': calculate_style_score(tweet),
        'suggestions': generate_suggestions(tweet)
    }
    
    return jsonify(analysis)

@app.route('/examples')
def examples():
    """Get example tweets for reference"""
    
    if simulator.tweets:
        examples = random.sample(simulator.tweets, min(10, len(simulator.tweets)))
    else:
        examples = [
            "$BTC looking absolutely fire right now.\n\nClean break above resistance.\n\nUp only 🚀",
            "This is the best time in history to be building.\n\nIt's also the worst time to be waiting.\n\nThe choice is yours.",
            "Unpopular opinion: Bear markets build generational wealth.\n\nBull markets just reveal it.",
            "GM.\n\nToday we're going to make it."
        ]
    
    return jsonify({'examples': examples})

def calculate_engagement_score(tweet):
    """Calculate predicted engagement score"""
    score = 50  # Base score
    
    # Positive factors
    if '?' in tweet:
        score += 10
    if any(word in tweet.lower() for word in ['unpopular opinion', 'thread', 'alpha']):
        score += 15
    if '$' in tweet:
        score += 10
    if len(tweet) < 150:
        score += 5
    if any(emoji in tweet for emoji in ['🚀', '🔥', '💎']):
        score += 10
    
    # Structure bonus
    if tweet.count('\n') == 2:  # Three-part structure
        score += 10
    
    return min(score, 100)

def analyze_structure(tweet):
    """Analyze tweet structure"""
    lines = tweet.strip().split('\n')
    
    if len(lines) == 3:
        return "Perfect three-part structure"
    elif len(lines) == 2:
        return "Two-part structure"
    elif len(lines) == 1:
        return "Single line"
    else:
        return "Multi-line (consider simplifying)"

def calculate_style_score(tweet):
    """Calculate how well tweet matches Miles's style"""
    score = 0
    max_score = 100
    
    # Length check
    if 50 <= len(tweet) <= 200:
        score += 20
    
    # Structure check
    if tweet.count('\n') in [2, 4]:  # Preferred line breaks
        score += 20
    
    # Vocabulary check
    miles_words = ['ser', 'based', 'ngmi', 'wagmi', 'alpha', 'absolutely', 'literally']
    if any(word in tweet.lower() for word in miles_words):
        score += 20
    
    # Market terminology
    if any(term in tweet.lower() for term in ['bull', 'bear', 'chart', 'liquidity']):
        score += 20
    
    # Engagement elements
    if '?' in tweet or any(emoji in tweet for emoji in '🚀🔥💎'):
        score += 20
    
    return score

def generate_suggestions(tweet):
    """Generate improvement suggestions"""
    suggestions = []
    
    if len(tweet) > 280:
        suggestions.append("Shorten tweet to fit Twitter limit")
    
    if '\n' not in tweet and len(tweet) > 100:
        suggestions.append("Consider breaking into multiple lines for better readability")
    
    if '$' not in tweet and any(word in tweet.lower() for word in ['bitcoin', 'ethereum']):
        suggestions.append("Use ticker symbols (e.g., $BTC, $ETH) for better engagement")
    
    if not any(word in tweet.lower() for word in ['ser', 'based', 'alpha', 'gm']):
        suggestions.append("Add crypto-native terminology for authenticity")
    
    return suggestions

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║        Miles Deutscher AI - Local Test Server        ║
    ║                                                      ║
    ║  Starting server at: http://localhost:5000           ║
    ║                                                      ║
    ║  Features:                                           ║
    ║  - Real-time tweet generation                       ║
    ║  - Style analysis and scoring                       ║
    ║  - Input/output testing                             ║
    ║  - Engagement predictions                           ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    app.run(debug=True, port=5000)