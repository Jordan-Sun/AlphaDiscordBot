from typing import OrderedDict, Tuple
import random

FIVE_STAR_GEM_NAMES = ['Blessing of the Worthy', 'Blood-Soaked Jade', 'Bottled Hope', 'Chip of Stone Flesh', 'Echoing Shade', 'Howler\'s Call', 'Phoenix Ashes', 'Seeping Bile', 'Zwenson\'s Haunting']
TWO_STAR_GEM_NAMES = ['Battleguard', 'Bloody Reach', 'Cutthroat\'s Grin', 'Follower\'s Burden', 'Lightning Core', 'Power & Command', 'The Hunger', 'Unity Crystal']
ONE_STAR_GEM_NAMES = ['Berserker\'s Eye', 'The Black Rose', 'Ca\'arsen\'s Invigoration', 'Chained Death', 'Defiant Soul', 'Everlasting Torment', 'Freedom and Devotion', 'Mocking Laughter', 'Nightmare Wreath', 'Pain of Subjugation', 'Respite Stone', 'Seled\'s Weakening', 'Trickshot Gem', 'Zod Stone']
PITY_TIME = 50

# Helper method to get a random gem quality for 5 star gems.
def __quality() -> str:
    roll = random.randint(1, 100)
    if roll <= 1:
        return '★★★★★'
    elif roll <= 5:
        return '★★★★☆'
    elif roll <= 25:
        return '★★★☆☆'
    else:
        return '★★☆☆☆'

# Helper method to get a random 5 star legendary gem.
def __pity_gem() -> Tuple[str, str]:
    return (random.choice(FIVE_STAR_GEM_NAMES), __quality())

# Helper method to get a random legendary gem.
def __legendary_gem() -> Tuple[str, str]:
    roll = random.randint(1, 100)
    if roll <= 5:
        return (random.choice(FIVE_STAR_GEM_NAMES), __quality())
    elif roll <= 25:
        return (random.choice(TWO_STAR_GEM_NAMES), '★★')
    else:
        return (random.choice(ONE_STAR_GEM_NAMES), '★')

# Get random gems.
def gems(amount: int = 1) -> str:
    # Warn if the amount is less than 1.
    if amount <= 0:
        return 'No gems with no crests.'
    
    # Result collection.
    results = {}
    # Pity timer.
    pity_timer = 0
    pity_count = 0
    # Loop through the amount of gems requested.
    for i in range(amount):
        # Get a random gem.
        result = __legendary_gem()
        # Check gem stars
        if len(result[1]) == 5:
            # Reset the pity timer.
            pity_timer = 0
        else:
            # Increase the pity timer.
            pity_timer += 1
        # Pity system
        if pity_timer == PITY_TIME:
            # Get a five star gem instead.
            result = __pity_gem()
            # Reset the pity timer.
            pity_timer = 0
            pity_count += 1
        # Check if the result is already in the results.
        if result in results:
            # If it is, add one to the count.
            results[result] += 1
        else:
            # If it isn't, add it to the results.
            results[result] = 1

    # Sort the results.
    results = OrderedDict(sorted(results.items(), key=lambda x: (x[0][1].count('★'), x[0][1].count('☆'), x[0][0])))
    
    # Interpolate the results.
    message = 'Legendary gem summary:\n'
    for result in results:
        message += '[' + result[0] + ' ' + result[1] + '] x ' + str(results[result]) + '\n'
    if pity_count > 0:
        message += 'Triggered the pity system ' + str(pity_count) + ' times.'

    # Return the results.
    return message