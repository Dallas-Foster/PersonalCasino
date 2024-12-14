# deck.py
import random

SUITS = ['♥', '♦', '♣', '♠']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']


class Deck:
    def __init__(self):
        self.cards = [r + s[0] for s in SUITS for r in RANKS]
        # Alternative format: ('2 of Hearts', '2H') etc.
        # We'll use short form like 'AH' for Ace of Hearts.

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num=1):
        dealt = self.cards[:num]
        self.cards = self.cards[num:]
        return dealt
