# KindStranger.py

class BettingAgent:
    def __init__(self):
        self.balance = 1000  # Starting balance

    def place_bet(self, model, features):
        """Decides where to place a bet based on model prediction."""
        # Make sure features are in the correct format
        if len(features) != 6:
            raise ValueError("Expected 6 features for prediction.")

        # Predict the outcome
        prediction = model.predict([features])[0]

        # Map prediction to bet choice
        if prediction == 0:
            bet_choice = 'Player'
        elif prediction == 1:
            bet_choice = 'Banker'
        else:
            bet_choice = 'Tie'

        # Decide the bet amount (this can be more sophisticated)
        bet = 100  # Fixed bet for simplicity

        return bet_choice, bet

    def update_balance(self, bet, winner, bet_choice):
        """Updates the agent's balance based on the outcome."""
        if bet_choice == winner:
            # Assuming even payout
            self.balance += bet
            print(f"Bet won! +{bet}")
        else:
            self.balance -= bet
            print(f"Bet lost. -{bet}")
