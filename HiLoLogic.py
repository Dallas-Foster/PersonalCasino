import random

def create_deck():
    """Create a standard deck of cards with values 1-10 and J, Q, K, A."""
    values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
    deck = values * 4  # Four of each card (standard deck)
    random.shuffle(deck)
    return deck

def get_card_value(card):
    """Convert card face values to numeric values for comparison."""
    if card in ['J', 'Q', 'K']:
        return 11  # All face cards have the same value
    elif card == 'A':
        return 14  # Ace has the highest value
    return card  # Numeric cards keep their values

