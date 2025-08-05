// Miles Deutscher AI - Twitter Testing Interface

// DOM Elements
const tweetInput = document.getElementById('tweetInput');
const charCount = document.getElementById('charCount');
const generateBtn = document.getElementById('generateBtn');
const outputSection = document.getElementById('outputSection');
const outputContainer = document.getElementById('outputContainer');
const analyticsSection = document.getElementById('analyticsSection');
const analyticsContainer = document.getElementById('analyticsContainer');
const loadExamplesBtn = document.getElementById('loadExamplesBtn');
const examplesContainer = document.getElementById('examplesContainer');
const loadingSpinner = document.getElementById('loadingSpinner');

// Event Listeners
tweetInput.addEventListener('input', updateCharCount);
generateBtn.addEventListener('click', generateTweets);
loadExamplesBtn.addEventListener('click', loadExamples);

// Example buttons
document.querySelectorAll('.example-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        tweetInput.value = e.target.dataset.text;
        updateCharCount();
        tweetInput.focus();
    });
});

// Update character count
function updateCharCount() {
    const count = tweetInput.value.length;
    charCount.textContent = `${count} / 280`;
    charCount.style.color = count > 280 ? 'var(--danger-color)' : 'var(--text-secondary)';
}

// Generate tweets
async function generateTweets() {
    const input = tweetInput.value.trim();
    
    if (!input) {
        alert('Please enter some text to generate a tweet');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ input }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayOutputs(data);
            displayAnalytics(data);
        } else {
            alert('Error generating tweets: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Network error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Display generated tweets
function displayOutputs(data) {
    outputContainer.innerHTML = '';
    outputSection.style.display = 'block';
    
    data.outputs.forEach((tweet, index) => {
        const metrics = data.metrics[index];
        
        const tweetDiv = document.createElement('div');
        tweetDiv.className = 'tweet-output';
        
        tweetDiv.innerHTML = `
            <button class="copy-btn" onclick="copyTweet(this, '${escapeHtml(tweet)}')">Copy</button>
            <div class="tweet-text">${escapeHtml(tweet)}</div>
            <div class="tweet-metrics">
                <span class="metric">
                    <span>📏</span> ${metrics.length} chars
                </span>
                <span class="metric">
                    <span>🔥</span> ${metrics.engagement_score}% engagement
                </span>
                ${metrics.has_ticker ? '<span class="metric"><span>💰</span> Has ticker</span>' : ''}
                ${metrics.has_emoji ? '<span class="metric"><span>😊</span> Has emoji</span>' : ''}
            </div>
        `;
        
        outputContainer.appendChild(tweetDiv);
    });
}

// Display analytics
function displayAnalytics(data) {
    analyticsContainer.innerHTML = '';
    analyticsSection.style.display = 'block';
    
    // Calculate aggregate metrics
    const avgLength = Math.round(data.metrics.reduce((sum, m) => sum + m.length, 0) / data.metrics.length);
    const avgEngagement = Math.round(data.metrics.reduce((sum, m) => sum + m.engagement_score, 0) / data.metrics.length);
    const withTickers = data.metrics.filter(m => m.has_ticker).length;
    const withEmojis = data.metrics.filter(m => m.has_emoji).length;
    
    const metricsHTML = `
        <div class="metric-card">
            <div class="metric-value">${avgLength}</div>
            <div class="metric-label">Avg Length</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${avgEngagement}%</div>
            <div class="metric-label">Avg Engagement</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${withTickers}/${data.outputs.length}</div>
            <div class="metric-label">With Tickers</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">${withEmojis}/${data.outputs.length}</div>
            <div class="metric-label">With Emojis</div>
        </div>
    `;
    
    analyticsContainer.innerHTML = metricsHTML;
}

// Load examples
async function loadExamples() {
    showLoading(true);
    
    try {
        const response = await fetch('/examples');
        const data = await response.json();
        
        examplesContainer.innerHTML = '';
        examplesContainer.style.display = 'block';
        
        data.examples.forEach(example => {
            const exampleDiv = document.createElement('div');
            exampleDiv.className = 'example-tweet';
            exampleDiv.textContent = example;
            examplesContainer.appendChild(exampleDiv);
        });
        
        loadExamplesBtn.textContent = 'Refresh Examples';
    } catch (error) {
        alert('Error loading examples: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Copy tweet to clipboard
function copyTweet(button, tweet) {
    navigator.clipboard.writeText(tweet).then(() => {
        button.textContent = 'Copied!';
        button.classList.add('copied');
        
        setTimeout(() => {
            button.textContent = 'Copy';
            button.classList.remove('copied');
        }, 2000);
    });
}

// Show/hide loading spinner
function showLoading(show) {
    loadingSpinner.style.display = show ? 'flex' : 'none';
}

// Escape HTML for security
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to generate
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        generateTweets();
    }
    
    // Escape to clear
    if (e.key === 'Escape') {
        tweetInput.value = '';
        updateCharCount();
        tweetInput.focus();
    }
});

// Auto-focus on load
window.addEventListener('load', () => {
    tweetInput.focus();
});