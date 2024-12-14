import sys
from deck import Deck
from constants import BIG_BLIND, SMALL_BLIND
from handevaluator import hand_rank


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

    def is_active(self):
        return self.active and not self.has_folded

    def __str__(self):
        return f"{self.name} (stack={self.stack}, cards={self.hole_cards}, active={self.active})"


class Game:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.dealer_button = 0
        self.current_bet = 0

    def still_playing(self):
        count = sum(1 for p in self.players if p.stack > 0)
        return count > 1

    def play_hand(self):
        print("=== NEW HAND ===")
        if self.game_over():
            print("Game over detected in play_hand.")
            return

        self.reset_hand()
        print("Hand reset. Pot initialized to:", self.pot)

        self.post_blinds()
        print(f"Blinds posted. Pot now: {self.pot}")

        self.deal_hole_cards()
        print(f"Hole cards dealt. Players: {[str(p) for p in self.players]}")

        print("=== PREFLOP ===")
        if not self.betting_round("Preflop"):
            print("Preflop betting ended prematurely.")
            self.handle_end_of_betting_round()
            self.finish_hand()
            return

        if self.all_in_scenario():
            print("All-in detected after preflop.")
            self.run_out_board_and_showdown()
            self.finish_hand()
            return

        self.deal_flop()
        print(f"Flop: {self.community_cards}")
        if not self.betting_round("Flop"):
            print("Flop betting ended prematurely.")
            self.handle_end_of_betting_round()
            self.finish_hand()
            return

        if self.all_in_scenario():
            print("All-in detected after flop.")
            self.run_out_board_and_showdown()
            self.finish_hand()
            return

        self.deal_turn()
        print(f"Turn: {self.community_cards}")
        if not self.betting_round("Turn"):
            print("Turn betting ended prematurely.")
            self.handle_end_of_betting_round()
            self.finish_hand()
            return

        if self.all_in_scenario():
            print("All-in detected after turn.")
            self.run_out_board_and_showdown()
            self.finish_hand()
            return

        self.deal_river()
        print(f"River: {self.community_cards}")
        if not self.betting_round("River"):
            print("River betting ended prematurely.")
            self.handle_end_of_betting_round()
            self.finish_hand()
            return

        print("Proceeding to normal showdown.")
        self.showdown()
        self.finish_hand()

    def handle_end_of_betting_round(self):
        active_players = [p for p in self.players if p.is_active()]

        if len(active_players) == 1:
            winner = active_players[0]
            winner.stack += self.pot
            print(f"{winner.name} wins the pot of {self.pot} chips uncontested!")
        elif self.all_in_scenario():
            print("All-in scenario detected in handle_end_of_betting_round.")
            self.run_out_board_and_showdown()
        else:
            self.showdown_if_needed()

    def reset_hand(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.community_cards = []
        self.pot = 0
        for p in self.players:
            p.reset_for_new_hand()
        self.current_bet = 0

    def post_blinds(self):
        small_blind_pos = (self.dealer_button + 1) % len(self.players)
        big_blind_pos = (self.dealer_button + 2) % len(self.players)
        sb_player = self.players[small_blind_pos]
        bb_player = self.players[big_blind_pos]

        sb_amount = sb_player.bet(BIG_BLIND // 2)
        bb_amount = bb_player.bet(BIG_BLIND)
        self.pot += sb_amount + bb_amount
        self.current_bet = BIG_BLIND

    def deal_hole_cards(self):
        for p in self.players:
            if p.stack > 0:
                p.hole_cards = self.deck.deal(2)

    def deal_flop(self):
        self.community_cards = self.deck.deal(3)

    def deal_turn(self):
        self.community_cards.append(self.deck.deal(1)[0])

    def deal_river(self):
        self.community_cards.append(self.deck.deal(1)[0])

    def betting_round(self, round_name):
        for p in self.players:
            p.current_bet = 0
        self.current_bet = 0
        return self.run_betting_loop(round_name)

    def run_betting_loop(self, round_name):
        print(f"=== Betting Round: {round_name} ===")
        active = [p for p in self.players if p.is_active()]
        print(f"Active players: {[str(p) for p in active]}")
        print(f"Pot: {self.pot}, Current bet: {self.current_bet}")

        if len(active) == 1:
            print("Only one player active. Ending betting round.")
            return False

        if round_name == "Preflop":
            start_index = (self.dealer_button + 3) % len(self.players)
        else:
            start_index = (self.dealer_button + 1) % len(self.players)

        highest_bet = 0
        acted = set()
        current_player_index = start_index

        while True:
            player = self.players[current_player_index]
            if player.is_active():
                print(f"Player {player.name}'s turn. Stack: {player.stack}, Current bet: {player.current_bet}")
                action, amount = self.get_player_action(player, highest_bet, round_name)
                print(f"Player {player.name} chose action: {action}, amount: {amount}")

                if action == 'fold':
                    player.fold()
                    if sum(pl.is_active() for pl in self.players) == 1:
                        return False
                elif action == 'call':
                    call_amount = max(0, highest_bet - player.current_bet)
                    bet = player.bet(call_amount)
                    self.pot += bet
                elif action == 'check':
                    pass
                elif action == 'bet':
                    bet_amt = min(amount, player.stack)
                    bet = player.bet(bet_amt)
                    self.pot += bet
                    highest_bet = player.current_bet
                    acted = {player}
                elif action == 'raise':
                    call_amount = max(0, highest_bet - player.current_bet)
                    total_raise = call_amount + amount
                    total_raise = min(total_raise, player.stack)
                    bet = player.bet(total_raise)
                    self.pot += bet
                    highest_bet = player.current_bet
                    acted = {player}

                if player.is_active():
                    acted.add(player)

                active_players = [p for p in self.players if p.is_active()]
                all_acted = (len(acted) == len(active_players))
                bets_matched = all(p.current_bet == highest_bet for p in active_players)

                if self.all_in_scenario():
                    print("All players are all-in. Proceeding to run out the board...")
                    self.run_out_board_and_showdown()
                    return False

                if all_acted and bets_matched:
                    print("Betting round complete. All bets matched.")
                    return True

            current_player_index = (current_player_index + 1) % len(self.players)

    def get_player_action(self, player, highest_bet, round_name):
        call_amount = max(0, highest_bet - player.current_bet)

        if player.is_human:
            print(f"Your hand: {player.hole_cards}, Community: {self.community_cards}")
            print(f"Pot: {self.pot}, Call: {call_amount}, Your stack: {player.stack}")
            while True:
                action = input("Action? (fold/check/call/bet/raise): ").strip().lower()
                if action in ['fold', 'check', 'call']:
                    if action == 'call':
                        if call_amount > player.stack:
                            print("You don't have enough chips to call. Going all-in with your remaining stack!")
                            return ('call', player.stack)
                        else:
                            return ('call', call_amount)
                    else:
                        return (action, 0)
                elif action in ['bet', 'raise']:
                    amount_str = input("Amount?: ")
                    try:
                        amt = int(amount_str)
                        if amt <= 0:
                            print("Amount must be greater than 0.")
                            continue
                        if amt > player.stack:
                            print("You don't have that many chips. Going all-in with your remaining stack!")
                            return (action, player.stack)
                        else:
                            if amt == player.stack:
                                print("You are going all-in!")
                            return (action, amt)
                    except ValueError:
                        print("Invalid amount. Please enter a number.")
                else:
                    print("Invalid action. Choose from fold/check/call/bet/raise.")
        else:
            if call_amount <= player.stack:
                return ('call', call_amount)
            else:
                return ('call', player.stack)

    def showdown_if_needed(self):
        active_players = [p for p in self.players if p.is_active()]
        if len(active_players) == 1:
            winner = active_players[0]
            winner.stack += self.pot
            print(f"{winner.name} wins the pot of {self.pot} chips uncontested!")
        else:
            self.showdown()

    def showdown(self):
        active_players = [p for p in self.players if p.is_active()]
        print("=== SHOWDOWN ===")
        for p in active_players:
            print(f"{p.name}'s cards: {p.hole_cards}")

        best_score = (-1,)
        winners = []
        for p in active_players:
            full_hand = p.hole_cards + self.community_cards
            score = hand_rank(full_hand)
            if score > best_score:
                best_score = score
                winners = [p]
            elif score == best_score:
                winners.append(p)

        split_pot = self.pot // len(winners)
        remainder = self.pot % len(winners)
        for w in winners:
            w.stack += split_pot
        if remainder > 0:
            winners[0].stack += remainder

        if len(winners) == 1:
            print(f"{winners[0].name} wins the pot of {self.pot} chips with the best hand!")
        else:
            wn = ", ".join([w.name for w in winners])
            print(f"Split pot of {self.pot} between {wn}!")

    def rotate_dealer(self):
        self.dealer_button = (self.dealer_button + 1) % len(self.players)

    def game_over(self):
        active = [p for p in self.players if p.stack > 0]
        if len(active) <= 1:
            if len(active) == 1:
                print(f"Game over! {active[0].name} is the winner with {active[0].stack} chips!")
            else:
                print("Game over! No players have chips left.")
            return True
        return False

    def all_in_scenario(self):
        active_players = [p for p in self.players if p.is_active()]
        if len(active_players) > 1:
            if all(p.current_bet >= self.current_bet and p.stack == 0 for p in active_players):
                return True
        return False

    def run_out_board_and_showdown(self):
        print("=== RUNNING OUT THE BOARD ===")
        print(f"Starting community cards: {self.community_cards}")

        while len(self.community_cards) < 5:
            if len(self.community_cards) == 0:
                self.deal_flop()
                print(f"Flop dealt: {self.community_cards}")
            elif len(self.community_cards) == 3:
                self.deal_turn()
                print(f"Turn dealt: {self.community_cards}")
            elif len(self.community_cards) == 4:
                self.deal_river()
                print(f"River dealt: {self.community_cards}")

        print(f"Final community cards: {self.community_cards}")
        print(f"Active players: {[str(p) for p in self.players if p.is_active()]}")

        # Ensure the showdown is called even if all players are all-in
        print("Proceeding to showdown.")
        self.showdown()

    def finish_hand(self):
        print("Finishing hand. Rotating dealer...")
        self.rotate_dealer()

        human_players = [p for p in self.players if p.is_human]
        for hp in human_players:
            if hp.stack <= 0:
                print(f"{hp.name} is out of chips and can no longer play.")
