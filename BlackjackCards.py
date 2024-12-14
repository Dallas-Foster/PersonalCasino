class Card:
    SUITS = ('Hearts', 'Diamonds', 'Clubs', 'Spades')
    SUIT_SYMBOLS = {
        'Hearts': '♥',
        'Diamonds': '♦',
        'Clubs': '♣',
        'Spades': '♠'
    }
    RANKS = (
        '2', '3', '4', '5', '6', '7', '8', '9', '10',
        'Jack', 'Queen', 'King', 'Ace'
    )
    VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
        '8': 8, '9': 9, '10': 10,
        'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
    }

    def __init__(self, suit, rank):
        if suit not in Card.SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        if rank not in Card.RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        self.suit = suit
        self.rank = rank
        self.value = Card.VALUES[rank]

    def __str__(self):
        suit_symbol = Card.SUIT_SYMBOLS.get(self.suit, self.suit)
        return f"{self.rank} {suit_symbol}"
