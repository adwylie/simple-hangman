import random

from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask_restful import Api
from flask_restful import abort
from flask_restful import Resource
from flask_sqlalchemy import SQLAlchemy

from game import Hangman

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

api = Api(app)
db = SQLAlchemy(app)


# Database-related classes etc.
class UserScore(db.Model):
    USER_NAME_MAX_LENGTH = 20

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(USER_NAME_MAX_LENGTH), unique=False, nullable=False)
    score = db.Column(db.String(64), unique=False, nullable=False)

    def __repr__(self):
        return '<UserScore %s %s>' % (self.user, self.score)


def get_leaderboard_data(offset=0, limit=10):
    return [{'user': user_score.user, 'score': user_score.score} for user_score in
            UserScore.query.order_by(UserScore.score, UserScore.user)
            .offset(offset).limit(limit).all()]


# Map of game identifiers to in-progress games.
games = {}


def get_identifier():
    id_format = '%08x'
    max_players = 2 ** 32

    identifier = id_format % random.randrange(max_players)
    while games.get(identifier, None):
        identifier = id_format % random.randrange(max_players)

    return identifier


def get_game_obj(game, **kwargs):
    """
    Return a JSON-compatible read-only representation of the game state.

    Additional properties can be added using keyword arguments.

    """
    # NOTE: Set isn't JSON serializable, so we'll convert it to a list.
    return {
        'tries': game.get_tries(),
        'guesses': list(game.get_guesses()),
        'phrase': game.get_display_phrase(),
        'game_over': game.is_game_over(),
        'game_won': game.is_game_won(),
        **kwargs
    }


# Web Interface
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
            identifier = get_identifier()
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
                user = request.form['user'][:UserScore.USER_NAME_MAX_LENGTH]
                score = game.get_tries()

                db.session.add(UserScore(user=user, score=score))
                db.session.commit()

            del games[identifier]
            del session['hangman']

            return render_template('index.html', data={
                'leaderboard': get_leaderboard_data()
            })

    return render_template('index.html', data={
        'leaderboard': get_leaderboard_data(),
        'game': get_game_obj(game, invalid_guess=invalid_guess)})


# API methods.
class GamesAPI(Resource):
    # Games resource.
    # Create new game, get games.
    def get(self):
        """Get a list of all in-progress games (by identifier)."""
        # Return the requested games w/ 200, empty list otherwise.
        return list(games.keys()), 200

    def post(self):
        """Create a new game."""
        # Return 201 w/ location header and game data object.
        identifier = get_identifier()
        game = Hangman(random.choice(Hangman.PHRASES))

        games[identifier] = game

        game_json = get_game_obj(game, id=identifier)
        headers = {'Location': api.url_for(GameAPI, identifier=identifier)}

        return game_json, 201, headers


class GameAPI(Resource):
    # Games resource.
    # Get game, delete game.
    def get(self, identifier):
        """Get a specific game."""
        # Return the requested game w/ 200, 404 otherwise.
        try:
            game = games[identifier]

            game_json = get_game_obj(game, id=identifier)
            return game_json, 201

        except KeyError:
            abort(404)

    def delete(self, identifier):
        """Delete a game."""
        # Remove game and session information,
        # return 204, or 404 if doesn't exist.
        try:
            games.pop(identifier)
            return '', 204

        except KeyError:
            abort(404)


class GameGuessesAPI(Resource):
    # Guesses sub-resource.
    def post(self, identifier):
        """Update an in-play game with a new guess."""
        # Update game and return game data object.
        try:
            game = games[identifier]

            # Check for a valid game state,
            # don't allow guesses if game is over.
            if game.is_game_over():
                abort(409)

            # Get the guess, validate it, and then update the game.
            request_json = request.get_json()
            if not request_json:
                abort(400)

            guess = request_json.get('guess', None)
            if game.is_guess_valid(guess):
                game.guess(guess)

                game_json = get_game_obj(game, id=identifier)
                return game_json, 200

            else:
                abort(400)

        except KeyError:
            # No game exists with the given identifier.
            abort(404)


class GameScoreAPI(Resource):
    # Score sub-resource.
    def post(self, identifier):
        """
        Submit a score for a won game.

        Also deletes the game after the score has been submitted.

        """
        # User name passed for a game that is over and has been won.
        try:
            game = games[identifier]

            # Check for a valid game state, don't allow score submission
            # unless the game is over and has been won.
            if not game.is_game_over() or not game.is_game_won():
                abort(409)

            # Get the name to submit w/ score,
            # validate it, and then update the game.
            request_json = request.get_json()
            if not request_json:
                abort(400)

            user = request_json.get('user', None)
            score = game.get_tries()

            if user and isinstance(user, str) \
                    and len(user) <= UserScore.USER_NAME_MAX_LENGTH:
                user_score = UserScore(user=user, score=score)
                db.session.add(user_score)
                db.session.commit()

                # TODO: Not great to have POST w/ DELETE semantics.
                del games[identifier]

                # Scores don't have a specific location,
                # so we won't add a Location header.
                return user_score, 201

            else:
                abort(400)

        except KeyError:
            # No game exists with the given identifier.
            abort(404)


class ScoresAPI(Resource):
    # Scores resource.
    def get(self):
        """Return (already sorted) leaderboard data."""
        # Allow query parameters for offset and limit.
        offset = request.args.get('offset', 0)
        limit = request.args.get('limit', UserScore.query.count())

        return get_leaderboard_data(offset, limit), 200


api.add_resource(GamesAPI, '/api/games')
api.add_resource(GameAPI, '/api/games/<string:identifier>')
api.add_resource(GameGuessesAPI, '/api/games/<string:identifier>/guesses')
api.add_resource(GameScoreAPI, '/api/games/<string:identifier>/score')
api.add_resource(ScoresAPI, '/api/scores')
