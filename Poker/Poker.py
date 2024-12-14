import random
from itertools import combinations

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']
RANK_VALUES = {r: i for i, r in enumerate(RANKS)}

def create_deck():
    return [(r, s) for r in RANKS for s in SUITS]

def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

def card_str(card):
    return card[0] + card[1]

class Player:
    def __init__(self, name, stack=1000, is_human=False):
        self.name = name
        self.stack = stack
        self.hole_cards = []
        self.active = True
        self.has_folded = False
        self.current_bet = 0
        self.is_human = is_human

    def reset_for_new_hand(self):
        self.hole_cards = []
        self.active = True
        self.has_folded = False
        self.current_bet = 0

    def bet(self, amount):
        actual_bet = min(amount, self.stack)
        self.stack -= actual_bet
        self.current_bet += actual_bet
        return actual_bet

    def fold(self):
        self.active = False
        self.has_folded = True

    def __str__(self):
        return f"{self.name} (stack={self.stack}, cards={self.hole_cards}, active={self.active})"

class PokerGame:
    def __init__(self, num_players=4):
        assert 2 <= num_players <= 5, "Number of players must be between 2 and 5."
        # Player1 is human
        self.players = [Player(f"Player{i+1}", is_human=(i==0)) for i in range(num_players)]
        self.deck = []
        self.pot = 0
        self.community_cards = []
        self.dealer_position = 0
        self.small_blind = 5
        self.big_blind = 10

    def reset_deck_and_hands(self):
        self.deck = create_deck()
        shuffle_deck(self.deck)
        for p in self.players:
            p.reset_for_new_hand()
        self.community_cards = []
        self.pot = 0

    def deal_hole_cards(self):
        for _ in range(2):
            for p in self.players:
                p.hole_cards.append(self.deck.pop())

    def post_blinds(self):
        sb_index = (self.dealer_position + 1) % len(self.players)
        bb_index = (self.dealer_position + 2) % len(self.players)
        sb_amount = self.players[sb_index].bet(self.small_blind)
        bb_amount = self.players[bb_index].bet(self.big_blind)
        self.pot += sb_amount + bb_amount

    def betting_round(self, round_name):
        # Determine start index
        if round_name == "preflop":
            # action starts left of big blind
            start_index = (self.dealer_position + 3) % len(self.players)
        else:
            # postflop start is dealer+1
            start_index = (self.dealer_position + 1) % len(self.players)

        highest_bet = max((p.current_bet for p in self.players if p.active), default=0)
        players_in_hand = [p for p in self.players if p.active and not p.has_folded]

        # If highest_bet == 0, everyone must act to give a chance to bet/check/fold
        # If highest_bet > 0, all players who haven't matched must act
        if highest_bet == 0:
            players_to_act = set(players_in_hand)
        else:
            players_to_act = {p for p in players_in_hand if p.current_bet < highest_bet}

        acting_index = start_index

        while True:
            # Check if single player left mid-round
            if self.resolve_if_single_player_left_internal():
                # One player remains, round and hand end
                self.reset_player_bets()  # reset bets for next hand
                return

            if not players_to_act:
                # No player needs to act, betting round ends
                break

            current_player = self.players[acting_index]

            if current_player.active and not current_player.has_folded and current_player in players_to_act:
                required_call = highest_bet - current_player.current_bet
                action = self.get_action(current_player, highest_bet, required_call)

                if action[0] == "fold":
                    current_player.fold()
                    if current_player in players_to_act:
                        players_to_act.remove(current_player)
                    players_in_hand = [p for p in players_in_hand if p != current_player]

                elif action[0] == "call":
                    call_amount = highest_bet - current_player.current_bet
                    self.pot += current_player.bet(call_amount)
                    if current_player in players_to_act:
                        players_to_act.remove(current_player)

                elif action[0] == "check":
                    # Only possible if required_call == 0
                    if current_player in players_to_act:
                        players_to_act.remove(current_player)

                elif action[0] == "bet":
                    # bet sets a new highest bet if was 0 before
                    bet_amount = action[1]
                    self.pot += current_player.bet(bet_amount)
                    highest_bet = current_player.current_bet
                    # Everyone except current player must now act again
                    players_to_act = {p for p in players_in_hand if p != current_player}

                elif action[0] == "raise":
                    raise_to = action[1]
                    raise_amount = raise_to - current_player.current_bet
                    self.pot += current_player.bet(raise_amount)
                    highest_bet = current_player.current_bet
                    # Everyone except raiser must act again
                    players_to_act = {p for p in players_in_hand if p != current_player}

            acting_index = (acting_index + 1) % len(self.players)

        # Betting round complete
        self.reset_player_bets()  # reset all player bets for the next round

    def reset_player_bets(self):
        # After a betting round completes, all bets go into the pot and are reset
        for p in self.players:
            p.current_bet = 0

    def get_action(self, player, highest_bet, required_call):
        if player.is_human:
            return self.human_action(player, required_call, highest_bet)
        else:
            return self.bot_action(player, highest_bet)

    def human_action(self, player, required_call, highest_bet):
        print(f"\nYour turn ({player.name}):")
        print(f"Your cards: {', '.join(card_str(c) for c in player.hole_cards)}")
        print(f"Community cards: {', '.join(card_str(c) for c in self.community_cards)}")
        print(f"Pot: {self.pot}, Your stack: {player.stack}, Call needed: {required_call}")

        while True:
            if required_call > 0:
                move = input("Enter your action (fold/call/raise): ").strip().lower()
                if move == "fold":
                    return ("fold", None)
                elif move == "call":
                    return ("call", None)
                elif move == "raise":
                    try:
                        amt = int(input("Enter raise-to amount: "))
                        if amt > highest_bet and amt <= player.current_bet + player.stack:
                            return ("raise", amt)
                        else:
                            print("Invalid raise amount. Must exceed current bet and not exceed your stack.")
                    except ValueError:
                        print("Please enter a valid number.")
                else:
                    print("Invalid action. Possible: fold, call, raise.")
            else:
                # No required call
                move = input("Enter your action (check/bet/fold): ").strip().lower()
                if move == "fold":
                    return ("fold", None)
                elif move == "check":
                    return ("check", None)
                elif move == "bet":
                    try:
                        amt = int(input("Enter bet amount: "))
                        if amt > 0 and amt <= player.stack:
                            return ("bet", amt)
                        else:
                            print("Invalid bet amount. Must be >0 and <= your stack.")
                    except ValueError:
                        print("Please enter a valid number.")
                else:
                    print("Invalid action. Possible: check, bet, fold.")

    def bot_action(self, player, highest_bet):
        required_call = highest_bet - player.current_bet
        equity = self.estimate_equity(player.hole_cards, self.community_cards,
                                      [p for p in self.players if p is not player and p.active and not p.has_folded])

        if required_call > 0:
            # must fold/call/raise
            pot_odds = required_call / (self.pot + required_call)
            if equity > pot_odds:
                # call or raise if strong
                if equity > 0.7 and player.stack > required_call + 20:
                    raise_amount = highest_bet + max(20, int(equity*100))
                    return ("raise", raise_amount)
                else:
                    return ("call", None)
            else:
                return ("fold", None)
        else:
            # no required call: can check/bet/fold
            if equity > 0.55 and player.stack > 20:
                bet_amount = max(20, int(equity*50))
                return ("bet", bet_amount)
            else:
                return ("check", None)

    def deal_community_cards(self, count):
        for _ in range(count):
            self.community_cards.append(self.deck.pop())

    def estimate_equity(self, hole_cards, community_cards, opponents):
        if not opponents:
            return 1.0

        used_cards = hole_cards + community_cards
        deck = create_deck()
        remaining_deck = [c for c in deck if c not in used_cards]

        simulations = 200
        wins = 0
        ties = 0

        for _ in range(simulations):
            trial_deck = remaining_deck[:]
            random.shuffle(trial_deck)
            opponent_cards = []
            for opp in opponents:
                if len(trial_deck) < 2:
                    break
                opp_cards = [trial_deck.pop(), trial_deck.pop()]
                opponent_cards.append(opp_cards)

            full_board = self.complete_board(community_cards, trial_deck)
            my_score = self.best_hand_score(hole_cards, full_board)

            opp_scores = [self.best_hand_score(oc, full_board) for oc in opponent_cards]

            if not opp_scores:
                wins += 1
                continue

            max_opp = max(opp_scores)
            if my_score > max_opp:
                wins += 1
            elif my_score == max_opp:
                ties += 1

        equity = (wins + ties/2) / simulations
        return equity

    def complete_board(self, community_cards, deck):
        full_board = community_cards[:]
        while len(full_board) < 5 and deck:
            full_board.append(deck.pop())
        return full_board

    def best_hand_score(self, hole_cards, board_cards):
        all_cards = hole_cards + board_cards
        best_score = 0
        for combo in combinations(all_cards, 5):
            score = self.hand_rank(combo)
            if score > best_score:
                best_score = score
        return best_score

    def hand_rank(self, five_cards):
        ranks = sorted([RANK_VALUES[c[0]] for c in five_cards], reverse=True)
        suits = [c[1] for c in five_cards]
        is_flush = len(set(suits)) == 1
        sorted_r = sorted(ranks)
        is_straight = False
        high_straight_card = sorted_r[-1]
        if all(sorted_r[i] - sorted_r[i+1] == 1 for i in range(4)):
            is_straight = True
            high_straight_card = sorted_r[0]
        # A2345 straight special case
        if set(ranks) == {12, 0, 1, 2, 3}:
            is_straight = True
            high_straight_card = 3

        from collections import Counter
        count_ranks = Counter(ranks)
        counts = sorted(count_ranks.values(), reverse=True)

        if is_straight and is_flush:
            return 8_000_000_000 + high_straight_card
        if 4 in counts:
            four_card = [r for r,cnt in count_ranks.items() if cnt == 4][0]
            kicker = [r for r,cnt in count_ranks.items() if cnt == 1][0]
            return 7_000_000_000 + four_card * 100 + kicker
        if 3 in counts and 2 in counts:
            three_card = [r for r,cnt in count_ranks.items() if cnt == 3][0]
            pair_card = [r for r,cnt in count_ranks.items() if cnt == 2][0]
            return 6_000_000_000 + three_card * 100 + pair_card
        if is_flush:
            sorted_desc = sorted(ranks, reverse=True)
            val = 0
            for r in sorted_desc:
                val = val*100 + r
            return 5_000_000_000 + val
        if is_straight:
            return 4_000_000_000 + high_straight_card
        if 3 in counts:
            three_card = [r for r,cnt in count_ranks.items() if cnt == 3][0]
            kickers = sorted([r for r,cnt in count_ranks.items() if cnt == 1], reverse=True)
            val = three_card * 10000 + kickers[0]*100 + kickers[1]
            return 3_000_000_000 + val
        if counts == [2,2,1]:
            pairs = sorted([r for r,cnt in count_ranks.items() if cnt == 2], reverse=True)
            kicker = [r for r,cnt in count_ranks.items() if cnt == 1][0]
            val = pairs[0]*10000 + pairs[1]*100 + kicker
            return 2_000_000_000 + val
        if 2 in counts:
            pair_card = [r for r,cnt in count_ranks.items() if cnt == 2][0]
            kickers = sorted([r for r,cnt in count_ranks.items() if cnt == 1], reverse=True)
            val = pair_card * 1000000
            for k in kickers:
                val = val*100 + k
            return 1_000_000_000 + val

        sorted_desc = sorted(ranks, reverse=True)
        val = 0
        for r in sorted_desc:
            val = val*100 + r
        return val

    def showdown(self):
        active_players = [p for p in self.players if p.active and not p.has_folded]
        if not active_players:
            return

        best_player = None
        best_score = -1
        print("\nShowdown:")
        for p in active_players:
            print(f"{p.name}'s cards: {', '.join(card_str(c) for c in p.hole_cards)}")

        for p in active_players:
            score = self.best_hand_score(p.hole_cards, self.community_cards)
            if score > best_score:
                best_score = score
                best_player = p

        print(f"{best_player.name} wins the pot of {self.pot}!")
        best_player.stack += self.pot
        self.pot = 0

    def resolve_if_single_player_left_internal(self):
        active_players = [p for p in self.players if p.active and not p.has_folded]
        if len(active_players) == 1:
            winner = active_players[0]
            print(f"All other players folded. {winner.name} wins the pot of {self.pot}.")
            winner.stack += self.pot
            self.pot = 0
            return True
        return False

    def resolve_if_single_player_left(self):
        active_players = [p for p in self.players if p.active and not p.has_folded]
        return len(active_players) == 1

    def play_hand(self):
        self.reset_deck_and_hands()
        self.deal_hole_cards()
        self.post_blinds()

        print("\n--- Preflop ---")
        self.betting_round("preflop")
        if self.resolve_if_single_player_left():
            return

        # Flop
        self.deal_community_cards(3)
        print("\n--- Flop ---")
        print("Community cards:", ', '.join(card_str(c) for c in self.community_cards))
        self.betting_round("flop")
        if self.resolve_if_single_player_left():
            return

        # Turn
        self.deal_community_cards(1)
        print("\n--- Turn ---")
        print("Community cards:", ', '.join(card_str(c) for c in self.community_cards))
        self.betting_round("turn")
        if self.resolve_if_single_player_left():
            return

        # River
        self.deal_community_cards(1)
        print("\n--- River ---")
        print("Community cards:", ', '.join(card_str(c) for c in self.community_cards))
        self.betting_round("river")
        if self.resolve_if_single_player_left():
            return

        self.showdown()

    def next_dealer(self):
        self.dealer_position = (self.dealer_position + 1) % len(self.players)


if __name__ == "__main__":
    game = PokerGame(num_players=4)
    num_hands = 3
    for _ in range(num_hands):
        print("-" * 40)
        print(f"Starting a new hand. Dealer: {game.players[game.dealer_position].name}")
        game.play_hand()
        print("Stacks after hand:")
        for p in game.players:
            print(f"{p.name}: {p.stack}")
        game.next_dealer()

    print("\nFinal stacks:")
    for p in game.players:
        print(p.name, p.stack)
