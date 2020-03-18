import random

from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask_sqlalchemy import SQLAlchemy

from game import Hangman

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Database setup/configuration
db = SQLAlchemy(app)


class Score(db.Model):
    USER_NAME_MAX_LENGTH = 20

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(USER_NAME_MAX_LENGTH), unique=False, nullable=False)
    score = db.Column(db.String(64), unique=False, nullable=False)

    def __repr__(self):
        return '<Score %s %s>' % (self.user, self.score)


def get_leaderboard_data():
    return [(score.user, score.score) for score
            in Score.query.order_by(Score.score, Score.user).limit(10).all()]


# Map of game identifiers to in-progress games.
games = {}


# 2020/03/16 : 70m (+15m images), website
# 2020/03/17 : 100m, website
# 2020/03/18 : 60m, website (leaderboard/database)
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
                'leaderboard': get_leaderboard_data()
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
                # Note: High score is # of tries used, so lower is better.
                # Ensure the user name length is valid.
                user = request.form['user'][:Score.USER_NAME_MAX_LENGTH]
                score = game.get_tries()
                db.session.add(Score(user=user, score=score))
                db.session.commit()

            del games[identifier]
            del session['hangman']

            return render_template('index.html', data={
                'leaderboard': get_leaderboard_data()
            })

    return render_template('index.html', data={
        'leaderboard': get_leaderboard_data(),
        'game': {
            'tries': game.get_tries(),
            'guesses': game.get_guesses(),
            'invalid_guess': invalid_guess,
            'phrase': game.get_display_phrase(),
            'game_over': game.is_game_over(),
            'game_won': game.is_game_won()
        }})
