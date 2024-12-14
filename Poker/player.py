# player.py
class Player:
    def __init__(self, name, is_human=False):
        self.name = name
        self.is_human = is_human
        self.stack = 0
        self.hole_cards = []
        self.has_folded = False
        self.current_bet = 0  # Amount currently invested in the pot this round

    def reset_for_new_hand(self):
        self.hole_cards = []
        self.has_folded = False
        self.current_bet = 0

    def bet(self, amount):
        actual_bet = min(amount, self.stack)
        self.stack -= actual_bet
        self.current_bet += actual_bet
        return actual_bet

    def fold(self):
        self.has_folded = True

    def is_active(self):
        return not self.has_folded and self.stack > 0
