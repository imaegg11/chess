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

    def __init__(self, boardSetup):
        self.dimensions = pygame.display.get_surface().get_size()
        self.boardSetup = boardSetup
        self.board = [[None for i in range(8)] for i in range(8)]
        self.offSetW = (self.dimensions[0] - (self.dimensions[1] - 100)) / 2
        self.offSetH = 50
        self.boardSize = self.dimensions[1] - 100
        self.squareSize = self.boardSize // 8
        self.currentSelectedPiece = [None, None]
        self.currentMover = -1
        self.lastPieceMoved = [None, None]
        self.boardColor = [[(235, 210, 185) if i % 2 == 1 else (161, 111, 92) for i in range(i,i+8)] for i in range(1,9)]
        self.whitePieces = []
        self.blackPieces = []
        self.pastMoves = {boardSetup: 1}
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
        self.botDepth = None
        self.reversed = [0, 8, 1]
        self.secondColorLayer = [[None for i in range(8)] for i in range(8)]

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

        ranks = self.boardSetup.split("/")
        for i in range(len(ranks)):
            temp = []
            for j in range(len(ranks[i])):
                if ord(ranks[i][j]) - ord('0') >= 0 and ord(ranks[i][j]) - ord('0') <= 9:
                    temp.append("".join([" " for i in range(int(ranks[i][j]))]))
                else:
                    temp.append(ranks[i][j])
            ranks[i] = "".join(temp)

        for i in range(len(ranks)):
            for j in range(len(ranks[i])):
                self.board[i][j] = copy.copy(pieceLookUpTable[ranks[i][j]])
                self.board[i][j].x = i
                self.board[i][j].y = j

        self.keepTrack()
        self.botThread.start()

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

    def gameResult(self):
        pieces = self.whitePieces if self.currentMover == -1 else self.blackPieces
        otherPieces = self.blackPieces if self.currentMover == -1 else self.whitePieces
        noLegalMoves = True
        check = False

        if self.currentMover == 1 and self.Wtime < 0:
            return 3
        elif self.currentMover == -1 and self.Btime < 0:
            return 4

        fenString = self.toFEN().split(" ")[0]
        if fenString not in self.pastMoves:
            self.pastMoves[fenString] = 1
        else:
            self.pastMoves[fenString] += 1

        if self.pastMoves[fenString] == 3:
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
        self.drawStockFishLevel()

    def drawStockFishLevel(self):
        myfont = pygame.font.SysFont("Trebuchet MS", int(self.squareSize * 0.5))
        stockfishText = myfont.render(f"Stockfish Level: {self.botDepth}", True, (255, 255, 255))
        stockfishCenter = stockfishText.get_rect()
        stockfishCenter.center = ((self.dimensions[0] - self.boardSize)/4, self.dimensions[1]/2)
        screen.blit(stockfishText, stockfishCenter)


    def drawBoard(self):
        self.updateDimensions()
        for i in range(self.reversed[0], self.reversed[1], self.reversed[2]):
            for j in range(8):
                locationY = self.offSetH + ((i + 8) if i < 0 else i) * self.squareSize
                k = (i * -1 - 1) if i < 0 else i

                square = pygame.Rect(self.offSetW + j * self.squareSize, locationY, self.squareSize, self.squareSize)
                pygame.draw.rect(screen, self.boardColor[k][j] , square)
                if self.secondColorLayer[k][j] != None:
                    pygame.draw.rect(screen, self.secondColorLayer[k][j] , square)
                if self.board[k][j].color != 0:
                    screen.blit(self.board[k][j].returnPiece(), (self.offSetW + j * self.squareSize, locationY))
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
        self.secondColorLayer = [[None for i in range(8)] for i in range(8)]

    def resetLegalMoves(self):
        self.boardColor = [[(235, 210, 185) if i % 2 == 1 else (161, 111, 92) for i in range(i,i+8)] for i in range(1,9)]

    def addLegalMoves(self, legalMoves):
        for i in legalMoves:
            self.boardColor[i[0]][i[1]] = (64, 143, 190) if i[0] % 2 != i[1] % 2 else (91, 170, 215)

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
                match gameResult:
                    case 3:
                        print("black won by timeout")
                    case 4:
                        print("white won by timeout")
                self.isGameRunning = False

    def endOfTurn(self, i , j):

        self.resetSecondLayerColours()
        self.secondColorLayer[self.currentSelectedPiece[0]][self.currentSelectedPiece[1]] = (191, 154, 94) if self.currentSelectedPiece[0] % 2 != self.currentSelectedPiece[1] % 2 else (211, 199, 121)
        self.secondColorLayer[i][j] = (191, 154, 94) if i % 2 != j % 2 else (211, 199, 121)

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
        gameResult = self.gameResult()
        if gameResult != -1:
            match gameResult:
                case 0:
                    print("white won" if self.currentMover == 1 else "black won")
                case 1:
                    print("stalemate")
                case 2:
                    print("draw - three fold repitition")
                case 3:
                    print("black won by timeout")
                case 4:
                    print("white won by timeout")
            self.isGameRunning = False

    def clickTile(self, x, y):
        for i in range(self.reversed[0], self.reversed[1], self.reversed[2]):
            for j in range(8):
                k = (i * -1 - 1) if i < 0 else i
                if x > self.offSetW + j * self.squareSize and y > self.offSetH + ((i + 8) if i < 0 else i) * self.squareSize and x < self.offSetW + (j+1) * self.squareSize and y < self.offSetH + ((i + 8) if i < 0 else i) * self.squareSize + self.squareSize:
                    if self.currentSelectedPiece == [None, None] and self.board[k][j].color != 0 and self.board[k][j].color == self.currentMover:
                        self.currentSelectedPiece = [k, j]
                        legalMoves = self.board[self.currentSelectedPiece[0]][self.currentSelectedPiece[1]].findLegalMoves(self.board, self.lastPieceMoved)[0]
                        self.addLegalMoves(legalMoves)
                        if self.timeOfStartOfMove == 0:
                            self.timeOfStartOfMove = int(time.time() * 1000)
                            self.isGameRunning = True
                    elif [k, j] == self.currentSelectedPiece:
                        legalMoves = self.board[self.currentSelectedPiece[0]][self.currentSelectedPiece[1]].findLegalMoves(self.board, self.lastPieceMoved)[0]
                        self.currentSelectedPiece = [None, None]
                        self.resetLegalMoves()
                    elif self.board[k][j].color == self.currentMover:
                        self.resetLegalMoves()
                        self.currentSelectedPiece = [k, j]
                        legalMoves = self.board[self.currentSelectedPiece[0]][self.currentSelectedPiece[1]].findLegalMoves(self.board, self.lastPieceMoved)[0]
                        self.addLegalMoves(legalMoves)
                    elif self.currentSelectedPiece != [None, None] and self.board[k][j].color != self.currentMover:
                        legalMoves = self.board[self.currentSelectedPiece[0]][self.currentSelectedPiece[1]].findLegalMoves(self.board, self.lastPieceMoved)[0]
                        if [k, j] in legalMoves:
                            prevPieceData = self.board[self.currentSelectedPiece[0]][self.currentSelectedPiece[1]]
                            if prevPieceData.piece == 1:
                                prevPieceData.enPassant(self.board, self.lastPieceMoved, k, j)
                            elif prevPieceData.piece == 6:
                                prevPieceData.castling(self.board, k, j)
                            self.board[k][j] = piece(prevPieceData.color, prevPieceData.piece, k, j, self.squareSize, prevPieceData.numberOfMoves + 1)
                            self.board[self.currentSelectedPiece[0]][self.currentSelectedPiece[1]] = piece(0, 1, 0, 0, self.squareSize, 0)
                            if self.board[k][j].piece == 1:
                                self.board[k][j].promotion()
                            self.endOfTurn(k, j)

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
                #print(end-start)

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
        if self.botActive:
            if self.currentMover != self.botColor:
                if clicked:
                    self.clickTile(x, y)
            else:
                if self.timeOfStartOfMove == 0:
                    self.timeOfStartOfMove = int(time.time() * 1000)
                    self.isGameRunning = True
                if self.botPaused:
                    self.resume()
        elif clicked:
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
        except:
            config({}).throwErrorMesssage(f"FileNotFoundError: Config.json file was not found at location {path}config.json")
            self.endThread()
            sys.exit()
    
    def convertConfigParams(self, configs):
        self.botActive, self.botColor, self.prevBtime, self.prevWtime, self.botDepth = configs
        self.Btime, self.Wtime = self.prevBtime, self.prevWtime
        if self.botActive and self.botColor == -1:
            self.reversed = [-8, 0, 1]
        
        self.bot.stockfish.set_depth = self.botDepth


run = True

board = board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
#board = board("7k/44/8/3P4/8/5K2/3p4/8")
#board = board("2k1r2r/ppp2ppR/8/8/8/8/8/4K3")
#board = board("k7/R3b3/8/8/R7/8/8/R3K2R")
board.setUpBoard()
board.readConfigs()



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
        else:
            board.manageTurn(-1, -1, False)

    board.drawTimeControls()


    pygame.display.update()
    #run = False
