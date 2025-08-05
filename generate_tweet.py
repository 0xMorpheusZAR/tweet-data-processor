"""Generate Miles-style tweet from complex input"""

input_text = """Overhang slows the breakout; although it doesn't cancel it. Alt-season still needs two catalysts:
* Macro tailwind (liquidity ↑, rate cuts, ETF optimism).
* A new narrative potent enough to dwarf legacy bags.

If those align, even the heaviest bagholder stack gets steam-rolled. If they don't, expect choppy, underwhelming pump."""

print("=== MILES DEUTSCHER TWEET OPTIONS ===\n")
print("Original input:", len(input_text), "characters")
print("="*60, "\n")

# Tweet options in Miles's style
options = [
    # Option 1: Condensed insight
    """Alt-season needs two things:

1. Macro tailwind (liquidity injection)
2. New narrative > legacy bags

Without both? Choppy pumps ahead. https://t.co/xY9kL3mN2p""",

    # Option 2: Key insight focus
    """Overhang slows but doesn't cancel the breakout.

Real alt-season requires macro liquidity + a narrative strong enough to steamroll bagholders.

Missing either = underwhelming pumps. https://t.co/aB4cD5eF6g""",

    # Option 3: Formula style
    """Alt-season math is simple:

Liquidity + New Narrative > Legacy Bags = Moon
Liquidity + No Narrative = Choppy pump

Plan accordingly. https://t.co/hJ7kM8nP9q""",

    # Option 4: Chart-first
    """https://t.co/zX2vC4bN5m

Overhang creating resistance but breakout intact.

Alt-season catalyst checklist:
- Macro liquidity
- Narrative > bagholders

Both required or expect chop.""",

    # Option 5: Direct take
    """Everyone waiting for alt-season.

It needs:
- Macro liquidity (rate cuts, ETF hype)
- Narrative that dwarfs old bags

Without both? Just choppy pumps.

Position accordingly. https://t.co/kL9jH6tY4u"""
]

# Display all options
for i, tweet in enumerate(options, 1):
    print(f"Option {i} ({len(tweet)} chars):")
    print("-" * 40)
    print(tweet)
    print("\n")

# Recommendation
print("="*60)
print("\nRECOMMENDED: Option 3")
print("Why: Clear formula format that Miles often uses, concise, memorable, actionable")