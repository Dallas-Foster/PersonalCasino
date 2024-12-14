from player import Player
from game import Game

def main():
    num_bots = int(input("How many bot opponents? "))
    player_stack = int(input("Enter your starting stack size: "))
    bot_stack = int(input("Enter each bot's starting stack size: "))

    # Create human player
    human_player = Player("You", is_human=True)
    human_player.stack = player_stack
    players = [human_player]

    # Create bot players
    for i in range(num_bots):
        bot_player = Player(f"Bot_{i+1}", is_human=False)
        bot_player.stack = bot_stack
        players.append(bot_player)

    game = Game(players)

    # Let game_over() determine when to stop
    while not game.game_over():
        game.play_hand()

    print("Game has ended.")

if __name__ == "__main__":
    main()
