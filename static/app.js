/* ==========================================================================
   Hangman Web Experience - Client JavaScript
   Handles API communication, DOM updates, and keyboard events
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const statsWins = document.getElementById('stats-wins');
    const statsLosses = document.getElementById('stats-losses');
    const gameCategory = document.getElementById('game-category');
    const guessesRemaining = document.getElementById('guesses-remaining');
    const gameProgress = document.getElementById('game-progress');
    const wordSlots = document.getElementById('word-slots');
    const keyboard = document.getElementById('keyboard');
    
    // Action Buttons
    const btnNewGame = document.getElementById('btn-new-game');
    const btnResetStats = document.getElementById('btn-reset-stats');
    
    // Modal Elements
    const modalBackdrop = document.getElementById('modal-backdrop');
    const modal = document.getElementById('game-modal');
    const modalIcon = document.getElementById('modal-icon');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const modalRevealedWord = document.getElementById('modal-revealed-word');
    const modalBtnAction = document.getElementById('modal-btn-action');

    // Local state tracking
    let isGameOver = false;
    let guessedLetters = [];

    // Initialize Game
    initGame();

    // Event Listeners
    btnNewGame.addEventListener('click', () => startNewGame());
    btnResetStats.addEventListener('click', () => resetStats());
    modalBtnAction.addEventListener('click', () => {
        closeModal();
        startNewGame();
    });

    // Listen to physical keyboard keypresses
    document.addEventListener('keydown', (e) => {
        if (isGameOver) return;
        
        // Ensure modal is closed before accepting key inputs
        if (modalBackdrop.classList.contains('active')) return;

        const char = e.key.toLowerCase();
        
        // Verify key is a single English letter
        if (char.length === 1 && char >= 'a' && char <= 'z') {
            handleGuess(char);
        }
    });

    /**
     * Initializes the keyboard grid and pulls initial game state.
     */
    function initGame() {
        createKeyboard();
        startNewGame();
    }

    /**
     * Creates virtual keys A-Z dynamically.
     */
    function createKeyboard() {
        keyboard.innerHTML = '';
        const alphabet = 'abcdefghijklmnopqrstuvwxyz';
        
        for (let i = 0; i < alphabet.length; i++) {
            const letter = alphabet[i];
            const button = document.createElement('button');
            button.classList.add('key');
            button.id = `key-${letter}`;
            button.textContent = letter;
            button.setAttribute('data-letter', letter);
            
            button.addEventListener('click', () => {
                if (!isGameOver) {
                    handleGuess(letter);
                }
            });
            
            keyboard.appendChild(button);
        }
    }

    /**
     * Sends API call to start a new round.
     */
    async function startNewGame() {
        try {
            const response = await fetch('/api/new-game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) throw new Error('Failed to start a new game');
            
            const data = await response.json();
            updateUI(data);
            isGameOver = false;
            guessedLetters = [];
            
            // Enable and clear all keyboard buttons
            const keys = document.querySelectorAll('.key');
            keys.forEach(key => {
                key.disabled = false;
                key.className = 'key'; // Resets styles to default
            });
            
        } catch (error) {
            console.error('Error starting game:', error);
            alert('Failed to connect to game server. Please try again.');
        }
    }

    /**
     * Process a letter guess via API.
     */
    async function handleGuess(letter) {
        // Prevent duplicate guesses
        if (guessedLetters.includes(letter)) return;
        
        guessedLetters.push(letter);
        
        // Instantly disable the virtual key
        const keyBtn = document.getElementById(`key-${letter}`);
        if (keyBtn) {
            keyBtn.disabled = true;
        }

        try {
            const response = await fetch('/api/guess', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ guess: letter })
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.warn(errorData.error);
                return;
            }

            const data = await response.json();
            
            // Highlight the virtual button
            if (keyBtn) {
                if (data.displayed_word.includes(letter)) {
                    keyBtn.classList.add('correct');
                } else {
                    keyBtn.classList.add('incorrect');
                }
            }
            
            updateUI(data);
            
            // Check round end
            if (data.status === 'won' || data.status === 'lost') {
                isGameOver = true;
                showGameOverModal(data.status, data.secret_word);
            }

        } catch (error) {
            console.error('Error processing guess:', error);
        }
    }

    /**
     * Dynamic DOM rendering for current game state.
     */
    function updateUI(data) {
        // Update stats
        statsWins.textContent = data.wins;
        statsLosses.textContent = data.losses;
        
        // Update category & counts
        gameCategory.textContent = data.category;
        guessesRemaining.textContent = `${data.max_incorrect - data.incorrect_guesses}/${data.max_incorrect}`;
        
        // Update progress bar width
        const progressPercentage = (data.incorrect_guesses / data.max_incorrect) * 100;
        gameProgress.style.width = `${progressPercentage}%`;
        
        // Update word slots
        wordSlots.innerHTML = '';
        data.displayed_word.forEach(char => {
            const slot = document.createElement('div');
            slot.classList.add('letter-slot');
            
            if (char !== '_') {
                slot.textContent = char;
                slot.classList.add('revealed');
            } else {
                slot.textContent = '';
            }
            
            wordSlots.appendChild(slot);
        });
    }

    /**
     * Sends API call to reset wins and losses.
     */
    async function resetStats() {
        if (!confirm('Are you sure you want to reset your score record?')) return;
        
        try {
            const response = await fetch('/api/reset-stats', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) throw new Error('Failed to reset stats');
            
            const data = await response.json();
            statsWins.textContent = data.wins;
            statsLosses.textContent = data.losses;
            
        } catch (error) {
            console.error('Error resetting stats:', error);
        }
    }

    /**
     * Triggers the game over modal display.
     */
    function showGameOverModal(status, secretWord) {
        modalRevealedWord.textContent = secretWord.toUpperCase();
        
        if (status === 'won') {
            modalIcon.textContent = '🎉';
            modalTitle.textContent = 'Victory!';
            modalMessage.textContent = 'Excellent word-solving skills! You guessed it right.';
            modal.style.boxShadow = '0 24px 64px rgba(0, 0, 0, 0.6), 0 0 40px rgba(16, 185, 129, 0.4)';
        } else {
            modalIcon.textContent = '💀';
            modalTitle.textContent = 'Game Over!';
            modalMessage.textContent = 'You ran out of guesses. Keep practicing!';
            modal.style.boxShadow = '0 24px 64px rgba(0, 0, 0, 0.6), 0 0 40px rgba(239, 68, 68, 0.4)';
        }
        
        modalBackdrop.classList.add('active');
    }

    /**
     * Closes the game over modal display.
     */
    function closeModal() {
        modalBackdrop.classList.remove('active');
    }
});
