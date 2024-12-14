from BlackjackDeck import Deck
from BlackjackPlayer import Player, Hand


class BlackjackGame:
    def __init__(self, starting_stack=1000, num_decks=1):
        self.deck = Deck(num_decks=num_decks)
        self.player = Player(name="Player", stack=starting_stack)
        self.dealer = Player(name="Dealer", stack=0)  # Dealer doesn't use stack

    def take_bet(self):
        while True:
            try:
                bet = float(input(f"Your current stack: {self.player.stack}. Enter your bet: "))
                if bet <= 0:
                    print("Bet must be greater than 0.")
                    continue
                self.player.place_bet(bet)
                break
            except ValueError as e:
                print(f"Invalid input: {e}")

    def initial_deal(self):
        self.player.reset_hands()
        self.dealer.reset_hands()

        # Dealer starts with one hand
        self.dealer.hands = [Hand()]

        # Deal two cards to each hand of the player and dealer
        for _ in range(2):
            self.player.hands[0].add_card(self.deck.deal_card())  # Deal to player's single hand
            self.dealer.hands[0].add_card(self.deck.deal_card())  # Deal to dealer's single hand

    def show_hands(self, show_dealer_card=False):
        print("\n--- Hands ---")
        # Show player's hands
        for idx, hand in enumerate(self.player.hands):
            status = "Active" if hand.is_active else "Inactive"
            print(
                f"Player Hand {idx + 1}: {', '.join(str(card) for card in hand.cards)} (Value: {hand.calculate_value()}) [{status}]")
        # Show dealer's hand
        if show_dealer_card:
            dealer_hand = self.dealer.hands[0]
            print(
                f"Dealer: {', '.join(str(card) for card in dealer_hand.cards)} (Value: {dealer_hand.calculate_value()})")
        else:
            dealer_hand = self.dealer.hands[0]
            if len(dealer_hand.cards) >= 1:
                print(f"Dealer: {str(dealer_hand.cards[0])}, Hidden Card")
            else:
                print("Dealer: No cards dealt yet.")
        print("------------\n")

    def player_turn(self):
        for hand_index, hand in enumerate(self.player.hands):
            self.player.current_hand_index = hand_index
            while hand.is_active and not hand.is_busted() and not hand.has_blackjack():
                self.show_hands()
                options = ['[H]it', '[S]tand']
                if len(hand.cards) == 2 and self.player.stack >= hand.bet:
                    if hand.can_split():
                        options.append('[P]split')
                    options.append('[D]ouble Down')
                print(f"Options for Hand {hand_index + 1}: " + ', '.join(options))
                choice = input("Choose an option: ").strip().lower()

                if choice == 'h':
                    hand.add_card(self.deck.deal_card())
                    print(f"Hand {hand_index + 1} hits.")
                elif choice == 's':
                    hand.is_active = False
                    print(f"Hand {hand_index + 1} stands.")
                elif choice == 'd' and '[D]ouble Down' in options:
                    self.handle_double_down(hand)
                elif choice == 'p' and '[P]split' in options:
                    self.handle_split(hand_index)
                else:
                    print("Invalid choice. Please choose a valid option.")

                if hand.is_busted():
                    print(f"Hand {hand_index + 1} has busted!")

    def handle_double_down(self, hand):
        try:
            double_bet = hand.bet
            if double_bet > self.player.stack:
                print("Insufficient funds to double down.")
                return
            hand.bet += double_bet
            self.player.stack -= double_bet
            hand.is_doubled = True
            hand.add_card(self.deck.deal_card())
            hand.is_active = False  # Automatically stands after doubling down
            print(f"Hand doubled down. New bet: {hand.bet}")
        except ValueError as e:
            print(f"Error: {e}")

    def handle_split(self, hand_index):
        hand = self.player.hands[hand_index]
        if not hand.can_split():
            print("Cannot split this hand.")
            return
        try:
            split_bet = hand.bet
            if split_bet > self.player.stack:
                print("Insufficient funds to split.")
                return
            # Create two new hands
            card1 = hand.cards[0]
            card2 = hand.cards[1]
            new_hand1 = Hand(cards=[card1], bet=split_bet)
            new_hand2 = Hand(cards=[card2], bet=split_bet)
            self.player.stack -= split_bet
            # Replace the original hand with the two new hands
            self.player.hands[hand_index] = new_hand1
            self.player.hands.insert(hand_index + 1, new_hand2)
            # Deal one additional card to each new hand
            new_hand1.add_card(self.deck.deal_card())
            new_hand2.add_card(self.deck.deal_card())
            print(f"Hand {hand_index + 1} has been split into two hands.")
        except ValueError as e:
            print(f"Error: {e}")

    def dealer_turn(self):
        print("\nDealer's turn:")
        self.show_hands(show_dealer_card=True)
        dealer_hand = self.dealer.hands[0]
        while dealer_hand.calculate_value() < 17:
            print("Dealer hits.")
            dealer_hand.add_card(self.deck.deal_card())
            self.show_hands(show_dealer_card=True)
            if dealer_hand.is_busted():
                print("Dealer has busted!")
                break
        if not dealer_hand.is_busted():
            print("Dealer stands.")

    def settle_bets(self):
        dealer_hand = self.dealer.hands[0]
        dealer_value = dealer_hand.calculate_value()
        dealer_bust = dealer_hand.is_busted()
        dealer_blackjack = dealer_hand.has_blackjack()

        for idx, hand in enumerate(self.player.hands):
            player_value = hand.calculate_value()
            player_bust = hand.is_busted()
            player_blackjack = hand.has_blackjack()

            print(f"\nSettling Hand {idx + 1}:")
            if player_blackjack:
                if dealer_blackjack:
                    print("Both player and dealer have Blackjack. Push.")
                    self.player.stack += hand.bet
                else:
                    print("Blackjack! You win 3:2.")
                    winnings = hand.bet * 2.5
                    self.player.stack += winnings
            elif player_bust:
                print("You busted. You lose your bet.")
                # Bet is already deducted
            elif dealer_bust:
                print("Dealer busted. You win your bet.")
                self.player.stack += hand.bet * 2
            elif dealer_blackjack:
                print("Dealer has Blackjack. You lose your bet.")
                # Bet is already deducted
            else:
                if player_value > dealer_value:
                    print(f"You have {player_value} and dealer has {dealer_value}. You win!")
                    self.player.stack += hand.bet * 2
                elif player_value < dealer_value:
                    print(f"You have {player_value} and dealer has {dealer_value}. You lose.")
                    # Bet is already deducted
                else:
                    print(f"Both have {player_value}. Push.")
                    self.player.stack += hand.bet

    def play_round(self):
        self.take_bet()
        self.initial_deal()
        self.show_hands()
        self.player_turn()
        if any(not hand.is_busted() and not hand.has_blackjack() for hand in self.player.hands):
            self.dealer_turn()
        self.settle_bets()
        print(f"\nYour current stack: {self.player.stack}\n")

    def is_game_over(self):
        return self.player.stack <= 0

    def start(self):
        print("Welcome to Blackjack!")
        while True:
            if self.is_game_over():
                print("You have run out of money! Game over.")
                break
            self.play_round()
            choice = input("Do you want to play another round? [Y/N]: ").strip().lower()
            if choice != 'y':
                print("Thank you for playing!")
                break
