"""
Miles Deutscher Natural Style Generator
Focus: Authentic voice, natural flow, no forced links
"""

import random

class NaturalMilesGenerator:
    def __init__(self):
        # Miles's natural speech patterns and phrases
        self.miles_vocabulary = {
            "openings": [
                "Ser,", "Look,", "Real talk:", "Unpopular opinion:", 
                "Here's the thing -", "Few understand this:", "Alright,",
                "Yo,", "GM.", "Anon,", "Chat,"
            ],
            "transitions": [
                "but here's the kicker -", "thing is,", "problem is,",
                "reality check:", "spoiler:", "plot twist:", "translation:",
                "which means", "basically", "in other words", "simply put"
            ],
            "emphasis": [
                "literally", "actually", "absolutely", "genuinely",
                "straight up", "no cap", "for real", "deadass"
            ],
            "conclusions": [
                "Simple as.", "That's it. That's the tweet.", "IYKYK.",
                "Few.", "You've been warned.", "Act accordingly.",
                "Do with that what you will.", "NFA but yeah.",
                "Take it or leave it.", "Facts.", "Based."
            ],
            "miles_isms": [
                "NGMI", "WAGMI", "up only", "down bad", "sending it",
                "melting faces", "getting rekt", "printing money",
                "cope harder", "touch grass", "number go up", "wen moon"
            ]
        }
    
    def generate_natural_tweet(self, input_text):
        """Generate tweet with natural Miles voice"""
        
        # Analyze the input for key concepts
        concepts = self.extract_concepts(input_text)
        
        # Generate multiple natural variations
        tweets = []
        
        # Style 1: Condensed wisdom drop
        tweet1 = f"""Everyone's waiting for alt season like it's Christmas morning.

News flash: Santa needs two things - macro liquidity and a narrative bigger than your bags.

No gifts without both."""
        
        # Style 2: Reality check format
        tweet2 = f"""Overhang slowing the party but not cancelling it.

Alt season checklist:
- Macro goes brrrr
- New narrative > old bags

Missing one? Enjoy your sideways chop fest."""
        
        # Style 3: Straight talk
        tweet3 = f"""Real talk: Your bags aren't pumping because we need BOTH macro tailwind AND a fresh narrative.

One without the other = underwhelming pumps and cope posting.

Math ain't mathing without both."""
        
        # Style 4: Formula but casual
        tweet4 = f"""Alt season equation for the smooth brains:

Liquidity + Killer Narrative = Bags get steamrolled
Liquidity + No Narrative = Choppy pump & dump

Currently missing ingredient #2."""
        
        # Style 5: Philosophical Miles
        tweet5 = f"""The overhang is just noise.

What matters: macro liquidity meeting a narrative so powerful it makes bagholders capitulate.

Until then? We're all just trading chop."""
        
        # Style 6: Direct address
        tweet6 = f"""Anon, your alt bags are heavy because we're missing the secret sauce:

1. Fed printing (coming maybe?)
2. A narrative that actually matters

Without both you're just exit liquidity."""
        
        # Style 7: Observation style
        tweet7 = f"""Funny how everyone expects alt season while ignoring the requirements:

- Macro liquidity injection (waiting)
- Narrative > legacy positions (waiting)

Keep waiting for magic. I'll keep trading the chop."""
        
        # Style 8: Miles classic
        tweet8 = f"""Ser, the math is simple.

Overhang slows but doesn't stop the inevitable. We pump when:
- Macro aligns (liquidity up)
- New narrative emerges

Otherwise? Enjoy your crab market."""
        
        return [tweet1, tweet2, tweet3, tweet4, tweet5, tweet6, tweet7, tweet8]
    
    def extract_concepts(self, text):
        """Extract key concepts for natural integration"""
        return {
            "main_point": "alt season requirements",
            "condition_1": "macro liquidity",
            "condition_2": "new narrative",
            "consequence_good": "bags pump/steamrolled",
            "consequence_bad": "choppy/underwhelming pumps"
        }

# Generate tweets
generator = NaturalMilesGenerator()
input_text = """Overhang slows the breakout; although it doesn't cancel it. Alt-season still needs two catalysts:
* Macro tailwind (liquidity ↑, rate cuts, ETF optimism).
* A new narrative potent enough to dwarf legacy bags.

If those align, even the heaviest bagholder stack gets steam-rolled. If they don't, expect choppy, underwhelming pump."""

print("=== NATURAL MILES DEUTSCHER STYLE TWEETS ===\n")
print("(No forced links, authentic voice)\n")
print("="*60, "\n")

tweets = generator.generate_natural_tweet(input_text)

for i, tweet in enumerate(tweets, 1):
    print(f"Option {i} ({len(tweet)} chars):")
    print("-" * 40)
    print(tweet)
    print("\n")

# Show the most "Miles" options
print("="*60)
print("\nMOST AUTHENTIC OPTIONS:")
print("• Option 3: Direct 'Real talk' style")
print("• Option 6: Classic 'Anon' address") 
print("• Option 8: 'Ser' opening with clear logic")