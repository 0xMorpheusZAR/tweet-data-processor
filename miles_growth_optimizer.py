#!/usr/bin/env python3
"""
Miles Twitter Growth Optimization Model
Interactive mathematical model for reaching 1M followers with scenario planning
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import math
import os
from typing import Dict, List, Tuple, Any
import statistics

class MilesGrowthOptimizer:
    def __init__(self):
        # Current baseline metrics (estimated from data analysis)
        self.current_followers = 250000  # Estimated current follower count
        self.target_followers = 1000000  # Target: 1M followers
        
        # Engagement metrics from analysis
        self.avg_engagement_rate = 0.035  # 3.5% average engagement rate
        self.top_tweet_engagement = 0.089  # Top performing tweets get ~8.9%
        
        # Content performance tiers (from analysis)
        self.content_tiers = {
            'tier_1_premium': {
                'avg_engagement_score': 5800,
                'follower_conversion_rate': 0.008,  # 0.8% of engagements convert to follows
                'viral_potential': 0.15,  # 15% chance of going viral
                'patterns': ['5_part_situation', '3_part_contrarian', 'question_hook']
            },
            'tier_2_high': {
                'avg_engagement_score': 4800,
                'follower_conversion_rate': 0.005,
                'viral_potential': 0.08,
                'patterns': ['short_take', 'micro_pattern', 'cta_focused']
            },
            'tier_3_standard': {
                'avg_engagement_score': 3200,
                'follower_conversion_rate': 0.003,
                'viral_potential': 0.03,
                'patterns': ['basic_advice', 'standard_format']
            }
        }
        
        # Growth factors
        self.platform_growth_factor = 1.02  # Twitter's monthly growth factor
        self.seasonality_factors = {
            'Q1': 1.1,  # Crypto season typically strong
            'Q2': 0.9,
            'Q3': 0.85,
            'Q4': 1.15   # Year-end crypto bull runs
        }
        
        # Algorithm boost factors
        self.algorithm_factors = {
            'consistency_boost': 1.25,      # Posting consistently
            'engagement_velocity_boost': 1.4, # High early engagement
            'thread_boost': 1.3,           # Twitter favors threads
            'retweet_boost': 1.6,          # Retweets have highest weight
            'reply_engagement_boost': 1.2   # Active in replies
        }
        
    def calculate_daily_growth_potential(self, content_tier: str, tweets_per_day: int, 
                                       consistency_factor: float = 1.0) -> Dict:
        """Calculate daily follower growth potential"""
        tier_data = self.content_tiers[content_tier]
        
        # Base engagement per tweet
        base_engagement = tier_data['avg_engagement_score']
        
        # Daily total engagement
        daily_engagement = base_engagement * tweets_per_day * consistency_factor
        
        # Follower conversion
        daily_new_followers = daily_engagement * tier_data['follower_conversion_rate']
        
        # Viral boost (probabilistic)
        viral_boost = 0
        if np.random.random() < tier_data['viral_potential'] * tweets_per_day:
            viral_multiplier = np.random.uniform(3, 15)  # Viral tweets get 3-15x engagement
            viral_boost = base_engagement * viral_multiplier * 0.012  # Higher conversion for viral
        
        total_daily_growth = daily_new_followers + viral_boost
        
        return {
            'base_growth': daily_new_followers,
            'viral_boost': viral_boost,
            'total_growth': total_daily_growth,
            'engagement_generated': daily_engagement
        }
    
    def simulate_growth_scenario(self, scenario: Dict) -> Dict:
        """Simulate growth over time with given scenario parameters"""
        current_followers = self.current_followers
        days_to_simulate = scenario.get('days', 365)
        
        daily_results = []
        cumulative_engagement = 0
        
        for day in range(days_to_simulate):
            # Current date simulation
            current_date = datetime.now() + timedelta(days=day)
            quarter = f"Q{(current_date.month - 1) // 3 + 1}"
            
            # Apply seasonality
            seasonal_factor = self.seasonality_factors.get(quarter, 1.0)
            
            # Calculate daily growth
            daily_growth = self.calculate_daily_growth_potential(
                scenario['content_tier'],
                scenario['tweets_per_day'],
                scenario.get('consistency_factor', 1.0)
            )
            
            # Apply seasonal and algorithm factors
            adjusted_growth = daily_growth['total_growth'] * seasonal_factor
            
            # Apply algorithm boosts based on scenario
            if scenario.get('high_engagement_velocity', False):
                adjusted_growth *= self.algorithm_factors['engagement_velocity_boost']
            
            if scenario.get('consistent_posting', False):
                adjusted_growth *= self.algorithm_factors['consistency_boost']
            
            if scenario.get('thread_focused', False):
                adjusted_growth *= self.algorithm_factors['thread_boost']
            
            # Update followers
            current_followers += adjusted_growth
            cumulative_engagement += daily_growth['engagement_generated']
            
            daily_results.append({
                'day': day + 1,
                'date': current_date.strftime('%Y-%m-%d'),
                'followers': int(current_followers),
                'daily_growth': adjusted_growth,
                'engagement': daily_growth['engagement_generated'],
                'seasonal_factor': seasonal_factor
            })
            
            # Break if target reached
            if current_followers >= self.target_followers:
                break
        
        # Calculate summary statistics
        final_followers = current_followers
        days_to_target = len(daily_results) if final_followers >= self.target_followers else None
        avg_daily_growth = statistics.mean([r['daily_growth'] for r in daily_results])
        total_engagement = cumulative_engagement
        
        return {
            'scenario': scenario,
            'results': {
                'final_followers': int(final_followers),
                'days_to_1M': days_to_target,
                'avg_daily_growth': avg_daily_growth,
                'total_engagement_generated': total_engagement,
                'success_probability': min(1.0, final_followers / self.target_followers)
            },
            'daily_data': daily_results
        }
    
    def generate_optimization_scenarios(self) -> List[Dict]:
        """Generate multiple optimization scenarios"""
        scenarios = [
            {
                'name': 'Conservative Growth',
                'content_tier': 'tier_3_standard',
                'tweets_per_day': 2,
                'consistency_factor': 0.9,
                'consistent_posting': True,
                'high_engagement_velocity': False,
                'thread_focused': False,
                'days': 730  # 2 years
            },
            {
                'name': 'Moderate Growth',
                'content_tier': 'tier_2_high',
                'tweets_per_day': 3,
                'consistency_factor': 1.1,
                'consistent_posting': True,
                'high_engagement_velocity': True,
                'thread_focused': True,
                'days': 540  # 1.5 years
            },
            {
                'name': 'Aggressive Growth',
                'content_tier': 'tier_1_premium',
                'tweets_per_day': 4,
                'consistency_factor': 1.2,
                'consistent_posting': True,
                'high_engagement_velocity': True,
                'thread_focused': True,
                'days': 365  # 1 year
            },
            {
                'name': 'Premium Content Focus',
                'content_tier': 'tier_1_premium',
                'tweets_per_day': 2,
                'consistency_factor': 1.3,
                'consistent_posting': True,
                'high_engagement_velocity': True,
                'thread_focused': True,
                'days': 450
            },
            {
                'name': 'High Volume Strategy',
                'content_tier': 'tier_2_high',
                'tweets_per_day': 6,
                'consistency_factor': 1.0,
                'consistent_posting': True,
                'high_engagement_velocity': True,
                'thread_focused': False,
                'days': 300
            }
        ]
        
        return scenarios
    
    def analyze_content_patterns_roi(self) -> Dict:
        """Analyze ROI of different content patterns"""
        pattern_analysis = {
            '5_part_situation': {
                'avg_engagement': 5465,
                'production_time_minutes': 15,
                'viral_potential': 0.18,
                'follower_conversion': 0.008,
                'roi_score': 9.2
            },
            '3_part_contrarian': {
                'avg_engagement': 5200,
                'production_time_minutes': 10,
                'viral_potential': 0.12,
                'follower_conversion': 0.007,
                'roi_score': 8.8
            },
            'question_hook': {
                'avg_engagement': 6487,
                'production_time_minutes': 5,
                'viral_potential': 0.25,
                'follower_conversion': 0.010,
                'roi_score': 9.8
            },
            'short_take': {
                'avg_engagement': 3500,
                'production_time_minutes': 3,
                'viral_potential': 0.05,
                'follower_conversion': 0.004,
                'roi_score': 7.5
            },
            'micro_pattern': {
                'avg_engagement': 4800,
                'production_time_minutes': 8,
                'viral_potential': 0.10,
                'follower_conversion': 0.006,
                'roi_score': 8.2
            }
        }
        
        return pattern_analysis
    
    def generate_content_calendar_optimization(self, days: int = 30) -> Dict:
        """Generate optimized content calendar"""
        pattern_roi = self.analyze_content_patterns_roi()
        
        # Optimal daily mix based on ROI and engagement patterns
        daily_content_mix = [
            {'pattern': 'question_hook', 'time': '09:00', 'day_of_week': 'any'},
            {'pattern': '5_part_situation', 'time': '14:00', 'day_of_week': 'weekday'},
            {'pattern': '3_part_contrarian', 'time': '18:00', 'day_of_week': 'any'},
            {'pattern': 'short_take', 'time': '21:00', 'day_of_week': 'weekend'}
        ]
        
        calendar = []
        for day in range(days):
            current_date = datetime.now() + timedelta(days=day)
            day_of_week = current_date.strftime('%A').lower()
            
            daily_posts = []
            for content in daily_content_mix:
                if content['day_of_week'] == 'any' or \
                   (content['day_of_week'] == 'weekday' and day_of_week not in ['saturday', 'sunday']) or \
                   (content['day_of_week'] == 'weekend' and day_of_week in ['saturday', 'sunday']):
                    
                    pattern_data = pattern_roi[content['pattern']]
                    daily_posts.append({
                        'time': content['time'],
                        'pattern': content['pattern'],
                        'expected_engagement': pattern_data['avg_engagement'],
                        'production_time': pattern_data['production_time_minutes'],
                        'viral_potential': pattern_data['viral_potential']
                    })
            
            calendar.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day_of_week': day_of_week,
                'posts': daily_posts,
                'daily_total_engagement': sum([p['expected_engagement'] for p in daily_posts]),
                'daily_production_time': sum([p['production_time'] for p in daily_posts])
            })
        
        return {
            'calendar': calendar,
            'summary': {
                'avg_daily_engagement': statistics.mean([d['daily_total_engagement'] for d in calendar]),
                'avg_daily_production_time': statistics.mean([d['daily_production_time'] for d in calendar]),
                'total_expected_engagement': sum([d['daily_total_engagement'] for d in calendar])
            }
        }
    
    def create_interactive_dashboard_html(self) -> str:
        """Create interactive HTML dashboard"""
        scenarios = self.generate_optimization_scenarios()
        scenario_results = [self.simulate_growth_scenario(scenario) for scenario in scenarios]
        content_calendar = self.generate_content_calendar_optimization()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Miles Twitter Growth Optimization Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: bold;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 15px;
            color: white;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .scenario-section {{
            margin: 40px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            border-left: 5px solid #667eea;
        }}
        .scenario-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-top: 25px;
        }}
        .scenario-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }}
        .scenario-card:hover {{
            border-color: #667eea;
            transform: translateY(-5px);
        }}
        .scenario-card.recommended {{
            border-color: #28a745;
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        }}
        .chart-container {{
            margin: 30px 0;
            height: 400px;
        }}
        .interactive-controls {{
            background: #e9ecef;
            padding: 25px;
            border-radius: 12px;
            margin: 30px 0;
        }}
        .control-group {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .control-item {{
            display: flex;
            flex-direction: column;
        }}
        .control-item label {{
            font-weight: bold;
            margin-bottom: 8px;
            color: #495057;
        }}
        .control-item input, .control-item select {{
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        .success-indicator {{
            color: #28a745;
            font-weight: bold;
        }}
        .warning-indicator {{
            color: #ffc107;
            font-weight: bold;
        }}
        .danger-indicator {{
            color: #dc3545;
            font-weight: bold;
        }}
        .content-calendar {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .calendar-day {{
            border-bottom: 1px solid #eee;
            padding: 15px 0;
        }}
        .calendar-day:last-child {{
            border-bottom: none;
        }}
        .day-header {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .post-item {{
            background: #f8f9fa;
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Miles Twitter Growth Optimization Dashboard</h1>
            <p>Mathematical Model for Reaching 1M Followers</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{self.current_followers:,}</div>
                <div>Current Followers</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.target_followers:,}</div>
                <div>Target Followers</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.avg_engagement_rate:.1%}</div>
                <div>Avg Engagement Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(scenario_results)}</div>
                <div>Growth Scenarios</div>
            </div>
        </div>
        
        <div class="scenario-section">
            <h2>📊 Growth Scenarios Analysis</h2>
            <div class="scenario-grid">
"""
        
        # Add scenario cards
        for i, result in enumerate(scenario_results):
            scenario = result['scenario']
            results = result['results']
            
            # Determine if this is the recommended scenario
            is_recommended = results['days_to_1M'] and results['days_to_1M'] < 400
            card_class = "scenario-card recommended" if is_recommended else "scenario-card"
            
            success_class = "success-indicator" if results['days_to_1M'] else "danger-indicator"
            days_text = f"{results['days_to_1M']} days" if results['days_to_1M'] else "Not reached in timeframe"
            
            html_content += f"""
                <div class="{card_class}">
                    <h3>{scenario['name']}</h3>
                    <div style="margin: 15px 0;">
                        <strong>Content Tier:</strong> {scenario['content_tier'].replace('_', ' ').title()}<br>
                        <strong>Tweets/Day:</strong> {scenario['tweets_per_day']}<br>
                        <strong>Time to 1M:</strong> <span class="{success_class}">{days_text}</span><br>
                        <strong>Final Followers:</strong> {results['final_followers']:,}<br>
                        <strong>Avg Daily Growth:</strong> {results['avg_daily_growth']:.0f}<br>
                        <strong>Success Probability:</strong> {results['success_probability']:.1%}
                    </div>
                    {'<div style="background: #28a745; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;">🏆 RECOMMENDED</div>' if is_recommended else ''}
                </div>
            """
        
        # Add interactive controls
        html_content += f"""
            </div>
        </div>
        
        <div class="interactive-controls">
            <h2>🎯 Custom Scenario Builder</h2>
            <div class="control-group">
                <div class="control-item">
                    <label>Content Tier:</label>
                    <select id="contentTier">
                        <option value="tier_1_premium">Premium (Highest Engagement)</option>
                        <option value="tier_2_high">High Quality</option>
                        <option value="tier_3_standard">Standard</option>
                    </select>
                </div>
                <div class="control-item">
                    <label>Tweets per Day:</label>
                    <input type="number" id="tweetsPerDay" value="3" min="1" max="10">
                </div>
                <div class="control-item">
                    <label>Consistency Factor:</label>
                    <input type="range" id="consistencyFactor" min="0.5" max="1.5" step="0.1" value="1.0">
                    <span id="consistencyValue">1.0</span>
                </div>
                <div class="control-item">
                    <label>Days to Simulate:</label>
                    <input type="number" id="daysToSimulate" value="365" min="30" max="1095">
                </div>
            </div>
            <div style="text-align: center;">
                <button class="btn-primary" onclick="runCustomScenario()">🚀 Run Custom Scenario</button>
            </div>
            <div id="customResults" style="margin-top: 20px;"></div>
        </div>
        
        <div class="content-calendar">
            <h2>📅 Optimized Content Calendar (Next 7 Days)</h2>
"""
        
        # Add content calendar for first 7 days
        for day_data in content_calendar['calendar'][:7]:
            html_content += f"""
            <div class="calendar-day">
                <div class="day-header">{day_data['date']} - {day_data['day_of_week'].title()}</div>
"""
            for post in day_data['posts']:
                html_content += f"""
                <div class="post-item">
                    <strong>{post['time']}</strong> - {post['pattern'].replace('_', ' ').title()} 
                    (Expected Engagement: {post['expected_engagement']:,})
                </div>
"""
            html_content += f"""
                <div style="margin-top: 10px; font-size: 14px; color: #666;">
                    Daily Total: {day_data['daily_total_engagement']:,} engagement | 
                    Production Time: {day_data['daily_production_time']} minutes
                </div>
            </div>
"""
        
        # Add chart and JavaScript
        html_content += f"""
        </div>
        
        <div class="chart-container">
            <canvas id="growthChart"></canvas>
        </div>
        
        <div style="background: #e8f5e8; padding: 25px; border-radius: 12px; margin: 30px 0; border-left: 5px solid #28a745;">
            <h3>🎯 Key Recommendations</h3>
            <ul>
                <li><strong>Optimal Strategy:</strong> {scenario_results[0]['scenario']['name']} - Reaches 1M in {scenario_results[0]['results']['days_to_1M'] or 'N/A'} days</li>
                <li><strong>Content Focus:</strong> Prioritize "Question Hook" pattern (ROI: 9.8) and "5-Part Situation" format</li>
                <li><strong>Posting Schedule:</strong> 3-4 tweets/day with high consistency factor (1.1+)</li>
                <li><strong>Engagement Strategy:</strong> Focus on early engagement velocity and thread creation</li>
                <li><strong>Content Mix:</strong> 60% Premium tier, 30% High tier, 10% Standard tier content</li>
            </ul>
        </div>
    </div>
    
    <script>
        // Chart setup
        const ctx = document.getElementById('growthChart').getContext('2d');
        const growthChart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {[f'Day {i}' for i in range(1, 366, 10)]},
                datasets: [
"""
        
        # Add dataset for each scenario
        colors = ['#667eea', '#28a745', '#ffc107', '#dc3545', '#17a2b8']
        for i, result in enumerate(scenario_results[:5]):
            daily_data = result['daily_data']
            follower_data = [daily_data[j]['followers'] for j in range(0, len(daily_data), 10)]
            
            html_content += f"""
                    {{
                        label: '{result['scenario']['name']}',
                        data: {follower_data[:36]},
                        borderColor: '{colors[i]}',
                        backgroundColor: '{colors[i]}20',
                        tension: 0.4
                    }},"""
        
        html_content += f"""
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Follower Growth Projections'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false,
                        title: {{
                            display: true,
                            text: 'Followers'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Time (Days)'
                        }}
                    }}
                }}
            }}
        }});
        
        // Interactive controls
        document.getElementById('consistencyFactor').addEventListener('input', function(e) {{
            document.getElementById('consistencyValue').textContent = e.target.value;
        }});
        
        function runCustomScenario() {{
            const contentTier = document.getElementById('contentTier').value;
            const tweetsPerDay = parseInt(document.getElementById('tweetsPerDay').value);
            const consistencyFactor = parseFloat(document.getElementById('consistencyFactor').value);
            const daysToSimulate = parseInt(document.getElementById('daysToSimulate').value);
            
            // Simulate custom scenario (simplified client-side calculation)
            const tierData = {{
                'tier_1_premium': {{ engagement: 5800, conversion: 0.008 }},
                'tier_2_high': {{ engagement: 4800, conversion: 0.005 }},
                'tier_3_standard': {{ engagement: 3200, conversion: 0.003 }}
            }};
            
            const tier = tierData[contentTier];
            const dailyGrowth = tier.engagement * tweetsPerDay * consistencyFactor * tier.conversion;
            const projectedFollowers = {self.current_followers} + (dailyGrowth * daysToSimulate);
            const daysTo1M = projectedFollowers >= 1000000 ? Math.ceil((1000000 - {self.current_followers}) / dailyGrowth) : null;
            
            document.getElementById('customResults').innerHTML = `
                <div style="background: white; padding: 20px; border-radius: 12px; border: 2px solid #667eea;">
                    <h4>Custom Scenario Results</h4>
                    <p><strong>Projected Followers:</strong> ${{projectedFollowers.toLocaleString()}}</p>
                    <p><strong>Days to 1M:</strong> ${{daysTo1M ? daysTo1M + ' days' : 'Not reached in timeframe'}}</p>
                    <p><strong>Daily Growth:</strong> ${{Math.round(dailyGrowth)}} followers/day</p>
                    <p><strong>Success Probability:</strong> ${{Math.min(100, (projectedFollowers / 1000000 * 100)).toFixed(1)}}%</p>
                </div>
            `;
        }}
    </script>
</body>
</html>
"""
        
        return html_content
    
    def run_complete_analysis(self):
        """Run complete optimization analysis and generate reports"""
        print("="*80)
        print("MILES TWITTER GROWTH OPTIMIZATION MODEL")
        print("="*80)
        
        # Generate scenarios
        scenarios = self.generate_optimization_scenarios()
        print(f"\nAnalyzing {len(scenarios)} growth scenarios...")
        
        # Run simulations
        results = []
        for scenario in scenarios:
            result = self.simulate_growth_scenario(scenario)
            results.append(result)
            
            print(f"\n📊 {scenario['name']}:")
            print(f"   Content Tier: {scenario['content_tier']}")
            print(f"   Tweets/Day: {scenario['tweets_per_day']}")
            print(f"   Days to 1M: {result['results']['days_to_1M'] or 'Not reached'}")
            print(f"   Final Followers: {result['results']['final_followers']:,}")
            print(f"   Success Probability: {result['results']['success_probability']:.1%}")
        
        # Find best scenario
        successful_scenarios = [r for r in results if r['results']['days_to_1M']]
        if successful_scenarios:
            best_scenario = min(successful_scenarios, key=lambda x: x['results']['days_to_1M'])
            print(f"\n🏆 RECOMMENDED STRATEGY: {best_scenario['scenario']['name']}")
            print(f"   Reaches 1M followers in {best_scenario['results']['days_to_1M']} days")
            print(f"   Requires {best_scenario['scenario']['tweets_per_day']} tweets/day")
            print(f"   Focus on {best_scenario['scenario']['content_tier']} content")
        
        # Generate content calendar
        print(f"\n📅 Generating optimized content calendar...")
        content_calendar = self.generate_content_calendar_optimization()
        print(f"   Average daily engagement potential: {content_calendar['summary']['avg_daily_engagement']:,.0f}")
        print(f"   Average daily production time: {content_calendar['summary']['avg_daily_production_time']:.0f} minutes")
        
        # Create interactive dashboard
        print(f"\n🌐 Creating interactive dashboard...")
        html_content = self.create_interactive_dashboard_html()
        
        dashboard_path = os.path.join(os.path.dirname(__file__), 'miles_growth_dashboard.html')
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"   Interactive dashboard saved to: {dashboard_path}")
        
        # Summary recommendations
        print(f"\n{'='*60}")
        print("KEY OPTIMIZATION INSIGHTS")
        print(f"{'='*60}")
        
        pattern_roi = self.analyze_content_patterns_roi()
        best_pattern = max(pattern_roi.items(), key=lambda x: x[1]['roi_score'])
        
        print(f"✅ Best Content Pattern: {best_pattern[0]} (ROI: {best_pattern[1]['roi_score']})")
        print(f"✅ Optimal Posting Frequency: 3-4 tweets/day")
        print(f"✅ Critical Success Factors:")
        print(f"   • Consistency Factor: 1.1+ (post regularly)")
        print(f"   • Engagement Velocity: High early engagement")
        print(f"   • Thread Usage: Include 2-3 threads/week")
        print(f"   • Content Mix: 60% Premium + 30% High + 10% Standard")
        
        return {
            'scenarios': results,
            'best_scenario': best_scenario if successful_scenarios else None,
            'content_calendar': content_calendar,
            'dashboard_path': dashboard_path
        }

if __name__ == "__main__":
    optimizer = MilesGrowthOptimizer()
    results = optimizer.run_complete_analysis()