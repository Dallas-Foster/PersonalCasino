# BaccaratLogic.py

import numpy as np


def play_baccarat():
    """
    Simulates a single game of Baccarat following official rules.

    Returns:
        player_score (int): Player's total score.
        banker_score (int): Banker's total score.
        winner (str): 'Player', 'Banker', or 'Tie'.
        player_card1 (int): Player's first card.
        player_card2 (int): Player's second card.
        player_card3 (int): Player's third card (0 if not drawn).
        banker_card1 (int): Banker's first card.
        banker_card2 (int): Banker's second card.
        banker_card3 (int): Banker's third card (0 if not drawn).
    """
    # Generate random cards between 1 and 9 for Player and Banker
    player_card1, player_card2 = np.random.randint(1, 10, size=2)
    banker_card1, banker_card2 = np.random.randint(1, 10, size=2)

    # Calculate initial scores
    player_score = (player_card1 + player_card2) % 10
    banker_score = (banker_card1 + banker_card2) % 10

    # Initialize third cards as 0 (no third card drawn)
    player_card3 = 0
    banker_card3 = 0

    # Check for Natural Win
    if player_score in [8, 9] or banker_score in [8, 9]:
        if player_score > banker_score:
            winner = 'Player'
        elif banker_score > player_score:
            winner = 'Banker'
        else:
            winner = 'Tie'
        return player_score, banker_score, winner, player_card1, player_card2, player_card3, banker_card1, banker_card2, banker_card3

    # Determine if Player draws a third card
    if player_score <= 5:
        player_card3 = np.random.randint(1, 10)
        player_score = (player_score + player_card3) % 10
        player_draw = True
    else:
        player_draw = False

    # Determine if Banker draws a third card based on Player's third card
    if player_draw:
        if player_card3 in [0, 1, 2, 3]:
            if banker_score <= 4:
                banker_card3 = np.random.randint(1, 10)
                banker_score = (banker_score + banker_card3) % 10
        elif player_card3 in [4, 5]:
            if banker_score <= 5:
                banker_card3 = np.random.randint(1, 10)
                banker_score = (banker_score + banker_card3) % 10
        elif player_card3 in [6, 7]:
            if banker_score <= 6:
                banker_card3 = np.random.randint(1, 10)
                banker_score = (banker_score + banker_card3) % 10
        elif player_card3 == 8:
            if banker_score <= 2:
                banker_card3 = np.random.randint(1, 10)
                banker_score = (banker_score + banker_card3) % 10
        else:  # player_card3 >=9
            if banker_score <= 3:
                banker_card3 = np.random.randint(1, 10)
                banker_score = (banker_score + banker_card3) % 10
    else:
        # Player stands; Banker draws if Banker score <=5
        if banker_score <= 5:
            banker_card3 = np.random.randint(1, 10)
            banker_score = (banker_score + banker_card3) % 10

    # Determine the winner
    if player_score > banker_score:
        winner = 'Player'
    elif banker_score > player_score:
        winner = 'Banker'
    else:
        winner = 'Tie'

    return player_score, banker_score, winner, player_card1, player_card2, player_card3, banker_card1, banker_card2, banker_card3
