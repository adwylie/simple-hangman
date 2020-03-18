## Hangman Game

  |======|        A B C D E F G H I J K L M
  | /    !
  |/     O        N O P Q R S T U V W X Y Z
  |    --|--
  |      |        H a _ g m a _   G a m _  
  |     / \
  |               Invalid guess, try again.
=====             Enter your guess: b


### Requirements

- Game play operates as a regular hangman game.

- Placeholders are displayed for unknown letters of a phrase.
- The user can make a guess by selecting a letter.
- If a guess matches an unknown letter, that letter becomes a known letter.
- Known letters are displayed in the phrase instead of placeholders.

- Each guess that does not match an unknown letter counts as a try.
- The game is over (a loss) when the user accumulates five (5) tries.
- The game is over (a win) if all letters of the phrase are known using less that five (5) tries.

- If the user wins they will be congratulated.
- If the user wins their score will be saved.

- Six phrases are possible: '3dhubs', 'marvin', 'print', 'filament', 'order', 'layer'.

- The game can be played by clients using a simple API.
- The game can be played by users using an interface.


### Derived requirements

- The API provided to clients will be REST-ful.
- The interface provided to users will be web-based.

- A list of player scores should be displayed in the game's interface.

- Phrases and guesses are assumed to be alpha-numeric only.
- The case (uppercase/lowercase) of phrases and guesses does not matter.

- Scores are defined as the number of tries to complete the game.
- Leaderboard shows top 10 high scores.

## Deployment

virtualenv

```python
from app import db
db.create_all()
```

export FLASK_ENV=development
