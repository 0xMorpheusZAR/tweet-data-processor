"""
Miles Deutscher AI - Manual Training Data Update
Allows manual addition of new tweets and data optimization
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict
import re

class ManualTrainingUpdater:
    """Manual training data management"""
    
    def __init__(self):
        self.existing_data = []
        self.new_entries = []
        self.load_existing_data()
        
    def load_existing_data(self):
        """Load existing training data"""
        data_files = ['miles_enhanced_updated.jsonl', 'miles_1000_enhanced.jsonl', 'data.jsonl']
        
        for file_name in data_files:
            if os.path.exists(file_name):
                print(f"Loading data from {file_name}...")
                with open(file_name, 'r', encoding='utf-8') as f:
                    for line in f:
                        self.existing_data.append(json.loads(line))
                print(f"Loaded {len(self.existing_data)} existing examples")
                break
    
    def add_tweet(self, text: str, quality_score: float = 0.8):
        """Add a single tweet to training data"""
        # Clean the text
        text = text.strip()
        
        # Check for duplicates
        text_hash = hashlib.md5(text.encode()).hexdigest()
        for entry in self.existing_data:
            existing_text = entry.get('completion', '').strip()
            if hashlib.md5(existing_text.encode()).hexdigest() == text_hash:
                print("Tweet already exists in training data!")
                return False
        
        # Analyze structure
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        structure = f"{len(lines)}_part"
        
        # Create entry
        entry = {
            'prompt': 'Write a tweet in the style of Miles Deutscher:',
            'completion': f" {text}",
            'metadata': {
                'source': 'manual_addition',
                'added_at': datetime.now().isoformat(),
                'quality_score': quality_score,
                'structure': structure,
                'manually_verified': True
            }
        }
        
        self.new_entries.append(entry)
        print(f"Added tweet with {structure} structure")
        return True
    
    def add_batch(self, tweets: List[str]):
        """Add multiple tweets"""
        added = 0
        for tweet in tweets:
            if self.add_tweet(tweet):
                added += 1
        
        print(f"\nAdded {added} new tweets to training data")
    
    def save_updates(self):
        """Save updated training data"""
        if not self.new_entries:
            print("No new entries to save")
            return
        
        # Combine data
        all_data = self.existing_data + self.new_entries
        
        # Save to new file
        output_file = 'miles_training_updated_manual.jsonl'
        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in all_data:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        print(f"\nSaved {len(all_data)} total examples to {output_file}")
        print(f"Added {len(self.new_entries)} new examples")
        
        # Create summary
        self.create_summary(all_data)
    
    def create_summary(self, data: List[Dict]):
        """Create summary of training data"""
        structures = {}
        sources = {}
        
        for entry in data:
            metadata = entry.get('metadata', {})
            
            structure = metadata.get('structure', 'unknown')
            structures[structure] = structures.get(structure, 0) + 1
            
            source = metadata.get('source', 'original')
            sources[source] = sources.get(source, 0) + 1
        
        summary = {
            'total_examples': len(data),
            'structure_distribution': structures,
            'source_distribution': sources,
            'new_additions': len(self.new_entries),
            'update_timestamp': datetime.now().isoformat()
        }
        
        with open('training_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\nTraining Data Summary:")
        print(f"Total examples: {summary['total_examples']}")
        print("\nStructure distribution:")
        for structure, count in sorted(structures.items(), key=lambda x: x[1], reverse=True):
            print(f"  {structure}: {count}")

def interactive_mode():
    """Interactive mode for adding tweets"""
    updater = ManualTrainingUpdater()
    
    print("\n" + "="*60)
    print("Miles Deutscher AI - Manual Training Update")
    print("="*60)
    print("\nCommands:")
    print("  add <tweet>  - Add a single tweet")
    print("  batch        - Add multiple tweets")
    print("  save         - Save updates")
    print("  quit         - Exit without saving")
    print("  help         - Show commands")
    print("="*60)
    
    while True:
        command = input("\n> ").strip()
        
        if command.startswith("add "):
            tweet_text = command[4:].strip()
            if tweet_text:
                # Handle multi-line input
                if '\\n' in tweet_text:
                    tweet_text = tweet_text.replace('\\n', '\n')
                updater.add_tweet(tweet_text)
            else:
                print("Please provide tweet text")
        
        elif command == "batch":
            print("Enter tweets (one per line, empty line to finish):")
            tweets = []
            while True:
                line = input()
                if not line:
                    break
                tweets.append(line)
            
            if tweets:
                updater.add_batch(tweets)
        
        elif command == "save":
            updater.save_updates()
            break
        
        elif command == "quit":
            if updater.new_entries:
                confirm = input("You have unsaved changes. Really quit? (y/n): ")
                if confirm.lower() == 'y':
                    break
            else:
                break
        
        elif command == "help":
            print("\nCommands:")
            print("  add <tweet>  - Add a single tweet")
            print("  batch        - Add multiple tweets")
            print("  save         - Save updates")
            print("  quit         - Exit without saving")
        
        else:
            print("Unknown command. Type 'help' for commands.")

# Example high-quality tweets to add
EXAMPLE_TWEETS = [
    """The merge narrative was peak euphoria.

What actually mattered: macro liquidity conditions.

Tale as old as time.""",
    
    """Your favorite influencer pumping bags ≠ investment thesis.

Do your own research or become exit liquidity.

Choice is yours.""",
    
    """BTC dominance telling the real story.

Alts bleeding while everyone's calling for alt season.

Patience pays.""",
    
    """Market makers don't care about your TA.

They care about liquidity zones and stop losses.

Trade accordingly.""",
    
    """Everyone wants 100x gains.

Nobody wants to hold through 90% drawdowns.

This is why few make it."""
]

def add_examples():
    """Add example tweets to training data"""
    updater = ManualTrainingUpdater()
    
    print("\nAdding example high-quality tweets...")
    for tweet in EXAMPLE_TWEETS:
        print(f"\nAdding: {tweet[:50]}...")
        updater.add_tweet(tweet, quality_score=0.9)
    
    updater.save_updates()

# Analyze existing data
def analyze_current_data():
    """Analyze current training data"""
    data_file = None
    for f in ['miles_enhanced_updated.jsonl', 'miles_1000_enhanced.jsonl', 'data.jsonl']:
        if os.path.exists(f):
            data_file = f
            break
    
    if not data_file:
        print("No training data found")
        return
    
    data = []
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    
    print(f"\nAnalyzing {data_file}")
    print(f"Total examples: {len(data)}")
    
    # Structure analysis
    structures = {}
    for entry in data:
        text = entry.get('completion', '').strip()
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        structure = f"{len(lines)}_part"
        structures[structure] = structures.get(structure, 0) + 1
    
    print("\nStructure distribution:")
    for struct, count in sorted(structures.items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = (count / len(data)) * 100
        print(f"  {struct}: {count} ({percentage:.1f}%)")
    
    # Sample tweets
    print("\nSample tweets:")
    import random
    samples = random.sample(data, min(3, len(data)))
    for i, sample in enumerate(samples, 1):
        text = sample.get('completion', '').strip()
        print(f"\n{i}. {text[:150]}..." if len(text) > 150 else f"\n{i}. {text}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "examples":
            add_examples()
        elif sys.argv[1] == "analyze":
            analyze_current_data()
    else:
        interactive_mode()