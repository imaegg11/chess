# Python Chess 
## Important Notice
~~Due to my incredible lack of brain cells and will to do it, this bot will only play the best move. It will play the same moves every time given the same position, including in openings. This means that there are 0 variations in the opening. I could probably solve this by creating a large json file of openings and look at that during the opening. However, I am too lazy so that will come later.~~


Nevermind, found a fix to it. It was called using my braincells and not being dumb. 

## Overview

I don't know what you want, it's just chess in Python using pygame. A very bad one as well. 

## How To Use (Not Like Anyone Will But Whatever)

### Requirements
- Python: [Link to Python Website](https://www.python.org/)
- Python Libraries Needed:
  - Pygame: [Link To Pygame Library](https://pypi.org/project/pygame/)
  - Stockfish: [Link To Stockfish Library](https://pypi.org/project/stockfish/)
- Stockfish Engine [Link To Stockfish Download](https://stockfishchess.org/download/)
  - Under Windows, download AVX2 

### Setup
- Find the <>Code button, download the zip file and unzip it on your computer (Main folder should be called chess-main)
- Unzip the Stockfish Engine zip and place it in the chess-main folder (Also the folder that contains all of the code from the github)
- Run chess.py to run the program 

### Configs 
Configs can be found in the config.json file. Settings should be self-explanatory. Time is measured in milliseconds. 

### Controls
- Below are the controls 
  - R: Restarts the game ~~(INVESTIGATING AN ISSUE RIGHT NOW DO NOT USE)~~ It's fixed now??? I didn't even change anything???
  - Q: Resigns the game
  - S: Starts the game if you are playing the engine when it has the white pieces

### Problems
Read the error message. If it is in red, read it and fix the issue. If it's not, cry about it because there's a high likely chance I am not fixing the issue. 

## If You Want To Fix This Program
If you want to fix this program, fork the repository and die while reading my code. It's is horrendous and it is probably the worst code you will ever read. I forgot how half the code works. Also enjoy the comments while you are at it. 