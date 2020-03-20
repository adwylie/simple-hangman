## Hangman Game

```
  |======|        A B C D E F G H I J K L M
  | /    !        N O P Q R S T U V W X Y Z
  |/     O        0 1 2 3 4 5 6 7 8 9
  |    --|--
  |      |        H a _ g m a _   G a m _  
  |     / \
  |               Invalid guess, try again.
=====             Enter your guess: b
```


### Requirements

- Game play operates as a regular hangman game.

- Placeholders are displayed for unknown letters of a phrase.
- The user can make a guess by selecting a letter.
- If a guess matches an unknown letter, that letter becomes a known letter.
- Known letters are displayed in the phrase instead of placeholders.

- Each guess that does not match an unknown letter counts as a try.
- The game is over (a loss) when the user accumulates five (5) tries.
- The game is over (a win) if all letters of the phrase are known
  and less than five (5) tries have been accumulated.

- If the user wins they will be congratulated.
- If the user wins their score will be saved.

- Six phrases are possible: '3dhubs', 'marvin', 'print', 'filament', 'order', 'layer'.

- The game can be played by clients using a simple API.
- The game can be played by users using an interface.


### Derived requirements (Assumptions)

- The API provided to clients will be REST-ful.
- The interface provided to users will be web-based.

- A list of user scores should be displayed in the game's interface.
- Only the best 10 scores will be displayed in the game's interface.
- Scores are defined as the number of tries accumulated when the game is won.
  Therefore, a lower score is better.

- Phrases and guesses are assumed to be alpha-numeric only.
- The case (uppercase/lowercase) of phrases and guesses does not matter.


## Deployment

### Development

1. Clone the repository.
2. Create and activate a virtual environment in the cloned project.
3. Initialize the database.
4. Run the server.

```bash
$ git clone git@github.com:adwylie/simple-hangman.git
$ cd simple-hangman
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ python -c 'from app import db; db.create_all()'
$ FLASK_ENV=development flask run
```


## API Usage

The examples below assume default development server configuration and
execution on the localhost (`127.0.0.1`). Endpoints are listed the order that
they'd most likely be used during game play.

Note that all endpoints consume and output JSON data.

Endpoints which require POST data will validate the sent data. If there is an
error an 'HTTP 400 Bad Request' response will be returned.


#### List all games

The identifiers of all in-progress games will be returned.

If successful this endpoint will return an 'HTTP 200 OK' response.

Note that if no games exist this endpoint will return an empty list instead of
an error.

```
$ curl http://localhost:5000/api/games

[
    "c686c587",
    "499618d7"
]
```

#### Create a game

A new game will be created and returned.

If successful this endpoint will return an 'HTTP 201 Created' response.
Additionally, a 'Location' header will be included in the response indicating
where the created resource can be found.

```
$ curl http://localhost:5000/api/games -X POST

{
    "tries": 0,
    "guesses": [],
    "phrase": "_____",
    "game_over": false,
    "game_won": false,
    "id": "c686c587"
}
```

#### Make a guess

This endpoint allows a client to submit a guess for an in-progress game.

If successful this endpoint will return an 'HTTP 200 OK' response.

An 'HTTP 409 Conflict' response will be returned if this endpoint is called
for any game which is over (either won or lost).

Note that a 'Content-Type' header must be sent with the request.

```
$ curl http://localhost:5000/api/games/c686c587/guesses \
       -X POST -d '{"guess": "e"}' -H "Content-Type: application/json"

{
    "tries": 0,
    "guesses": [
        "e"
    ],
    "phrase": "___e_",
    "game_over": false,
    "game_won": false,
    "id": "c686c587"
}
```

#### Get a game

An in-progress game can be retrieved via this endpoint.

If successful this endpoint will return an 'HTTP 200 OK' response.

```
$ curl http://localhost:5000/api/games/c686c587

{
    "tries": 1,
    "guesses": [
        "o",
        "r",
        "d",
        "e",
        "l"
    ],
    "phrase": "order",
    "game_over": true,
    "game_won": true,
    "id": "c686c587"
}
```

#### Submit your score

If a game is over and has been won the client will be able to submit their
score. This is done by providing a user name to accompany the score.

Also, after the score has been submitted the game will be deleted.

If successful this endpoint will return an 'HTTP 201 Created' response
(indicating creation of the score).

An 'HTTP 409 Conflict' response will be returned if this endpoint is called
for any game which is not over or has been lost.

Note that a 'Content-Type' header must be sent with the request.

```
$ curl http://localhost:5000/api/games/c686c587/score \
       -X POST -d '{"user": "Quentin J."}' -H "Content-Type: application/json"

{
    "id": 6,
    "user": "Quentin J.",
    "score": "1"
}
```

#### Delete a game

If a game is over and was lost it needs to be deleted. A game can also
be deleted at any point before it is over.

If successful this endpoint will return an 'HTTP 204 No Content' response.

```
$ curl -v "http://localhost:5000/api/games/1441f0ed" -X DELETE
```

#### View all scores

The list of scores can be viewed via this endpoint. The endpoint accepts the
query parameters 'offset' and 'limit' which control how many user scores are
returned. If these parameters are not provided then all scores will be
returned.

If successful this endpoint will return an 'HTTP 200 OK' response.

```
$ curl -v "http://127.0.0.1:5000/api/scores"

[
    {
        "user": "ADW",
        "score": "0"
    },
    {
        "user": "Bram",
        "score": "0"
    },
    {
        "user": "ADW",
        "score": "1"
    },
    {
        "user": "Quentin J.",
        "score": "1"
    },
    {
        "user": "Quentin J.",
        "score": "1"
    },
    {
        "user": "ADW",
        "score": "3"
    }
]
```
