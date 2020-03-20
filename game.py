class Hangman:
    MAXIMUM_TRIES = 5
    PHRASES = ['3dhubs', 'marvin', 'print', 'filament', 'order', 'layer']

    def __init__(self, phrase, guesses=None, tries=None):
        # Allow an existing game to be continued if given all arguments.
        # TODO: Validate arguments?
        self.phrase = phrase
        self.guesses = guesses or {' '}
        self.tries = tries or 0

    def guess(self, letter):
        """Allow a user to make a guess, uppercase/lowercase doesn't matter."""
        self.guesses.add(letter.lower())

        if letter.lower() not in self.phrase.lower():
            self.tries += 1

    def is_game_over(self):
        return self.tries >= Hangman.MAXIMUM_TRIES \
               or set(self.phrase.lower()).issubset(self.guesses)

    def is_game_won(self):
        return set(self.phrase.lower()).issubset(self.guesses) \
               and self.tries < Hangman.MAXIMUM_TRIES

    def is_guess_valid(self, guess):
        # The input guess must be a single character, alphanumeric,
        # and must not have already been guessed.
        if guess and isinstance(guess, str) \
                and len(guess) == 1 \
                and guess.isalnum() \
                and guess.lower() not in self.guesses:
            return True

        return False

    def get_display_phrase(self):
        """Return the phrase with unknown letters covered."""
        return ''.join(
            ['_' if x.lower() not in self.guesses else x for x in self.phrase])

    def get_guesses(self):
        """Convenience function for GUI (show user which letters are available)."""
        # Return a copy of the guesses so it can't be modified.
        return self.guesses - {' '}

    def get_tries(self):
        """Convenience function for GUI (drawing the hanged man)."""
        return self.tries


if __name__ == '__main__':
    import random

    def get_input():
        return input("Enter your guess: ").strip()

    game = Hangman(random.choice(Hangman.PHRASES))

    while not game.is_game_over():

        print(' '.join(game.get_display_phrase()))

        # Allow the user to make a guess.
        text = get_input()

        while not game.is_guess_valid(text):
            print("Invalid guess entered, please try again.")
            text = get_input()

        game.guess(text)

        if game.is_game_over():
            if game.is_game_won():
                print("Congratulations, you win!")

            else:
                print("Sorry, you lost!")

            exit()
