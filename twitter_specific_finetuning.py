"""
Twitter/X-Specific Fine-tuning System for Miles Deutscher AI
Optimized for: Text Input → Miles-style Tweet Output
"""

import json
import re
from typing import Dict, List, Tuple, Optional
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments
import numpy as np

class TwitterMilesAI:
    """
    Specialized system for converting any text input into Miles Deutscher-style tweets
    """
    
    def __init__(self):
        self.max_tweet_length = 280  # Twitter's character limit
        self.style_patterns = self.load_miles_patterns()
        
    def load_miles_patterns(self) -> Dict:
        """Extract Miles's specific Twitter writing patterns"""
        return {
            "openings": {
                "market_analysis": ["$BTC", "$ETH", "Chart shows", "Market is"],
                "philosophical": ["This is the", "The best time", "Remember:"],
                "reactive": ["Ser,", "GM", "Based", "King energy"],
                "questioning": ["Is it just me or", "Thoughts on", "Anyone else"]
            },
            "structures": {
                "insight_link": "{insight}\n\n{link}",
                "question_answer": "{question}\n\n{answer}",
                "statement_emphasis": "{statement}.\n\n{emphasis}",
                "multi_point": "{point1}\n\n{point2}\n\n{conclusion}"
            },
            "closings": {
                "bullish": ["LFG", "Up only", "WAGMI", "🚀"],
                "bearish": ["NGMI", "Down bad", "Rekt incoming"],
                "neutral": ["DYOR", "NFA", "Time will tell"],
                "engaging": ["Thoughts?", "Am I wrong?", "Let me know"]
            },
            "vocabulary": {
                "crypto_slang": ["ser", "gm", "ngmi", "wagmi", "degen", "ape"],
                "market_terms": ["liquidity", "resistance", "support", "breakout"],
                "emphasis": ["absolutely", "literally", "actually", "definitely"]
            }
        }
    
    def create_twitter_specific_dataset(self, original_data: List[Dict]) -> List[Dict]:
        """
        Transform dataset specifically for Twitter input→output training
        """
        twitter_dataset = []
        
        for item in original_data:
            # Extract the core tweet content (remove the prompt template)
            original_tweet = item['completion'].strip()
            
            # Create various input scenarios that might be typed into Twitter
            input_variations = self.generate_input_variations(original_tweet)
            
            for input_text in input_variations:
                twitter_dataset.append({
                    "input": input_text,
                    "output": original_tweet,
                    "metadata": {
                        "length": len(original_tweet),
                        "has_link": "https://t.co" in original_tweet,
                        "has_ticker": "$" in original_tweet,
                        "style": self.classify_tweet_style(original_tweet)
                    }
                })
        
        return twitter_dataset
    
    def generate_input_variations(self, tweet: str) -> List[str]:
        """
        Generate various ways someone might input text to get a Miles-style tweet
        """
        variations = []
        
        # Extract core topic
        topic = self.extract_topic(tweet)
        
        if "$" in tweet:  # Market-related
            variations.extend([
                f"thoughts on {topic}",
                f"what do you think about {topic}",
                f"{topic} analysis",
                f"tweet about {topic}",
                f"{topic}"  # Just the ticker/topic
            ])
        elif "?" in tweet:  # Question-based
            variations.extend([
                f"ask about {topic}",
                f"question about {topic}",
                f"wondering about {topic}",
                topic  # The core question
            ])
        else:  # General thoughts
            variations.extend([
                topic,
                f"tweet about {topic}",
                f"thoughts on {topic}",
                f"say something about {topic}"
            ])
        
        return variations[:3]  # Limit to 3 variations per tweet
    
    def extract_topic(self, tweet: str) -> str:
        """Extract the main topic from a tweet"""
        
        # Remove links
        tweet_clean = re.sub(r'https://\S+', '', tweet).strip()
        
        # Look for tickers
        tickers = re.findall(r'\$[A-Z]+', tweet_clean)
        if tickers:
            return tickers[0]
        
        # Look for key phrases
        if len(tweet_clean) < 50:
            return tweet_clean.lower()
        
        # Take first meaningful phrase
        sentences = tweet_clean.split('.')
        if sentences:
            return sentences[0][:30].lower().strip()
        
        return tweet_clean[:30].lower()
    
    def classify_tweet_style(self, tweet: str) -> str:
        """Classify tweet style for better training organization"""
        
        if any(term in tweet for term in ['$BTC', '$ETH', 'chart', 'market']):
            return "market_analysis"
        elif "?" in tweet:
            return "question"
        elif len(tweet) < 50:
            return "short_reaction"
        elif any(term in tweet.lower() for term in ['best time', 'worst time', 'remember']):
            return "philosophical"
        else:
            return "general"

