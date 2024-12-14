from game_logic import create_deck, get_card_value


def main():
    print("Welcome to the Hi-Lo Casino Game!")
    print("Guess whether the next card will be Higher (H) or Lower (L).")
    print("You start with 100 chips. Good luck!\n")

    chips = 100
    deck = create_deck()  # Generate and shuffle the deck

    # Draw the first card
    current_card = deck.pop()

    while chips > 0 and len(deck) > 0:
        print(f"Current card: {current_card}")
        guess = input("Will the next card be Higher (H) or Lower (L)? ").strip().lower()

        while guess not in ['h', 'l']:
            print("Invalid input. Please enter 'H' for Higher or 'L' for Lower.")
            guess = input("Will the next card be Higher (H) or Lower (L)? ").strip().lower()

        # Draw the next card
        next_card = deck.pop()
        print(f"Next card: {next_card}")

        # Compare values
        if guess == 'h' and get_card_value(next_card) > get_card_value(current_card):
            chips += 10
            print("Correct! You win 10 chips.")
        elif guess == 'l' and get_card_value(next_card) < get_card_value(current_card):
            chips += 10
            print("Correct! You win 10 chips.")
        else:
            chips -= 10
            print("Wrong! You lose 10 chips.")

        print(f"Your current chip count: {chips}\n")
        current_card = next_card

        if chips > 0 and len(deck) > 0:
            play_again = input("Do you want to keep playing? (Y/N): ").strip().lower()
            if play_again != 'y':
                break

    if len(deck) == 0:
        print("No more cards left in the deck!")
    print("Game over!")
    print(f"You finished with {chips} chips.")
    print("Thanks for playing!")


if __name__ == "__main__":
    main()
