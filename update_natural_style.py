"""
Update test_miles_ai.py to generate more natural tweets without forced links
"""

# Configuration for more natural Miles style
natural_style_config = {
    "temperature": 0.85,  # Higher for more creativity
    "remove_forced_links": True,
    "link_probability": 0.3,  # Only 30% chance of links (when contextually appropriate)
    "style_weights": {
        "conversational": 1.3,  # Increase casual tone
        "philosophical": 1.2,   # More deep thoughts
        "technical": 0.8,       # Less forced technical
        "engagement": 1.1       # Natural questions
    }
}

# Natural templates without forced links
natural_templates = {
    "market_bullish": [
        "$TICKER absolutely sending it.\n\nClean break of resistance + volume = up only.",
        "Ser, $TICKER is about to melt faces.\n\nAccumulation done. Distribution next.\n\nYou know what comes after.",
        "$TICKER chart telling a beautiful story.\n\nHigher lows, higher highs.\n\nTrend is your friend until it ends.",
        "Real talk: $TICKER looking stupid bullish.\n\nNot even trying to be objective anymore.",
        "$TICKER pumping while everyone's distracted.\n\nClassic."
    ],
    
    "market_bearish": [
        "$TICKER showing major weakness.\n\nSupport gone. Buyers MIA.\n\nProtect your capital, anon.",
        "Warning: $TICKER about to get rekt.\n\nThat's not a dip, it's a cliff.",
        "$TICKER\n\nDown bad.\n\nThat's it. That's the tweet.",
        "If you're still bullish on $TICKER here...\n\nI admire your conviction but question your risk management.",
        "$TICKER breaking down.\n\nSometimes the best trade is no trade."
    ],
    
    "philosophical": [
        "This is the best time in history to ACTION.\n\nIt's also the worst time to OPPOSITE.\n\nThe paradox of opportunity.",
        "Everyone wants DESIRE.\n\nNobody wants to WORK.\n\nThe eternal struggle.",
        "The market rewards TRAIT.\n\nIt punishes OPPOSITE_TRAIT.\n\nSimple game, difficult to play.",
        "Success in crypto is 90% waiting and 10% acting.\n\nMost people get the ratio backwards.",
        "Your biggest enemy isn't the market.\n\nIt's your own psychology.\n\nMaster that first."
    ],
    
    "quick_reaction": [
        "INPUT\n\nBased.",
        "INPUT\n\nFew understand this.",
        "Unpopular opinion: INPUT\n\nBut I said what I said.",
        "INPUT\n\nIYKYK.",
        "INPUT\n\nNo further questions.",
        "GM to everyone who INPUT\n\nNGM to everyone else.",
        "INPUT\n\nThat's the alpha right there.",
        "Can't believe I have to explain this but INPUT"
    ],
    
    "question_response": [
        "QUESTION\n\nThe answer is always liquidity.",
        "QUESTION\n\nAnon, you already know the answer.",
        "QUESTION\n\nYes. Next question.",
        "QUESTION\n\nDepends on your time horizon.",
        "QUESTION\n\nIf you have to ask, you're not ready.",
        "QUESTION\n\nShort answer: Maybe.\nLong answer: Definitely maybe."
    ]
}

# More natural phrase replacements
natural_replacements = {
    "TECHNICAL_REASON": [
        "volume confirming", "momentum building", "buyers stepping in",
        "sellers exhausted", "accumulation complete", "distribution starting"
    ],
    "ACTION": [
        "build", "take risks", "be aggressive", "stay liquid",
        "compound gains", "cut losses", "follow momentum"
    ],
    "OPPOSITE": [
        "wait for perfect setups", "overthink every trade", "follow the herd",
        "ignore the charts", "fight the trend", "hold forever"
    ],
    "DESIRE": [
        "generational wealth", "financial freedom", "to time the top",
        "100x gains", "to buy the bottom", "passive income"
    ],
    "WORK": [
        "do the research", "manage risk", "stay disciplined",
        "learn from losses", "control emotions", "stick to the plan"
    ],
    "TRAIT": [
        "patience", "discipline", "conviction", "flexibility",
        "emotional control", "risk management"
    ],
    "OPPOSITE_TRAIT": [
        "greed", "fear", "impatience", "stubbornness",
        "emotional trading", "overleveraging"
    ]
}

print("Natural style configuration created!")
print("\nKey changes:")
print("- Removed forced link additions")
print("- More conversational tone")
print("- Natural vocabulary and phrasing")
print("- Authentic Miles voice patterns")
print("- Links only when contextually appropriate")

# Example usage
print("\n\nExample natural outputs:")
print("-" * 50)

examples = [
    "Real talk: $BTC looking stupid bullish.\n\nNot even trying to be objective anymore.",
    "Your biggest enemy isn't the market.\n\nIt's your own psychology.\n\nMaster that first.",
    "Unpopular opinion: We need the flush before the pump.\n\nBut I said what I said.",
    "Anon, your alt bags are heavy because you bought the narrative, not the chart.\n\nHappens to the best of us."
]

for ex in examples:
    print(f"\n{ex}")
    print(f"({len(ex)} chars)")