class TwitterOptimizedTrainer:
    """
    Training system optimized for Twitter text-input → tweet-output
    """
    
    def __init__(self, model_name: str = "gpt2"):
        self.model_name = model_name
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        
        # Twitter-specific tokens
        self.add_twitter_tokens()
        
    def add_twitter_tokens(self):
        """Add Twitter-specific tokens to vocabulary"""
        
        special_tokens = {
            "additional_special_tokens": [
                "[TICKER]", "[LINK]", "[MENTION]", "[HASHTAG]",
                "[MARKET_UP]", "[MARKET_DOWN]", "[QUESTION]", "[STATEMENT]"
            ]
        }
        
        self.tokenizer.add_special_tokens(special_tokens)
        self.model.resize_token_embeddings(len(self.tokenizer))
    
    def prepare_training_data(self, dataset: List[Dict]) -> Dict:
        """
        Prepare data specifically for input→output training
        """
        
        inputs = []
        outputs = []
        
        for item in dataset:
            # Format: "Input: {user_text} Output: {miles_tweet}"
            text = f"Input: {item['input']} Output: {item['output']}{self.tokenizer.eos_token}"
            inputs.append(text)
            
            # Create label where input part is masked (-100)
            tokenized = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            labels = tokenized["input_ids"].clone()
            
            # Find where "Output:" starts and only train on that part
            output_start = text.find("Output:")
            if output_start != -1:
                input_tokens = self.tokenizer(text[:output_start], return_tensors="pt")["input_ids"]
                labels[0, :input_tokens.shape[1]] = -100
            
            outputs.append(labels)
        
        return {"texts": inputs, "labels": outputs}
    
    def create_training_args(self) -> TrainingArguments:
        """Twitter-optimized training arguments"""
        
        return TrainingArguments(
            output_dir="./miles-twitter-ai",
            num_train_epochs=5,  # More epochs for input→output mapping
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir="./logs",
            
            # Twitter-specific optimizations
            learning_rate=3e-5,  # Slightly higher for pattern learning
            
            # Save best model based on Twitter-specific metrics
            evaluation_strategy="steps",
            eval_steps=50,
            save_strategy="steps",
            save_steps=100,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            
            # Generation settings for Twitter
            predict_with_generate=True,
            generation_max_length=280,
            generation_num_beams=4,
        )

def create_twitter_inference_function(model_path: str):
    """
    Create the actual function that converts input text to Miles-style tweets
    """
    
    model = GPT2LMHeadModel.from_pretrained(model_path)
    tokenizer = GPT2Tokenizer.from_pretrained(model_path)
    
    def generate_miles_tweet(input_text: str, 
                           temperature: float = 0.8,
                           max_length: int = 280) -> str:
        """
        Convert any input text into a Miles Deutscher-style tweet
        
        Args:
            input_text: What the user types (e.g., "bitcoin price", "thoughts on ETH")
            temperature: Creativity level (0.7-0.9 recommended)
            max_length: Maximum tweet length
            
        Returns:
            Miles-style tweet ready for posting
        """
        
        # Format input
        prompt = f"Input: {input_text} Output:"
        
        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
        
        # Generate with Twitter-optimized settings
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                max_length=len(inputs["input_ids"][0]) + max_length,
                temperature=temperature,
                top_p=0.9,
                do_sample=True,
                num_return_sequences=3,  # Generate 3 options
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                
                # Twitter-specific constraints
                no_repeat_ngram_size=3,  # Avoid repetition
                repetition_penalty=1.2,
                length_penalty=0.8,  # Prefer concise tweets
            )
        
        # Extract generated tweets
        generated_tweets = []
        for output in outputs:
            # Decode and extract only the output part
            full_text = tokenizer.decode(output, skip_special_tokens=True)
            tweet = full_text.split("Output:")[-1].strip()
            
            # Ensure it's within Twitter limits
            if len(tweet) <= 280:
                generated_tweets.append(tweet)
        
        # Return best tweet (you could also return all 3 for user selection)
        return generated_tweets[0] if generated_tweets else ""
    
    return generate_miles_tweet

# MAIN EXECUTION
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║     Twitter-Specific Miles Deutscher AI System       ║
    ║                                                      ║
    ║  Input: Any text in Twitter compose box              ║
    ║  Output: Perfect Miles-style tweet                   ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    # Load original data
    with open('data.jsonl', 'r', encoding='utf-8') as f:
        original_data = [json.loads(line) for line in f]
    
    # Create Twitter-specific dataset
    twitter_ai = TwitterMilesAI()
    twitter_dataset = twitter_ai.create_twitter_specific_dataset(original_data)
    
    # Save Twitter-specific dataset
    with open('twitter_training_data.jsonl', 'w', encoding='utf-8') as f:
        for item in twitter_dataset:
            f.write(json.dumps(item) + '\n')
    
    print(f"\n✅ Created {len(twitter_dataset)} Twitter-specific training examples")
    
    # Example usage after training:
    print("\n📝 Example Input → Output mappings:")
    for i in range(min(5, len(twitter_dataset))):
        example = twitter_dataset[i]
        print(f"\nInput: '{example['input']}'")
        print(f"Output: '{example['output']}'")
        print(f"Style: {example['metadata']['style']}")