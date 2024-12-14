from BlackjackLogic import BlackjackGame

def get_starting_stack():
    while True:
        try:
            stack = float(input("Enter your starting stack: "))
            if stack <= 0:
                print("Starting stack must be greater than 0.")
                continue
            return stack
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    starting_stack = get_starting_stack()
    game = BlackjackGame(starting_stack=starting_stack)
    game.start()

if __name__ == "__main__":
    main()
