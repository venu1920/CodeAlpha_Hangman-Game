import random

# A categorized word bank to select words from
WORD_BANK = {
    "Programming": ["python", "javascript", "developer", "computer", "software", "database", "algorithm", "compiler", "variable"],
    "Animals": ["elephant", "giraffe", "dolphin", "penguin", "kangaroo", "panther", "cheetah", "octopus", "squirrel"],
    "Countries": ["canada", "germany", "australia", "brazil", "japan", "egypt", "india", "france", "mexico"]
}

def get_random_word():
    """Selects a random category and a random word from that category."""
    category = random.choice(list(WORD_BANK.keys()))
    word = random.choice(WORD_BANK[category])
    return word, category

def play_round():
    """Plays a single round of Hangman. Returns True if the player wins, False otherwise."""
    secret_word, category = get_random_word()
    guessed_letters = set()
    incorrect_guesses = 0
    max_incorrect = 6
    
    print("\n" + "=" * 40)
    print(f"Category: {category}")
    print(f"The word has {len(secret_word)} letters.")
    print("=" * 40)
    
    while incorrect_guesses < max_incorrect:
        # Display the current state of the word (e.g., p _ t h o n)
        displayed_word = []
        for letter in secret_word:
            if letter in guessed_letters:
                displayed_word.append(letter)
            else:
                displayed_word.append("_")
        
        current_display = " ".join(displayed_word)
        print(f"\nWord: {current_display}")
        print(f"Incorrect guesses remaining: {max_incorrect - incorrect_guesses}")
        print(f"Guessed letters: {', '.join(sorted(guessed_letters)) if guessed_letters else 'None'}")
        
        # Check if the player has guessed all the letters
        if "_" not in displayed_word:
            print(f"\n🎉 Congratulations! You guessed the word: '{secret_word}'!")
            return True
            
        # Get and validate user input
        guess = input("Enter a letter: ").strip().lower()
        
        if len(guess) != 1 or not guess.isalpha():
            print("⚠️ Invalid input. Please enter a single alphabetical letter.")
            continue
            
        if guess in guessed_letters:
            print(f"⚠️ You already guessed the letter '{guess}'. Try another one.")
            continue
            
        # Add to guessed letters
        guessed_letters.add(guess)
        
        # Check if the guess is in the secret word
        if guess in secret_word:
            print(f"✅ Good job! '{guess}' is in the word.")
        else:
            incorrect_guesses += 1
            print(f"❌ Sorry, '{guess}' is not in the word.")
            
    else:
        print(f"\n💀 Game Over! You ran out of guesses. The word was '{secret_word}'.")
        return False

def main():
    wins = 0
    losses = 0
    
    print("=" * 40)
    print("Welcome to Hangman!")
    print("Guess the secret word one letter at a time.")
    print("You have a maximum of 6 incorrect guesses allowed per round.")
    print("=" * 40)
    
    while True:
        # Play a round and update score
        won = play_round()
        if won:
            wins += 1
        else:
            losses += 1
            
        # Display current session stats
        print("\n" + "-" * 20)
        print(f"Current Stats: Wins: {wins} | Losses: {losses}")
        print("-" * 20)
        
        # Ask to play again
        while True:
            play_again = input("\nDo you want to play another round? (y/n): ").strip().lower()
            if play_again in ['y', 'yes', 'n', 'no']:
                break
            print("⚠️ Please enter 'y' for Yes or 'n' for No.")
            
        if play_again in ['n', 'no']:
            print("\nThanks for playing Hangman! Final score:")
            print(f"Wins: {wins} | Losses: {losses}")
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()
