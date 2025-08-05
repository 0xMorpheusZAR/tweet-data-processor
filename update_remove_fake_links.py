"""
Update all files to remove fake/placeholder links
Only include links when contextually appropriate
"""

import os
import re

def remove_fake_links_from_file(filepath):
    """Remove fake Twitter links from a file"""
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match fake Twitter links
    fake_link_pattern = r'https://t\.co/[a-zA-Z0-9]{10,11}'
    
    # Remove fake links
    original_content = content
    content = re.sub(fake_link_pattern, '', content)
    
    # Clean up extra spaces and newlines left after link removal
    content = re.sub(r'\s+\n', '\n', content)
    content = re.sub(r'\n\n\n+', '\n\n', content)
    content = re.sub(r'\s+$', '', content, flags=re.MULTILINE)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

# Files to update
files_to_update = [
    'test_miles_ai.py',
    'local_server.py',
    'miles_natural_style.py',
    'twitter_api_integration.py',
    'enhanced_twitter_client.py',
    'test_and_host.py',
    'twitter_api_v2_complete.py'
]

print("Removing fake links from all files...")
print("=" * 60)

updated_count = 0
for filename in files_to_update:
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if remove_fake_links_from_file(filepath):
        print(f"✅ Updated: {filename}")
        updated_count += 1
    else:
        print(f"⏭️  No changes needed: {filename}")

print("=" * 60)
print(f"Updated {updated_count} files")

# Create new template without links
print("\nCreating new link-free templates...")

new_templates = '''
# Natural templates without forced links

market_bullish = [
    "$TICKER absolutely sending it.\\n\\nClean break of resistance + volume = up only.",
    "Ser, $TICKER is about to melt faces.\\n\\nAccumulation done. Distribution next.\\n\\nYou know what comes after.",
    "$TICKER chart telling a beautiful story.\\n\\nHigher lows, higher highs.\\n\\nTrend is your friend until it ends.",
    "Real talk: $TICKER looking stupid bullish.\\n\\nNot even trying to be objective anymore.",
    "$TICKER pumping while everyone's distracted.\\n\\nClassic."
]

market_bearish = [
    "$TICKER showing major weakness.\\n\\nSupport gone. Buyers MIA.\\n\\nProtect your capital, anon.",
    "Warning: $TICKER about to get rekt.\\n\\nThat's not a dip, it's a cliff.",
    "$TICKER\\n\\nDown bad.\\n\\nThat's it. That's the tweet.",
    "If you're still bullish on $TICKER here...\\n\\nI admire your conviction but question your risk management.",
    "$TICKER breaking down.\\n\\nSometimes the best trade is no trade."
]

philosophical = [
    "This is the best time in history to ACTION.\\n\\nIt's also the worst time to OPPOSITE.\\n\\nThe paradox of opportunity.",
    "Everyone wants DESIRE.\\n\\nNobody wants to WORK.\\n\\nThe eternal struggle.",
    "The market rewards TRAIT.\\n\\nIt punishes OPPOSITE_TRAIT.\\n\\nSimple game, difficult to play.",
    "Success in crypto is 90% waiting and 10% acting.\\n\\nMost people get the ratio backwards.",
    "Your biggest enemy isn't the market.\\n\\nIt's your own psychology.\\n\\nMaster that first."
]

general = [
    "INPUT\\n\\nBased.",
    "INPUT\\n\\nFew understand this.",
    "Unpopular opinion: INPUT\\n\\nBut I said what I said.",
    "INPUT\\n\\nIYKYK.",
    "INPUT\\n\\nNo further questions.",
    "GM to everyone who INPUT\\n\\nNGM to everyone else.",
    "INPUT\\n\\nThat's the alpha right there.",
    "Can't believe I have to explain this but INPUT"
]
'''

print(new_templates)
print("\n✅ Update complete! No more fake links in generated tweets.")