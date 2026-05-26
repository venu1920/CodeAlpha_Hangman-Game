import random
from flask import Flask, render_template, session, jsonify, request

app = Flask(__name__)
# Secret key is required for sessions (cookie signing)
app.secret_key = 'hangman-web-app-session-secret-key-98765'

# A categorized word bank to select words from
WORD_BANK = {
    "Programming": ["python", "javascript", "developer", "computer", "software", "database", "algorithm", "compiler", "variable"],
    "Animals": ["elephant", "giraffe", "dolphin", "penguin", "kangaroo", "panther", "cheetah", "octopus", "squirrel"],
    "Countries": ["canada", "germany", "australia", "brazil", "japan", "egypt", "india", "france", "mexico"],
    "Web Dev": ["frontend", "backend", "framework", "stylesheet", "responsive", "server", "endpoint", "browser", "database"]
}

def get_random_word():
    """Selects a random category and a random word from that category."""
    category = random.choice(list(WORD_BANK.keys()))
    word = random.choice(WORD_BANK[category])
    return word, category

@app.route('/')
def home():
    """Serves the main Hangman game page."""
    return render_template('index.html')

@app.route('/api/new-game', methods=['POST'])
def new_game():
    """Starts a new game round and initializes state in the user's session."""
    secret_word, category = get_random_word()
    
    session['secret_word'] = secret_word
    session['category'] = category
    session['guessed_letters'] = []
    session['incorrect_guesses'] = 0
    
    # Initialize global session stats if they don't exist
    if 'wins' not in session:
        session['wins'] = 0
    if 'losses' not in session:
        session['losses'] = 0
        
    displayed_word = ["_" for _ in secret_word]
    
    return jsonify({
        "category": category,
        "word_length": len(secret_word),
        "displayed_word": displayed_word,
        "incorrect_guesses": 0,
        "max_incorrect": 6,
        "wins": session['wins'],
        "losses": session['losses'],
        "guessed_letters": []
    })

@app.route('/api/guess', methods=['POST'])
def make_guess():
    """Handles a single letter guess, updates state, and evaluates win/loss."""
    # Ensure game is initialized
    if 'secret_word' not in session:
        return jsonify({"error": "No active game found. Please start a new game."}), 400
        
    data = request.get_json() or {}
    guess = data.get('guess', '').strip().lower()
    
    # Basic input validation
    if len(guess) != 1 or not guess.isalpha():
        return jsonify({"error": "Invalid guess. Please enter a single alphabetical character."}), 400
        
    guessed_letters = session.get('guessed_letters', [])
    if guess in guessed_letters:
        return jsonify({"error": f"You already guessed '{guess}'."}), 400
        
    # Append guess
    guessed_letters.append(guess)
    session['guessed_letters'] = guessed_letters
    
    secret_word = session['secret_word']
    incorrect_guesses = session.get('incorrect_guesses', 0)
    
    # Check if guess is correct
    if guess not in secret_word:
        incorrect_guesses += 1
        session['incorrect_guesses'] = incorrect_guesses
        
    # Check win/loss status
    won = all(letter in guessed_letters for letter in secret_word)
    lost = incorrect_guesses >= 6
    
    status = "playing"
    if won:
        status = "won"
        session['wins'] = session.get('wins', 0) + 1
    elif lost:
        status = "lost"
        session['losses'] = session.get('losses', 0) + 1
        
    # Formulate masked display word
    displayed_word = [letter if letter in guessed_letters else "_" for letter in secret_word]
    
    response_data = {
        "displayed_word": displayed_word,
        "incorrect_guesses": incorrect_guesses,
        "max_incorrect": 6,
        "status": status,
        "wins": session.get('wins', 0),
        "losses": session.get('losses', 0),
        "guessed_letters": guessed_letters
    }
    
    # If game is over, reveal the secret word to the frontend
    if won or lost:
        response_data["secret_word"] = secret_word
        
    return jsonify(response_data)

@app.route('/api/reset-stats', methods=['POST'])
def reset_stats():
    """Resets win/loss counters."""
    session['wins'] = 0
    session['losses'] = 0
    return jsonify({
        "wins": 0,
        "losses": 0
    })

if __name__ == '__main__':
    app.run(debug=True)
