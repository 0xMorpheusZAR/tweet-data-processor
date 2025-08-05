"""Run the original tweet processor for Miles Deutscher AI"""
from process_tweets import process_tweets
import random

# Set random seed for reproducibility
random.seed(42)

# Run with Miles Deutscher AI identifier
print("Processing tweets with identifier: Miles Deutscher AI")
process_tweets("Miles Deutscher AI")
print("\nDataset created successfully as data.jsonl")