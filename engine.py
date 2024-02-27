import stockfish, os
# import requests

class engine:

    '''
    
    Switched to stockfish elo system...
    Not sure if it works...
    
    '''

    def __init__(self):
        self.stockfish = stockfish.Stockfish(
                path=os.path.dirname(os.path.abspath(__file__)) + "\\" + "stockfish\stockfish-windows-x86-64-avx2.exe"
            )

        self.fenString = ""

    def updateStockFishPosition(self, fenString):
        self.stockfish.set_fen_position(fenString)
        self.fenString = fenString

    def getAndFormatBestMove(self):

        lookUpTable = {
            'p': 1,
            'n': 2,
            'b': 3,
            'r': 4,
            'q': 5
        }

        bestMove = [i for i in self.stockfish.get_best_move()]
        bestMove[0], bestMove[2] = ord(bestMove[0])-97, ord(bestMove[2])-97
        if len(bestMove) == 5:
            bestMove[-1] = lookUpTable[bestMove[-1]]
        bestMove = [int(i) for i in bestMove]
        bestMove[1], bestMove[3] = bestMove[1] * -1 + 8, bestMove[3] * -1 + 8
        bestMove[0], bestMove[1], bestMove[2], bestMove[3] = bestMove[1], bestMove[0], bestMove[3], bestMove[2]
        return bestMove
    
    '''

    Was going to use this.
    Decided I didn't want to anymore.
    Left here cause I am lazy.

    def getAndFormatBestMoveWeb(self):
        lookUpTable = {
            'p': 1,
            'n': 2,
            'b': 3,
            'r': 4,
            'q': 5
        }

        response = requests.get(f'https://www.chessdb.cn/cdb.php?action=querybest&board={self.fenString}')
        
        bestMove[0], bestMove[2] = ord(bestMove[0])-97, ord(bestMove[2])-97
        if len(bestMove) == 5:
            bestMove[-1] = lookUpTable[bestMove[-1]]
        bestMove = [int(i) for i in bestMove]
        bestMove[1], bestMove[3] = bestMove[1] * -1 + 8, bestMove[3] * -1 + 8
        bestMove[0], bestMove[1], bestMove[2], bestMove[3] = bestMove[1], bestMove[0], bestMove[3], bestMove[2]
        return bestMove

    '''