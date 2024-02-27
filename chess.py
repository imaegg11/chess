import pygame, sys, time, threading, copy, json, os
from timeit import timeit
from pygame.locals import *
from engine import engine 
from piece import piece
from config import config

'''

Holy crap does all of the following code suck. I will refactor the code later.

'''

pygame.init()

assetsPath = os.path.dirname(os.path.abspath(__file__)) + "\\assets\\"
path = os.path.dirname(os.path.abspath(__file__)) + "\\"
screen = pygame.display.set_mode((900, 500), pygame.RESIZABLE)
pygame.display.set_caption('Chess')
iconImg = pygame.image.load(assetsPath + "blackRook.png")
pygame.display.set_icon(iconImg)

class board():

    def __init__(self):
        self.dimensions = pygame.display.get_surface().get_size()
        self.boardSetup = None
        self.board = [[None for i in range(8)] for i in range(8)]
        self.offSetW = (self.dimensions[0] - (self.dimensions[1] - 100)) / 2
        self.offSetH = 50
        self.boardSize = self.dimensions[1] - 100
        self.squareSize = self.boardSize // 8
        self.currentSelectedPiece = [None, None]
        self.currentMover = -1
        self.lastPieceMoved = [None, None]
        self.boardColor = [[(235, 210, 185) if i % 2 == 1 else (161, 111, 92) for i in range(i,i+8)] for i in range(1,9)]
        self.secondColorLayer = [[None for i in range(8)] for i in range(8)]
        self.legalMovesLayer = [[None for i in range(8)] for i in range(8)]
        self.whitePieces = []
        self.blackPieces = []
        self.pastMovesDict = {}
        self.pastMoves = []
        self.pastColors = []
        self.pastIndex = 0
        self.timeOfStartOfMove = 0
        self.prevBtime = None
        self.prevWtime = None
        self.Btime = None
        self.Wtime = None
        self.numberOfFullmoves = 0
        self.bot = engine()
        self.isGameRunning = False
        self.botThread = threading.Thread(target=self.recieveAndUpdateBotMove)
        self.botLock = threading.Condition(threading.Lock())
        self.botPaused = True
        self.exit = False
        self.botActive = None
        self.botColor = None
        self.botELO = None
        self.reversed = [0, 8, 1]
        self.gameResultText = ""
        self.botThread.start()
        self.fiftyRuleMove = 0
        self.autoFlip = True
        self.blackTimeIncrement = 0
        self.whiteTimeIncrement = 0       

    def setUpBoard(self):

        pieceLookUpTable = {
            ' ': piece(0, 1, 0, 0, self.squareSize, 0),
            'P': piece(-1, 1, 0, 0, self.squareSize, 0),
            'N': piece(-1, 2, 0, 0, self.squareSize, 0),
            'B': piece(-1, 3, 0, 0, self.squareSize, 0),
            'R': piece(-1, 4, 0, 0, self.squareSize, 0),
            'Q': piece(-1, 5, 0, 0, self.squareSize, 0),
            'K': piece(-1, 6, 0, 0, self.squareSize, 0),
            'p': piece(1, 1, 0, 0, self.squareSize, 0),
            'n': piece(1, 2, 0, 0, self.squareSize, 0),
            'b': piece(1, 3, 0, 0, self.squareSize, 0),
            'r': piece(1, 4, 0, 0, self.squareSize, 0),
            'q': piece(1, 5, 0, 0, self.squareSize, 0),
            'k': piece(1, 6, 0, 0, self.squareSize, 0)
        }

        ranks = self.boardSetup.split("/")[:-1]
        for i in range(len(ranks)):
            temp = []
            for j in range(len(ranks[i])):
                if ord(ranks[i][j]) - ord('0') >= 0 and ord(ranks[i][j]) - ord('0') <= 9:
                    temp.append("".join([" " for i in range(int(ranks[i][j]))]))
                else:
                    temp.append(ranks[i][j])
            ranks[i] = "".join(temp)

        try:
            for i in range(len(ranks)):
                for j in range(len(ranks[i])):
                    self.board[i][j] = copy.copy(pieceLookUpTable[ranks[i][j]])
                    self.board[i][j].x = i
                    self.board[i][j].y = j
        except:
            config({}).throwErrorMesssage(f"Board in config.json is invalid")
            return

        self.keepTrack()
        self.currentMover = int(self.boardSetup.split("/")[-1])
        if self.currentMover == 1:
            self.reversed = [-8, 0, 1]
        else:
            self.reversed = [0, 8, 1]

        self.pastMovesDict = {self.boardSetup: 1}
        self.pastMoves = [self.copyBoard(self.board)]
        self.pastColors = [[[None for i in range(8)] for i in range(8)]]

    @staticmethod 
    def copyBoard(board):
        copyOfBoard = [[None for i in range(8)] for i in range(8)]

        for i in range(8):
                for j in range(8):
                    copyOfBoard[i][j] = copy.copy(board[i][j])

        return copyOfBoard

    '''

    def loadingScreen(self):
        myfont = pygame.font.SysFont("monospace", 40)
        loadingText = myfont.render("Loading...", True, (255, 255, 255))

        loadingTextCenter = loadingText.get_rect()
        loadingTextCenter.center = (450, 250)

        screen.blit(loadingText, loadingTextCenter)

    '''

    def keepTrack(self):
        self.whitePieces = []
        self.blackPieces = []
        for i in range(8):
            for j in range(8):
                if self.board[i][j].color == -1:
                    self.whitePieces += [self.board[i][j]]
                elif self.board[i][j].color == 1:
                    self.blackPieces += [self.board[i][j]]

    def toFEN(self):
        lookUpTable = {
            -1: "P",
            -2: "N",
            -3: "B",
            -4: "R",
            -5: "Q",
            -6: "K",
            1: "p",
            2: "n",
            3: "b",
            4: "r",
            5: "q",
            6: "k"
        }

        emptySquares = 0
        fenString = ""

        blackKing = self.board[0][4]
        whiteKing = self.board[7][4]
        rWhiteRook = self.board[7][0]
        lWhiteRook = self.board[7][7]
        rBlackRook = self.board[0][0]
        lBlackRook = self.board[0][7]
        castlingRights = [
            "Q" if whiteKing.numberOfMoves == 0 and whiteKing.piece == 6 and rWhiteRook.piece == 4 and rWhiteRook.color == whiteKing.color and rWhiteRook.numberOfMoves == 0 else "-",
            "K" if whiteKing.numberOfMoves == 0 and whiteKing.piece == 6 and lWhiteRook.piece == 4 and lWhiteRook.color == whiteKing.color and lWhiteRook.numberOfMoves == 0 else "-",
            "q" if blackKing.numberOfMoves == 0 and blackKing.piece == 6 and rBlackRook.piece == 4 and rBlackRook.color == blackKing.color and rBlackRook.numberOfMoves == 0 else "-",
            "k" if blackKing.numberOfMoves == 0 and blackKing.piece == 6 and lBlackRook.piece == 4 and lBlackRook.color == blackKing.color and lBlackRook.numberOfMoves == 0 else "-",
        ]
        lastPieceMoved = self.board[self.lastPieceMoved[0]][self.lastPieceMoved[1]] if self.lastPieceMoved != [None, None] else None
        enPassantable = True if self.lastPieceMoved != [None, None] and lastPieceMoved.numberOfMoves == 1 and lastPieceMoved.piece == 1 and lastPieceMoved.x == (3 if lastPieceMoved.color == 1 else 4) else False
        for i in self.board:
            for j in i:
                if j.color == 0:
                    emptySquares += 1
                else:
                    if emptySquares != 0:
                        fenString += str(emptySquares)
                        emptySquares = 0
                    fenString += lookUpTable[j.piece * j.color]
            if emptySquares != 0:
                fenString += str(emptySquares)
                emptySquares = 0
            fenString += "/"
        fenString = fenString[:-1]
        fenString += f' {"b" if self.currentMover == 1 else "w"}'
        fenString += f' {"-" if all([i == "-" for i in castlingRights]) else "".join([i for i in castlingRights if i != "-"])}'
        if self.lastPieceMoved != [None, None]:
            fenString += f' {chr(97+self.lastPieceMoved[1]) + str(self.lastPieceMoved[0]) if enPassantable else "-"}'
        else:
            fenString += " -"
        fenString += " 0"
        fenString += f' {self.numberOfFullmoves}'
        return fenString

    def checkIfPositionIsDrawn(self, pieces, otherPieces):
        
        '''
        
        Yes, I am creating an entirely seperate function just to check if the position is drawn by insufficient material
        Yes, this is using Lichess' implementation of determining whether a position is a draw
        Yes, this means that some position will be awarded unfairly
        No, I do not care
        
        '''

        piecesNum = [i.piece for i in pieces if i.piece != 6]
        otherPiecesNum = [i.piece for i in otherPieces if i.piece != 6]

        for i in pieces:
            if i.piece == 1 or i.piece == 4 or i.piece == 5:
                return False
        
        
        if len(set(piecesNum)) > 1:
            return False
        if piecesNum.count(2) > 1:
            return False
        if piecesNum == [2] and 5 not in otherPiecesNum and len(otherPiecesNum) != 0:
            return False
        if piecesNum == [3] and 3 not in otherPiecesNum and 4 not in otherPiecesNum and 5 not in otherPiecesNum and len(otherPiecesNum) != 0:
            return False
        if (piecesNum + otherPiecesNum).count(3) > 1:
            allPieces = pieces + otherPieces
            coloursOfBishops = set()
            for i in allPieces:
                if i.piece == 3:
                    coloursOfBishops.add(1 if i.x % 2 != i.y % 2 else 0)

            if len(coloursOfBishops) == 2:
                return False

        return True

    def gameResult(self):
        pieces = self.whitePieces if self.currentMover == -1 else self.blackPieces
        otherPieces = self.blackPieces if self.currentMover == -1 else self.whitePieces
        noLegalMoves = True
        check = False

        if self.currentMover == 1 and self.Wtime < 0:
            if self.checkIfPositionIsDrawn(self.whitePieces if self.currentMover == -1 else self.blackPieces, self.blackPieces if self.currentMover == -1 else self.whitePieces):
                return 5
            return 3
        elif self.currentMover == -1 and self.Btime < 0:
            if self.checkIfPositionIsDrawn(self.whitePieces if self.currentMover == -1 else self.blackPieces, self.blackPieces if self.currentMover == -1 else self.whitePieces):
                return 5
            return 4

        fenString = self.toFEN().split(" ")[0]
        if fenString not in self.pastMovesDict:
            self.pastMovesDict[fenString] = 1
        else:
            self.pastMovesDict[fenString] += 1

        self.pastMoves += [self.copyBoard(self.board)]
        self.pastIndex = len(self.pastMoves) - 1 

        if self.pastMovesDict[fenString] == 3:
            return 2

        for i in pieces:
            if len(i.findLegalMoves(self.board, self.lastPieceMoved)[0]) != 0:
                noLegalMoves = False
                break
        if noLegalMoves:
            for i in otherPieces:
                i.recursionStopper = False
                if (i.findLegalMoves(self.board, self.lastPieceMoved)[1]):
                    check = True
                    i.recursionStopper = True
                    break
                i.recursionStopper = True

        if noLegalMoves == True:
            if check == True:
                return 0
            else:
                return 1

        if self.checkIfPositionIsDrawn(self.whitePieces if self.currentMover == 1 else self.blackPieces, self.blackPieces if self.currentMover == 1 else self.whitePieces) == self.checkIfPositionIsDrawn(pieces, otherPieces) == True:
            return 5 

        if self.fiftyRuleMove == 100:
            return 6

        return -1

    def updateDimensions(self):
        self.dimensions = pygame.display.get_surface().get_size()
        self.offSetW = (self.dimensions[0] - (self.dimensions[1] - 100)) / 2
        self.offSetH = 50
        self.boardSize = self.dimensions[1] - 100
        self.squareSize = int(self.boardSize / 8)
        for i in self.board:
            for j in i:
                j.size = self.squareSize


    def drawTimeControls(self):
        reversed = (self.reversed != [0, 8, 1])
        myfont = pygame.font.SysFont("Trebuchet MS", int(self.squareSize * 0.65))
        wTime = myfont.render(self.msToString(self.Btime if reversed else self.Wtime), True, (255, 255, 255))
        bTime = myfont.render(self.msToString(self.Wtime if reversed else self.Btime), True, (255, 255, 255))

        wTimeCenter = wTime.get_rect()
        bTimeCenter = bTime.get_rect()

        offSet = (self.dimensions[0] - self.boardSize)/2 + self.boardSize + (self.dimensions[0] - self.boardSize)/4

        wTimeCenter.center = (offSet, self.dimensions[1]/2 + self.dimensions[1]/4)
        bTimeCenter.center = (offSet, self.dimensions[1]/2 - self.dimensions[1]/4)

        screen.blit(wTime, wTimeCenter)
        screen.blit(bTime, bTimeCenter)
        self.drawStockfishELO()
        self.drawGameResult()

    def drawStockfishELO(self):
        myfont = pygame.font.SysFont("Trebuchet MS", int(self.squareSize * 0.5))
        stockfishText = myfont.render(f"Stockfish ELO: {self.botELO if self.botActive else 'N/A'}", True, (255, 255, 255))
        stockfishCenter = stockfishText.get_rect()
        stockfishCenter.center = ((self.dimensions[0] - self.boardSize)/4, self.dimensions[1]/2)
        screen.blit(stockfishText, stockfishCenter)


    def drawGameResult(self):
        myfont = pygame.font.SysFont("Trebuchet MS", int(self.squareSize * 0.4))
        if len(self.gameResultText.split("\n")) == 1:
            gameResultText = myfont.render(self.gameResultText, True, (255, 255, 255))
            gameResultTextCenter = gameResultText.get_rect()
            gameResultTextCenter.center = ((self.dimensions[0] - self.boardSize)/4 * 3 + self.boardSize, self.dimensions[1]/2)
            screen.blit(gameResultText, gameResultTextCenter)
        else:

            # Yes I know this is dumb. Shut up

            gameResultText1 = myfont.render(self.gameResultText.split("\n")[0], True, (255, 255, 255))
            gameResultTextCenter1 = gameResultText1.get_rect()
            gameResultTextCenter1.center = ((self.dimensions[0] - self.boardSize)/4 * 3 + self.boardSize, self.dimensions[1]/2 - self.dimensions[1]/50)
            screen.blit(gameResultText1, gameResultTextCenter1)
            gameResultText2 = myfont.render(self.gameResultText.split("\n")[1], True, (255, 255, 255))
            gameResultTextCenter2 = gameResultText2.get_rect()
            gameResultTextCenter2.center = ((self.dimensions[0] - self.boardSize)/4 * 3 + self.boardSize, self.dimensions[1]/2 + self.dimensions[1]/50)
            screen.blit(gameResultText2, gameResultTextCenter2)


    def drawBoard(self):
        self.updateDimensions()
        self.board = self.copyBoard(self.pastMoves[self.pastIndex])
        for i in range(self.reversed[0], self.reversed[1], self.reversed[2]):
            k = (i * -1 - 1) if i < 0 else i
            for j in range(self.reversed[0], self.reversed[1], self.reversed[2]):
                n = (j * -1 - 1) if j < 0 else j                
                locationY = self.offSetH + ((i + 8) if i < 0 else i) * self.squareSize
                square = pygame.Rect(self.offSetW + n * self.squareSize, locationY, self.squareSize, self.squareSize)
                pygame.draw.rect(screen, self.boardColor[k][n] , square)
                if self.currentSelectedPiece == [k, n]:
                    pygame.draw.rect(screen, (204, 77, 69) if k % 2 != n % 2 else (242, 120, 114), square)
                if self.pastColors[self.pastIndex][k][n] != None:
                    pygame.draw.rect(screen, self.pastColors[self.pastIndex][k][n] , square)
                if self.legalMovesLayer[k][n] != None:
                    pygame.draw.rect(screen, self.legalMovesLayer[k][n] , square)
                if self.board[k][n                                                                                                                                                                                                              ].color != 0:
                    screen.blit(self.board[k][n].returnPiece(), (self.offSetW + n * self.squareSize, locationY))
                    #self.board[i][j].returnPiece(self.offSetW + j * self.squareSize, self.offSetH + i * self.squareSize)
        #self.renderLegalMoves()


    '''
    Not in use anymore. Kept here just in case I do need it in the future

    def renderLegalMoves(self):
        for i in range(8):
            for j in range(8):
                if self.boardCircles[i][j] == 1:
                    centerW = self.squareSize * j + self.offSetW + self.squareSize / 2
                    centerH = self.squareSize * i + self.offSetH + self.squareSize / 2
                    color = (235, 210, 185) if self.boardColor[i][j] == (161, 111, 92) else (161, 111, 92)
                    pygame.draw.circle(screen, color, (centerW, centerH), self.squareSize/5)
    '''

    def resetSecondLayerColours(self):
        self.secondColorLayer = [[None for j in range(8)] for i in range(8)]

    def resetLegalMoves(self):
        self.legalMovesLayer = [[None for j in range(8)] for i in range(8)]

    def addLegalMoves(self, legalMoves):
        for i in legalMoves:
            self.legalMovesLayer[i[0]][i[1]] = (64, 143, 190) if i[0] % 2 != i[1] % 2 else (91, 170, 215)

    def msToString(self, time):
        hour = time//3600000
        minute = time%3600000//60000
        seconds = (time%3600000)%60000//1000
        milliseconds = time%1000

        timeInString = f'{"0" * (2-len(str(hour)))}{hour}:{"0" * (2-len(str(minute)))}{minute}:{"0" * (2-len(str(seconds)))}{seconds}.{"0" * (3-len(str(milliseconds)))}{milliseconds}'
        return timeInString

    def timer(self):
        if self.isGameRunning:
            if self.currentMover == -1:
                currentTime = int(time.time() * 1000)
                self.Wtime = self.prevWtime - (currentTime - self.timeOfStartOfMove)
            else:
                currentTime = int(time.time() * 1000)
                self.Btime = self.prevBtime - (currentTime - self.timeOfStartOfMove)

            if self.Wtime < 0 or self.Btime < 0:
                self.currentMover *= -1
                gameResult = self.gameResult()

                if self.Wtime < 0:
                    self.Wtime = 0
                else:
                    self.Btime = 0

                match gameResult:
                    case 3:
                        self.gameResultText = "Black Won By Timeout"
                    case 4:
                        self.gameResultText = "White Won By Timeout"
                    case 5:
                        self.gameResultText = "Draw\nInsufficient Material"

                self.isGameRunning = False

    def endOfTurn(self, i , j):

        self.resetSecondLayerColours()
        self.secondColorLayer[self.currentSelectedPiece[0]][self.currentSelectedPiece[1]] = (191, 154, 94) if self.currentSelectedPiece[0] % 2 != self.currentSelectedPiece[1] % 2 else (211, 199, 121)
        self.secondColorLayer[i][j] = (191, 154, 94) if i % 2 != j % 2 else (211, 199, 121)
        self.pastColors += [self.secondColorLayer.copy()]

        if self.currentMover == 1:
            self.numberOfFullmoves += 1

        if self.currentMover == -1:
            self.prevWtime = self.Wtime
        else:
            self.prevBtime = self.Btime
        self.currentMover = self.currentMover * -1

        self.timeOfStartOfMove = int(time.time() * 1000)
        self.currentSelectedPiece = [None, None]
        self.lastPieceMoved = [i, j]
        self.resetLegalMoves()
        self.keepTrack()

        otherPieces = self.blackPieces if self.currentMover == -1 else self.whitePieces
        pieces = self.whitePieces if self.currentMover == -1 else self.blackPieces

        for i in otherPieces:
            i.recursionStopper = False
            if (i.findLegalMoves(self.board, self.lastPieceMoved)[1]):
                for j in pieces:
                    if j.piece == 6:
                        self.secondColorLayer[j.x][j.y] = [234, 79, 79]
                i.recursionStopper = True
                break
            i.recursionStopper = True

        gameResult = self.gameResult()
        if gameResult != -1:
            match gameResult:
                case 0:
                    self.gameResultText = "Checkmate By White" if self.currentMover == 1 else "Checkmate By Black"
                case 1:
                    self.gameResultText = "Stalemate"
                case 2:
                    self.gameResultText = "Draw - Three\nFold Repitition"
                case 5:
                    self.gameResultText = "Draw\nInsufficient Material"
                case 6:
                    self.gameResultText = "Draw\nFifty Rule Move"
            self.isGameRunning = False
            return
        
        if self.currentMover == -1:
            self.Btime += self.blackTimeIncrement
            self.prevBtime = self.Btime
        else:
            self.Wtime += self.whiteTimeIncrement
            self.prevWtime = self.Wtime

        if not self.botActive and self.autoFlip:
            if self.currentMover == 1:
                self.reversed = [-8, 0, 1]
            else:
                self.reversed = [0, 8, 1]

    def clickTile(self, x, y):
        for i in range(self.reversed[0], self.reversed[1], self.reversed[2]):
            k = (i * -1 - 1) if i < 0 else i
            for j in range(self.reversed[0], self.reversed[1], self.reversed[2]):
                n = (j * -1 - 1) if j < 0 else j
                if x > self.offSetW + n * self.squareSize and y > self.offSetH + ((i + 8) if i < 0 else i) * self.squareSize and x < self.offSetW + (n+1) * self.squareSize and y < self.offSetH + ((i + 8) if i < 0 else i) * self.squareSize + self.squareSize:
                    if self.currentSelectedPiece == [None, None] and self.board[k][n].color != 0 and self.board[k][n].color == self.currentMover:
                        self.currentSelectedPiece = [k, n]
                        legalMoves = self.board[self.currentSelectedPiece[0]][self.currentSelectedPiece[1]].findLegalMoves(self.board, self.lastPieceMoved)[0]
                        self.addLegalMoves(legalMoves)
                        if self.timeOfStartOfMove == 0:
                            self.timeOfStartOfMove = int(time.time() * 1000)
                            self.isGameRunning = True
                    elif [k, n] == self.currentSelectedPiece:
                        # legalMoves = self.board[self.currentSelectedPiece[0]][self.currentSelectedPiece[1]].findLegalMoves(self.board, self.lastPieceMoved)[0]
                        self.currentSelectedPiece = [None, None]
                        self.resetLegalMoves()
                    elif self.board[k][n].color == self.currentMover:
                        self.resetLegalMoves()
                        self.currentSelectedPiece = [k, n]
                        legalMoves = self.board[self.currentSelectedPiece[0]][self.currentSelectedPiece[1]].findLegalMoves(self.board, self.lastPieceMoved)[0]
                        self.addLegalMoves(legalMoves)
                    elif self.currentSelectedPiece != [None, None] and self.board[k][n].color != self.currentMover:
                        legalMoves = self.board[self.currentSelectedPiece[0]][self.currentSelectedPiece[1]].findLegalMoves(self.board, self.lastPieceMoved)[0]
                        if [k, n] in legalMoves:
                            prevPieceData = self.board[self.currentSelectedPiece[0]][self.currentSelectedPiece[1]]
                            if prevPieceData.piece == 1 or self.board[k][n].color != 0:
                                self.fiftyRuleMove = 0
                            else:
                                self.fiftyRuleMove += 1
                            if prevPieceData.piece == 1:
                                prevPieceData.enPassant(self.board, self.lastPieceMoved, k, n)
                            elif prevPieceData.piece == 6:
                                prevPieceData.castling(self.board, k, n)
                            self.board[k][n] = piece(prevPieceData.color, prevPieceData.piece, k, n, self.squareSize, prevPieceData.numberOfMoves + 1)
                            self.board[self.currentSelectedPiece[0]][self.currentSelectedPiece[1]] = piece(0, 1, 0, 0, self.squareSize, 0)
                            if self.board[k][n].piece == 1:
                                self.board[k][n].promotion(screen)
                            self.endOfTurn(k, n)

    def recieveAndUpdateBotMove(self):
        while True:

            with self.botLock:
                while self.botPaused:
                    self.botLock.wait()

                if self.exit:
                    break

                start = time.time()

                self.bot.updateStockFishPosition(self.toFEN())
                botMove = self.bot.getAndFormatBestMove()
                self.currentSelectedPiece = [botMove[0], botMove[1]]
                prevPieceData = self.board[botMove[0]][botMove[1]]

                if prevPieceData.piece == 1 or self.board[botMove[2]][botMove[3]].color != 0:
                    self.fiftyRuleMove = 0
                else:
                    self.fiftyRuleMove += 1

                if prevPieceData.piece == 1:
                    prevPieceData.enPassant(self.board, self.lastPieceMoved, botMove[2], botMove[3])
                elif prevPieceData.piece == 6:
                    prevPieceData.castling(self.board, botMove[2], botMove[3])

                self.board[botMove[2]][botMove[3]] = piece(prevPieceData.color, prevPieceData.piece, botMove[2], botMove[3], self.squareSize, prevPieceData.numberOfMoves + 1)
                self.board[botMove[0]][botMove[1]] = piece(0, 1, 0, 0, self.squareSize, 0)

                if self.board[botMove[2]][botMove[3]].piece == 1 and len(botMove) == 5:
                    self.board[botMove[2]][botMove[3]].piece = botMove[-1]
                    self.board[botMove[2]][botMove[3]].updatePieceImg()



                self.endOfTurn(botMove[2], botMove[3])
                
                end = time.time()
                #self.gameResultText = end-start)

                self.pause()
            #time.sleep(0.1)
    '''

    I have no clue on how nor why the following two function works.
    They were provided by our soon to be overlord, Chat-GPT.
    Apparently getting rid of acquire() and lock() and adding with made everything work.
    I still have no clue on what acquire(), lock() or with does.
    I will find out soon tm.

    '''

    def pause(self):
        self.botPaused = True

    def resume(self):
        with self.botLock:
            self.botPaused = False
            self.botLock.notify()

    def endThread(self):
        board.exit = True
        board.resume()

    def manageTurn(self, x, y, clicked):
        if self.isGameRunning or self.timeOfStartOfMove == 0:
            if self.botActive:
                if self.currentMover != self.botColor:
                    if clicked:
                        self.clickTile(x, y)
                elif self.isGameRunning:
                    if self.timeOfStartOfMove == 0:
                        self.timeOfStartOfMove = int(time.time() * 1000)
                        self.isGameRunning = True
                    if self.botPaused:
                        self.resume()
            elif clicked:
                self.pastIndex = len(self.pastMoves)-1 
                self.clickTile(x, y)
    
    def readConfigs(self):
        try:
            with open(path + "config.json") as configFile:
                configInfo = json.loads(configFile.read())
                configClass = config(configInfo)
                if configClass.checkConfig() == False:
                    self.endThread()
                    sys.exit()
                else:
                    self.convertConfigParams(configClass.parseConfigs())
        except FileNotFoundError:
            config({}).throwErrorMesssage(f"FileNotFoundError: Config.json file was not found at location {path}config.json")
            self.endThread()
            sys.exit()
    
    def convertConfigParams(self, configs):
        self.botActive, self.botColor, self.prevBtime, self.prevWtime, self.botELO, self.autoFlip, self.blackTimeIncrement, self.whiteTimeIncrement, self.boardSetup = configs
        self.Btime, self.Wtime = self.prevBtime, self.prevWtime
        if self.botActive and self.botColor == -1:
            self.reversed = [-8, 0, 1]
        
        # Problem... Not sure how skill level works... so I just set it to the rating divided by 100 floored
        # Probably won't break anything... right...?

        self.bot.stockfish.update_engine_parameters({
            "UCI_Elo": self.botELO
        })

    def reset(self):

        # Makes sure the entire program doesn't die
        while (self.botActive and self.currentMover == self.botColor):
            pass
        
        self.botPaused = True
        self.dimensions = pygame.display.get_surface().get_size()
        self.board = [[None for i in range(8)] for i in range(8)]
        self.offSetW = (self.dimensions[0] - (self.dimensions[1] - 100)) / 2
        self.offSetH = 50
        self.boardSize = self.dimensions[1] - 100
        self.squareSize = self.boardSize // 8
        self.currentSelectedPiece = [None, None]
        self.currentMover = -1
        self.lastPieceMoved = [None, None]
        self.secondColorLayer = [[None for i in range(8)] for i in range(8)]
        self.legalMovesLayer = [[None for i in range(8)] for i in range(8)]
        self.whitePieces = []
        self.blackPieces = []
        self.pastMovesDict = {self.boardSetup: 1}
        self.pastMoves = []
        self.pastColors = []
        self.pastIndex = 0
        self.timeOfStartOfMove = 0
        self.prevBtime = None
        self.prevWtime = None
        self.Btime = None
        self.Wtime = None
        self.numberOfFullmoves = 0
        self.isGameRunning = False
        self.gameResultText = ""    
        self.fiftyRuleMove = 0

        self.readConfigs()
        self.setUpBoard()

    def resign(self):

        copyOfBoard = [[None for i in range(8)] for i in range(8)]
        copyOfsecondColorLayer = copy.copy(self.secondColorLayer)

        for i in range(8):
            for j in range(8):
                copyOfBoard[i][j] = copy.copy(self.board[i][j])

        while (self.botActive and self.currentMover == self.botColor):
            pass 

        self.secondColorLayer = copyOfsecondColorLayer
        self.legalMovesLayer = [[None for i in range(8)] for i in range(8)]
        self.board = copyOfBoard

        self.drawBoard()

        self.pause()
        self.isGameRunning = False
        
        if self.botActive:
            self.gameResultText = "Black Wins By\nResignation" if self.botColor == 1 else "White Wins By\nResignation"
        else:
            self.gameResultText = "Black Wins By\nResignation" if self.currentMover == -1 else "White Wins By\nResignation"

    def viewOtherPosition(self, type):
        
        self.currentSelectedPiece = [None, None]
        self.resetLegalMoves()
        match type:
            case 1:
                self.pastIndex = min(self.pastIndex+1, len(self.pastMoves)-1)
            case 2:
                self.pastIndex = max(self.pastIndex-1, 0)
            case 3:
                self.pastIndex = len(self.pastMoves)-1 
            case 4:
                self.pastIndex = 0

