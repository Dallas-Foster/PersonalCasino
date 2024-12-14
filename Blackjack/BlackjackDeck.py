import random
from BlackjackCards import Card

class Deck:
    def __init__(self, num_decks=1):
        self.num_decks = num_decks
        self.cards = []
        self.build()

    def build(self):
        self.cards = []
        for _ in range(self.num_decks):
            for suit in Card.SUITS:
                for rank in Card.RANKS:
                    self.cards.append(Card(suit, rank))
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        if len(self.cards) == 0:
            self.build()  # Rebuild and shuffle if out of cards
        return self.cards.pop()
