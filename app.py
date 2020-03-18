import random

from flask import Flask
from flask import render_template
from flask import request
from flask import session

from game import Hangman

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Map of game identifiers to in-progress games.
games = {}


# 2020/03/16 : 70m (+15m images), website
# 2020/03/17 : 100m, website
# 2020/03/18 : , website (leaderboard/database)
# 2020/03/19 : , api
@app.route('/', methods=['GET', 'POST'])
def website():
    invalid_guess = False

    if request.method == 'GET':
        # Several scenarios:
        # * Attempt to load an existing game if session data exists.
        #    * If session data doesn't correspond to an existing game then
        #      remove the data and present the splash screen.
        #
        # * Show the splash screen if session data does not exist.
        try:
            identifier = session['hangman']
            game = games[identifier]

        except KeyError:
            # Either session data does not exist
            # or a game does not exist for the session data.
            session.pop('hangman', None)
            return render_template('index.html', data={
                'leaderboard': {}  # TODO: Include valid leaderboard data.
            })

    elif request.method == 'POST':
        # Several scenarios:
        # * Post from forms:
        #    * 'play' game from splash screen.
        #    * 'guess' during game (possibly pass back validation error).
        #    * 'high-score' after game has been won.
        #    * 'exit' during or after game has finished.

        # Get the current game (or create one).
        # Implicitly handles post action for 'play' game form.
        try:
            identifier = session['hangman']
            game = games[identifier]

        except KeyError:
            # Clean and recreate session/game.
            identifier = '%030x' % random.randrange(2**32)
            while games.get(identifier, None):
                identifier = '%030x' % random.randrange(2 ** 32)

            game = Hangman(random.choice(Hangman.PHRASES))

            games[identifier] = game
            session['hangman'] = identifier

        # Handle POST action.
        if 'guess' in request.form:
            input_guess = request.form['guess-text']
            if game.is_guess_valid(input_guess):
                game.guess(input_guess)

            else:
                invalid_guess = True

        elif 'high-score' in request.form or 'exit' in request.form:
            # The game is over, remove the game and session.
            if 'high-score' in request.form:
                # TODO: Save high score.
                pass

            del games[identifier]
            del session['hangman']

            return render_template('index.html', data={
                'leaderboard': {}  # TODO: Include valid leaderboard data.
            })

    return render_template('index.html', data={
        'leaderboard': {},  # TODO: Include valid leaderboard data.
        'game': {
            'tries': game.get_tries(),
            'guesses': game.get_guesses(),
            'invalid_guess': invalid_guess,
            'phrase': game.get_display_phrase(),
            'game_over': game.is_game_over(),
            'game_won': game.is_game_won()
        }})