run = True

board = board()

board.readConfigs()
board.setUpBoard()


try:
    while run:

        screen.fill((31, 31, 31))

        board.drawBoard()
        board.timer()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                board.endThread()
                #pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #x, y = pygame.mouse.get_pos()
                #board.clickTile(x, y, 0)
                # TODO: IMPLEMENT DRAGGING LATER
                pass
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                board.manageTurn(x, y, True)
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                if width/height < 1.8:
                    width = height * 1.8
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == 120:
                    board.reversed = [-8, 0, 1] if board.reversed != [-8, 0, 1] else [0, 8, 1]
                elif event.key == 114:
                    board.reset()
                elif event.key == 115 and board.botActive and board.timeOfStartOfMove == 0 and board.botColor == -1:
                    board.isGameRunning = True
                elif event.key == 113 and board.isGameRunning:
                    board.resign()
                elif event.key == 1073741903: # Right
                    board.viewOtherPosition(1)
                elif event.key == 1073741904: # Left
                    board.viewOtherPosition(2)
                elif event.key == 1073741906: # Up
                    board.viewOtherPosition(3)
                elif event.key == 1073741905: # Down
                    board.viewOtherPosition(4)
            board.manageTurn(-1, -1, False)

        board.drawTimeControls()


        pygame.display.update()

except Exception as e:
    print(e)
    board.endThread()
    sys.exit()
