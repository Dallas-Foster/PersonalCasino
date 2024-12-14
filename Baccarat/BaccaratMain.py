# BaccaratMain.py

from BaccaratLogic import play_baccarat
from BaccaratStrategy import train_model
import joblib
import numpy as np


def load_model(filename="baccarat_model_with_history.pkl"):
    """
    Loads the trained model, scaler, and label encoder.

    Args:
        filename (str): Path to the saved model file.

    Returns:
        model (MLPClassifier): Trained machine learning model.
        scaler (StandardScaler): Fitted scaler for feature normalization.
        label_encoder (LabelEncoder): Fitted label encoder.
    """
    data = joblib.load(filename)
    return data['model'], data['scaler'], data['label_encoder']


def get_user_bet():
    """
    Prompts the user to place a bet.

    Returns:
        bet_choice (str): User's bet choice ('Player', 'Banker', 'Tie').
    """
    while True:
        bet = input("Place your bet on 'Player', 'Banker', or 'Tie': ").strip().capitalize()
        if bet in ['Player', 'Banker', 'Tie']:
            return bet
        else:
            print("Invalid bet choice. Please enter 'Player', 'Banker', or 'Tie'.")


def get_bet_amount(current_balance):
    """
    Prompts the user to enter a bet amount.

    Args:
        current_balance (int): User's current balance.

    Returns:
        bet_amount (int): Amount the user wants to bet.
    """
    while True:
        try:
            amount = int(input(f"Enter bet amount (Available balance: {current_balance}): "))
            if 1 <= amount <= current_balance:
                return amount
            else:
                print(f"Please enter a valid amount between 1 and {current_balance}.")
        except ValueError:
            print("Invalid input. Please enter a numerical value.")


def display_history(history):
    """
    Displays the last 3 game outcomes.

    Args:
        history (list): List of past game outcomes.
    """
    print(f"\n--- Last 3 Game Outcomes ---")
    print(" | ".join(history))
    print("-----------------------------")


def display_cards(player_card1, player_card2, player_card3, banker_card1, banker_card2, banker_card3):
    """
    Displays the cards for both Player and Banker.

    Args:
        player_card1 (int): Player's first card.
        player_card2 (int): Player's second card.
        player_card3 (int): Player's third card (0 if not drawn).
        banker_card1 (int): Banker's first card.
        banker_card2 (int): Banker's second card.
        banker_card3 (int): Banker's third card (0 if not drawn).
    """
    print("\n--- Current Game Cards ---")

    # Display Player's Cards
    if player_card3 != 0:
        print(f"Player's Cards: {player_card1}, {player_card2}, {player_card3}")
    else:
        print(f"Player's Cards: {player_card1}, {player_card2}")

    # Display Banker's Cards
    if banker_card3 != 0:
        print(f"Banker's Cards: {banker_card1}, {banker_card2}, {banker_card3}")
    else:
        print(f"Banker's Cards: {banker_card1}, {banker_card2}")

    print("----------------------------")


def simulate_game(user_bet_choice, bet_amount, model, scaler, label_encoder, history):
    """
    Simulates a single game of Baccarat.

    Args:
        user_bet_choice (str): User's bet choice.
        bet_amount (int): Amount the user wants to bet.
        model (MLPClassifier): Trained machine learning model.
        scaler (StandardScaler): Fitted scaler for feature normalization.
        label_encoder (LabelEncoder): Fitted label encoder.
        history (list): List of past game outcomes.

    Returns:
        outcome (str): Outcome of the current game ('Player', 'Banker', 'Tie').
        result (str): 'win' if user won, 'lose' otherwise.
        history (list): Updated list of past game outcomes.
    """
    # Simulate a game
    player_score, banker_score, winner, player_card1, player_card2, player_card3, banker_card1, banker_card2, banker_card3 = play_baccarat()

    # Update history
    history.append(winner)
    if len(history) > 3:
        history.pop(0)

    # Prepare features for prediction (last 3 outcomes)
    features = history.copy()
    display_history(history)
    print(f"Features for prediction: {features}")

    # Encode features
    encoded_features = label_encoder.transform(features)
    encoded_features = encoded_features.reshape(1, -1)  # Reshape for scaler

    # Scale features
    scaled_features = scaler.transform(encoded_features)

    # Model suggestion
    prediction = model.predict(scaled_features)[0]
    suggestion = label_encoder.inverse_transform([prediction])[0]
    print(f"[Model Suggestion] It is recommended to bet on: {suggestion}")

    # Display the cards for both Player and Banker
    display_cards(player_card1, player_card2, player_card3, banker_card1, banker_card2, banker_card3)

    # Determine if user's bet was correct
    if user_bet_choice == winner:
        print(f"Congratulations! You won {bet_amount}.")
        result = 'win'
    else:
        print(f"Sorry, you lost {bet_amount}.")
        result = 'lose'

    return winner, result, history


def main():
    """Main function."""
    print("Welcome to Baccarat!")

    # Attempt to load the trained model
    print("Loading trained model...")
    try:
        model, scaler, label_encoder = load_model()
    except FileNotFoundError:
        print("Model file 'baccarat_model_with_history.pkl' not found.")
        print("Training the model now...")
        model, scaler, label_encoder = train_model()
        print("Model training complete.")

    # Initialize user balance
    user_balance = 1000  # Starting balance

    # Initialize history with 'Tie' to handle initial games
    history = ['Tie'] * 3

    while True:
        print(f"\nCurrent Balance: {user_balance}")

        # Get user bet
        bet_choice = get_user_bet()
        bet_amount = get_bet_amount(user_balance)

        # Simulate game and get outcome
        outcome, result, history = simulate_game(bet_choice, bet_amount, model, scaler, label_encoder, history)

        # Update user balance
        if result == 'win':
            user_balance += bet_amount
        else:
            user_balance -= bet_amount

        print(f"Game Outcome: {outcome}")
        print(f"Updated Balance: {user_balance}")

        # Check if user wants to continue
        if user_balance <= 0:
            print("You've run out of balance! Game over.")
            break

        continue_game = input("Do you want to play another game? (yes/no): ").strip().lower()
        if continue_game not in ['yes', 'y']:
            print("Thank you for playing! Goodbye.")
            break


if __name__ == "__main__":
    main()
