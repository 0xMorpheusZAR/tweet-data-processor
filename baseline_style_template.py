"""
Miles Deutscher Baseline Style Template
Based on Option 5 - The preferred natural voice
"""

# BASELINE TEMPLATE (Option 5 structure)
"""
The overhang is just noise.

What matters: macro liquidity meeting a narrative so powerful it makes bagholders capitulate.

Until then? We're all just trading chop.
"""

# Key characteristics of this baseline:
baseline_structure = {
    "opening": {
        "style": "dismissive_observation",
        "examples": [
            "The [common concern] is just noise.",
            "The [obvious thing] doesn't matter.",
            "[Popular opinion] is missing the point.",
            "Everyone's focused on [X] when [Y] is what matters.",
            "[Surface issue] is a distraction."
        ]
    },
    
    "middle": {
        "style": "what_actually_matters",
        "format": "What matters: [core insight with specific conditions]",
        "examples": [
            "What matters: [condition A] meeting [condition B]",
            "What counts: [fundamental] aligning with [catalyst]",
            "The real game: [factor 1] plus [factor 2]",
            "Reality: [requirement] combined with [requirement]"
        ]
    },
    
    "closing": {
        "style": "current_state_assessment",
        "format": "Until then? [what we're doing now].",
        "examples": [
            "Until then? We're all just [current activity].",
            "For now? [resigned acceptance of reality].",
            "Meanwhile? [what smart money is doing].",
            "Translation? [simplified outcome].",
            "Bottom line? [current situation]."
        ]
    }
}

# Baseline voice characteristics
voice_profile = {
    "tone": "philosophical_realist",
    "perspective": "above_the_noise",
    "delivery": "casual_wisdom",
    "structure": "dismiss_refocus_conclude"
}

# Example applications of baseline
baseline_examples = [
    {
        "input": "Bitcoin dominance rising",
        "output": """BTC dominance charts are just noise.

What matters: alt liquidity returning when retail confidence meets a new narrative.

Until then? We're all just watching Bitcoin eat everyone's lunch."""
    },
    
    {
        "input": "NFT market dead",
        "output": """'NFTs are dead' is just noise.

What matters: digital ownership meeting actual utility beyond profile pictures.

Until then? We're all just trading jpegs to each other."""
    },
    
    {
        "input": "Fed rate decision",
        "output": """The Fed meeting is just theatre.

What matters: actual liquidity conditions meeting market positioning.

Until then? We're all just trading the rumor."""
    },
    
    {
        "input": "Layer 2 competition",
        "output": """The L2 wars are just noise.

What matters: actual adoption meeting sustainable fee models.

Until then? We're all just betting on VC narratives."""
    }
]

# Template function
def generate_baseline_style(topic, common_concern, what_matters, current_reality):
    """
    Generate tweet using Option 5 baseline structure
    
    Args:
        topic: Main subject
        common_concern: What everyone's worried about
        what_matters: The actual important factors
        current_reality: What we're doing while waiting
    """
    
    tweet = f"""{common_concern} is just noise.

What matters: {what_matters}.

Until then? We're all just {current_reality}."""
    
    return tweet

# Configuration for fine-tuning
baseline_config = {
    "template_weight": 0.7,  # How closely to follow this structure
    "variation_allowed": 0.3,  # Room for natural variation
    "key_elements": {
        "dismissive_opening": True,
        "what_matters_focus": True,
        "rhetorical_close": True
    },
    "word_choices": {
        "noise": ["noise", "distraction", "theatre", "cope", "hopium"],
        "matters": ["matters", "counts", "moves the needle", "actually matters"],
        "until_then": ["Until then?", "For now?", "Meanwhile?", "Reality?"]
    }
}

print("BASELINE STYLE TEMPLATE (Option 5)")
print("="*50)
print("\nStructure:")
print("1. Dismiss the obvious concern as 'noise'")
print("2. Refocus on what actually matters")
print("3. Conclude with current reality check")
print("\nThis creates Miles's philosophical yet practical voice")
print("\nExample:")
print("-"*50)
print(generate_baseline_style(
    "Alt season",
    "The overhang",
    "macro liquidity meeting a narrative so powerful it makes bagholders capitulate",
    "trading chop"
))