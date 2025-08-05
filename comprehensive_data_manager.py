"""
Miles Deutscher AI - Comprehensive Training Data Manager
Complete solution for updating, analyzing, and optimizing training data
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from collections import defaultdict, Counter
import re

class ComprehensiveDataManager:
    """Manages all aspects of training data"""
    
    def __init__(self):
        self.data = []
        self.data_file = self._find_latest_data_file()
        self.stats = {
            'total': 0,
            'structures': defaultdict(int),
            'quality_scores': [],
            'sources': defaultdict(int),
            'duplicates_removed': 0
        }
        self.load_data()
    
    def _find_latest_data_file(self) -> str:
        """Find the most recent training data file"""
        candidates = [
            'miles_training_updated_manual.jsonl',
            'miles_enhanced_updated.jsonl', 
            'miles_1000_enhanced.jsonl',
            'data.jsonl'
        ]
        
        for file in candidates:
            if os.path.exists(file):
                return file
        
        return 'data.jsonl'  # Default
    
    def load_data(self):
        """Load training data from file"""
        if not os.path.exists(self.data_file):
            print(f"No training data found at {self.data_file}")
            return
        
        print(f"Loading data from {self.data_file}...")
        
        seen_hashes = set()
        unique_data = []
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                
                # Check for duplicates
                text = entry.get('completion', '').strip()
                text_hash = hashlib.md5(text.encode()).hexdigest()
                
                if text_hash not in seen_hashes:
                    seen_hashes.add(text_hash)
                    unique_data.append(entry)
                    
                    # Update stats
                    metadata = entry.get('metadata', {})
                    structure = self._get_structure(text)
                    self.stats['structures'][structure] += 1
                    
                    if 'quality_score' in metadata:
                        self.stats['quality_scores'].append(metadata['quality_score'])
                    
                    source = metadata.get('source', 'original')
                    self.stats['sources'][source] += 1
                else:
                    self.stats['duplicates_removed'] += 1
        
        self.data = unique_data
        self.stats['total'] = len(self.data)
        
        print(f"Loaded {len(self.data)} unique examples")
        if self.stats['duplicates_removed'] > 0:
            print(f"Removed {self.stats['duplicates_removed']} duplicates")
    
    def _get_structure(self, text: str) -> str:
        """Get tweet structure"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return f"{len(lines)}_part"
    
    def add_tweets_from_list(self, tweets: List[Dict[str, any]]):
        """Add tweets from a list with metadata"""
        added = 0
        
        for tweet_data in tweets:
            if isinstance(tweet_data, str):
                # Simple string
                text = tweet_data
                quality_score = 0.8
            else:
                # Dict with metadata
                text = tweet_data.get('text', '')
                quality_score = tweet_data.get('quality_score', 0.8)
            
            if self._add_single_tweet(text, quality_score):
                added += 1
        
        print(f"Added {added} new tweets")
        return added
    
    def _add_single_tweet(self, text: str, quality_score: float) -> bool:
        """Add a single tweet"""
        text = text.strip()
        
        # Check for duplicate
        text_hash = hashlib.md5(text.encode()).hexdigest()
        for entry in self.data:
            existing_text = entry.get('completion', '').strip()
            if hashlib.md5(existing_text.encode()).hexdigest() == text_hash:
                return False
        
        # Create entry
        structure = self._get_structure(text)
        
        entry = {
            'prompt': 'Write a tweet in the style of Miles Deutscher:',
            'completion': f" {text}",
            'metadata': {
                'source': 'manual_addition',
                'added_at': datetime.now().isoformat(),
                'quality_score': quality_score,
                'structure': structure
            }
        }
        
        self.data.append(entry)
        self.stats['total'] += 1
        self.stats['structures'][structure] += 1
        self.stats['quality_scores'].append(quality_score)
        
        return True
    
    def optimize_dataset(self):
        """Optimize the dataset by removing low quality entries and balancing"""
        print("\nOptimizing dataset...")
        
        original_count = len(self.data)
        
        # Remove very low quality entries
        if self.stats['quality_scores']:
            avg_quality = sum(self.stats['quality_scores']) / len(self.stats['quality_scores'])
            threshold = max(0.3, avg_quality - 0.3)  # Dynamic threshold
            
            self.data = [
                entry for entry in self.data
                if entry.get('metadata', {}).get('quality_score', 0.5) >= threshold
            ]
            
            print(f"Removed {original_count - len(self.data)} low quality entries (threshold: {threshold:.2f})")
        
        # Balance structures (optional - keep diverse)
        self._recompute_stats()
        
        print(f"Optimized dataset has {len(self.data)} examples")
    
    def _recompute_stats(self):
        """Recompute statistics after changes"""
        self.stats = {
            'total': len(self.data),
            'structures': defaultdict(int),
            'quality_scores': [],
            'sources': defaultdict(int),
            'duplicates_removed': self.stats['duplicates_removed']
        }
        
        for entry in self.data:
            text = entry.get('completion', '').strip()
            metadata = entry.get('metadata', {})
            
            structure = self._get_structure(text)
            self.stats['structures'][structure] += 1
            
            if 'quality_score' in metadata:
                self.stats['quality_scores'].append(metadata['quality_score'])
            
            source = metadata.get('source', 'original')
            self.stats['sources'][source] += 1
    
    def save_dataset(self, filename: Optional[str] = None):
        """Save the dataset"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'miles_training_optimized_{timestamp}.jsonl'
        
        with open(filename, 'w', encoding='utf-8') as f:
            for entry in self.data:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        print(f"\nSaved {len(self.data)} examples to {filename}")
        
        # Save report
        self._save_report(filename)
    
    def _save_report(self, dataset_filename: str):
        """Save detailed report"""
        report = {
            'dataset_file': dataset_filename,
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'total_examples': self.stats['total'],
                'duplicates_removed': self.stats['duplicates_removed'],
                'average_quality': sum(self.stats['quality_scores']) / len(self.stats['quality_scores']) if self.stats['quality_scores'] else 0,
                'structure_distribution': dict(self.stats['structures']),
                'source_distribution': dict(self.stats['sources'])
            },
            'quality_analysis': {
                'high_quality': len([s for s in self.stats['quality_scores'] if s >= 0.7]),
                'medium_quality': len([s for s in self.stats['quality_scores'] if 0.4 <= s < 0.7]),
                'low_quality': len([s for s in self.stats['quality_scores'] if s < 0.4])
            }
        }
        
        report_filename = f'training_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Saved report to {report_filename}")
    
    def display_analysis(self):
        """Display comprehensive analysis"""
        print("\n" + "="*60)
        print("Training Data Analysis")
        print("="*60)
        
        print(f"\nTotal examples: {self.stats['total']}")
        
        print("\nStructure Distribution:")
        for structure, count in sorted(self.stats['structures'].items(), 
                                     key=lambda x: x[1], reverse=True):
            percentage = (count / self.stats['total']) * 100 if self.stats['total'] > 0 else 0
            bar = '#' * int(percentage / 2)
            print(f"  {structure:10} {count:5} ({percentage:5.1f}%) {bar}")
        
        if self.stats['quality_scores']:
            avg_quality = sum(self.stats['quality_scores']) / len(self.stats['quality_scores'])
            print(f"\nQuality Analysis:")
            print(f"  Average score: {avg_quality:.2f}")
            print(f"  High quality:  {len([s for s in self.stats['quality_scores'] if s >= 0.7])}")
            print(f"  Medium quality: {len([s for s in self.stats['quality_scores'] if 0.4 <= s < 0.7])}")
            print(f"  Low quality:   {len([s for s in self.stats['quality_scores'] if s < 0.4])}")
        
        print("\nData Sources:")
        for source, count in sorted(self.stats['sources'].items(), 
                                  key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count}")
        
        print("="*60)
    
    def export_for_ultimate_system(self):
        """Export data optimized for the ultimate system"""
        # Ensure the ultimate system uses the best data
        output_file = 'miles_ultimate_training.jsonl'
        
        # Sort by quality score
        sorted_data = sorted(self.data, 
                           key=lambda x: x.get('metadata', {}).get('quality_score', 0.5), 
                           reverse=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in sorted_data:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        print(f"\nExported {len(sorted_data)} examples to {output_file}")
        print("To use with ultimate system, rename to 'data.jsonl' or update system config")

# High-quality tweet examples
HIGH_QUALITY_TWEETS = [
    {
        'text': "The overhang narrative is just cope.\n\nWhat actually matters: positioning for the liquidity injection.\n\nUntil then? Range bound chop.",
        'quality_score': 0.95
    },
    {
        'text': "Alt season isn't a calendar event.\n\nIt's a liquidity phenomenon.\n\nStop watching dates, start watching flows.",
        'quality_score': 0.95
    },
    {
        'text': "Your portfolio doesn't need 50 altcoins.\n\nIt needs 5-10 high conviction plays.\n\nQuality > quantity in a liquidity crisis.",
        'quality_score': 0.9
    },
    {
        'text': "Everyone's an expert in a bull market.\n\nReal skill shows in the bear.\n\nSurvival is the name of the game.",
        'quality_score': 0.9
    },
    {
        'text': "Macro > narrative > technicals.\n\nIn that order.\n\nIgnore at your own peril.",
        'quality_score': 0.85
    }
]

def main_menu():
    """Main interactive menu"""
    manager = ComprehensiveDataManager()
    
    while True:
        print("\n" + "="*60)
        print("Miles Deutscher AI - Training Data Manager")
        print("="*60)
        print("\n1. Display current analysis")
        print("2. Add high-quality examples")
        print("3. Optimize dataset")
        print("4. Export for ultimate system")
        print("5. Save and exit")
        print("6. Exit without saving")
        
        choice = input("\nSelect option (1-6): ")
        
        if choice == '1':
            manager.display_analysis()
        
        elif choice == '2':
            print("\nAdding high-quality examples...")
            added = manager.add_tweets_from_list(HIGH_QUALITY_TWEETS)
            if added > 0:
                print("Examples added successfully!")
        
        elif choice == '3':
            manager.optimize_dataset()
            manager.display_analysis()
        
        elif choice == '4':
            manager.export_for_ultimate_system()
        
        elif choice == '5':
            manager.save_dataset()
            print("\nData saved successfully!")
            break
        
        elif choice == '6':
            confirm = input("Exit without saving? (y/n): ")
            if confirm.lower() == 'y':
                break
        
        else:
            print("Invalid option")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        # Automatic mode - add examples and optimize
        manager = ComprehensiveDataManager()
        manager.display_analysis()
        
        print("\nAdding high-quality examples...")
        manager.add_tweets_from_list(HIGH_QUALITY_TWEETS)
        
        manager.optimize_dataset()
        manager.export_for_ultimate_system()
        manager.save_dataset()
    else:
        # Interactive mode
        main_menu()