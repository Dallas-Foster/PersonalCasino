class Hand:
    def __init__(self, cards=None, bet=0):
        self.cards = cards if cards else []
        self.bet = bet
        self.is_active = True  # Whether the hand is still in play
        self.is_doubled = False  # Whether the hand has been doubled down

    def add_card(self, card):
        self.cards.append(card)

    def calculate_value(self):
        value = sum(card.value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == 'Ace')
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def has_blackjack(self):
        return len(self.cards) == 2 and self.calculate_value() == 21

    def is_busted(self):
        return self.calculate_value() > 21

    def can_split(self):
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank

    def __str__(self):
        hand_comp = ', '.join(str(card) for card in self.cards)
        return f"Hand: {hand_comp} (Value: {self.calculate_value()})"


class Player:
    def __init__(self, name, stack=1000):
        self.name = name
        self.stack = stack
        self.hands = []  # List of Hand instances
        self.current_hand_index = 0  # Index of the hand currently being played

    def place_bet(self, amount):
        if amount > self.stack:
            raise ValueError("Bet exceeds available stack.")
        self.hands = [Hand(bet=amount)]
        self.stack -= amount

    def add_hand(self, hand):
        self.hands.append(hand)

    def reset_hands(self):
        self.hands = [Hand()]  # Ensure at least one default hand
        self.current_hand_index = 0

    def current_hand(self):
        if self.current_hand_index < len(self.hands):
            return self.hands[self.current_hand_index]
        return None

    def move_to_next_hand(self):
        self.current_hand_index += 1

    def has_blackjack(self):
        return any(hand.has_blackjack() for hand in self.hands)

    def is_busted(self):
        return any(hand.is_busted() for hand in self.hands)

    def total_value(self):
        return sum(hand.calculate_value() for hand in self.hands)

    def __str__(self):
        hands_str = '\n'.join([f"Hand {i+1}: {hand}" for i, hand in enumerate(self.hands)])
        return f"{self.name}:\n{hands_str} (Stack: {self.stack})"
