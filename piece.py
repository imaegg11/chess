import pygame, copy, os

class piece():
    def __init__(self, color, piece, x, y, size, numberOfMoves):

        self.lookUpTable = {
            1: "Pawn",
            2: "Knight",
            3: "Bishop",
            4: "Rook",
            5: "Queen",
            6: "King",
        }
        self.color = color
        self.piece = piece
        self.x = x
        self.y = y
        self.size = size
        self.path = path = os.path.dirname(os.path.abspath(__file__)) + "\\assets\\"
        self.pieceImg = pygame.transform.scale(pygame.image.load(self.path + ("white" if color == -1 else "black") + self.lookUpTable[piece] + ".png").convert_alpha(), (size, size))
        self.numberOfMoves = numberOfMoves
        self.lastPieceMoved = [None, None]
        self.recursionStopper = True
        self.enPassantTry = False

    def updatePieceImg(self):
        self.pieceImg = pygame.transform.scale(pygame.image.load(self.path + ("white" if self.color == -1 else "black") + self.lookUpTable[self.piece] + ".png").convert_alpha(), (self.size, self.size))

    def returnPiece(self):
        if self.color != 0:
            self.updatePieceImg()
            return self.pieceImg

    def findLegalMoves(self, board, lastPieceMoved):
        self.lastPieceMoved = lastPieceMoved
        legalMoves = []
        results = None
        if self.piece == 1:
            results = [self.pawnMoves(board, lastPieceMoved)]
            legalMoves = results[0][0]
        elif self.piece == 2:
            results = [self.knightMoves(board)]
            legalMoves = results[0][0]
        elif self.piece == 3:
            results = [self.bishopMoves(board)]
            legalMoves = results[0][0]
        elif self.piece == 4:
            results = [self.rookMoves(board)]
            legalMoves = results[0][0]
        elif self.piece == 5:
            results = [self.rookMoves(board), self.bishopMoves(board)]
            legalMoves = results[0][0] + results[1][0]
        elif self.piece == 6:
            results = [self.kingMoves(board)]
            legalMoves = results[0][0]

        return legalMoves, any([results[i][1] for i in range(len(results))])

    def pawnMoves(self, board, lastPieceMoved):
        legalMoves = []
        kingInPath = False

        if int((self.color + 1) * 3.5) == self.x:
            return [legalMoves, kingInPath]

        results = self.checkValidMove(self.x + self.color, self.y, legalMoves, board)
        legalMoves = results[0]
        if kingInPath == False:
            kingInPath = results[2]

        if self.numberOfMoves == 0 and int((self.color+2) * -2.5 + 8.5) == self.x and legalMoves != []:
            results = self.checkValidMove(self.x + self.color * 2, self.y, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False: kingInPath = results[2]


        if self.y != 7:
            results = self.checkValidMove(self.x + self.color, self.y + 1, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False: kingInPath = results[2]
        if self.y != 0:
            results = self.checkValidMove(self.x + self.color, self.y - 1, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False: kingInPath = results[2]

        # God dammit en passant

        if self.y != 7 and board[self.x][self.y+1].color == (self.color * -1) and [self.x, self.y+1] == lastPieceMoved and board[self.x][self.y+1].piece == 1 and board[self.x][self.y+1].numberOfMoves == 1 and board[self.x][self.y+1].x == int((self.color + 2)*0.5 + 2.5):
            self.enPassantTry = True
            results = self.checkValidMove(self.x + self.color, self.y+1, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False: kingInPath = results[2]
            self.enPassantTry = False
        if self.y != 0 and board[self.x][self.y-1].color == (self.color * -1) and [self.x, self.y-1] == lastPieceMoved and board[self.x][self.y-1].piece == 1 and board[self.x][self.y-1].numberOfMoves == 1 and board[self.x][self.y-1].x == int((self.color + 2)*0.5 + 2.5):
            self.enPassantTry = True
            results = self.checkValidMove(self.x + self.color, self.y-1, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False: kingInPath = results[2]
            self.enPassantTry = False

        return [legalMoves, kingInPath]

    def promotion(self):
        if int((self.color + 1) * 3.5) == self.x:
            print("what to promote to????\n2 for knight\n3 for bishop\n4 for rook\n5 for queen")
            promotion = int(input())
            if promotion > 5 or promotion < 2:
                self.promotion()
            else:
                self.piece = promotion
                self.pieceImg = pygame.transform.scale(pygame.image.load(("white" if self.color == -1 else "black") + self.lookUpTable[self.piece] + ".png").convert_alpha(), (self.size, self.size))

    def enPassant(self, board, lastPieceMoved, x, y):
        if self.y != 7 and x == self.x + self.color and self.y+1 == y and board[self.x][self.y+1].x == int((self.color + 2)*0.5 + 2.5) and board[self.x][self.y+1].color == (self.color * -1) and [self.x, self.y+1] == lastPieceMoved and board[self.x][self.y+1].piece == 1 and board[self.x][self.y+1].numberOfMoves == 1:
            board[self.x][self.y+1] = piece(0, 1, 0, 0, self.size, 0)
        if self.y != 0 and x == self.x + self.color and self.y-1 == y and  board[self.x][self.y-1].x == int((self.color + 2)*0.5 + 2.5) and board[self.x][self.y-1].color == (self.color * -1) and [self.x, self.y-1] == lastPieceMoved and board[self.x][self.y-1].piece == 1 and board[self.x][self.y-1].numberOfMoves == 1:
            board[self.x][self.y-1] = piece(0, 1, 0, 0, self.size, 0)

    def knightMoves(self, board):
        legalMoves = []
        kingInPath = False
        possibleMoves = [[1, 2], [2, 1], [2, -1], [1, -2], [-1, -2], [-2, -1], [-2, 1], [-1, 2]]
        for i in possibleMoves:
            x = i[0] + self.x
            y = i[1] + self.y
            if x > 7 or x < 0 or y > 7 or y < 0:
                continue
            results = self.checkValidMove(x, y, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False:
                kingInPath = results[2]

        return [legalMoves, kingInPath]

    def bishopMoves(self, board):
        legalMoves = []
        kingInPath = False
        for i in range(self.x-1, -1, -1):
            j = self.y - (self.x - i)
            if j < 0:
                break
            results = self.checkValidMove(i, j, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False: kingInPath = results[2]
            if results[1] == 1:
                break
        for i in range(self.x-1, -1, -1):
            j = self.y + (self.x - i)
            if j > 7:
                break
            results = self.checkValidMove(i, j, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False: kingInPath = results[2]
            if results[1] == 1:
                break
        for i in range(self.x+1, 8):
            j = self.y + (i - self.x)
            if j > 7:
                break
            results = self.checkValidMove(i, j, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False: kingInPath = results[2]
            if results[1] == 1:
                break
        for i in range(self.x+1, 8):
            j = self.y - (i - self.x)
            if j < 0:
                break
            results = self.checkValidMove(i, j, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False: kingInPath = results[2]
            if results[1] == 1:
                break

        return [legalMoves, kingInPath]

    def rookMoves(self, board):
        legalMoves = []
        kingInPath = False
        for i in range(self.x-1, -1, -1):
            results = self.checkValidMove(i, self.y, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False: kingInPath = results[2]
            if results[1] == 1:
                break
        for i in range(self.x+1, 8):
            results = self.checkValidMove(i, self.y, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False: kingInPath = results[2]
            if results[1] == 1:
                break
        for i in range(self.y-1, -1, -1):
            results = self.checkValidMove(self.x, i, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False: kingInPath = results[2]
            if results[1] == 1:
                break
        for i in range(self.y+1, 8):
            results = self.checkValidMove(self.x, i, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False: kingInPath = results[2]
            if results[1] == 1:
                break

        return [legalMoves, kingInPath]

    def kingMoves(self, board):
        legalMoves = []
        kingInPath = False
        possibleMoves = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
        for i in possibleMoves:
            x = i[0] + self.x
            y = i[1] + self.y
            if x > 7 or x < 0 or y > 7 or y < 0:
                continue
            results = self.checkValidMove(x, y, legalMoves, board)
            legalMoves = results[0]
            if kingInPath == False:
                kingInPath = results[2]

        otherPiece = self.keepTrack(board)[0 if self.color == 1 else 1]

        '''
        I spent 1h+ trying to get this piece of code to work only to realize that a. I had already
        written a piece of function for this and b. the reason why this doesn't work is because
        while writing which color to fetch for the otherPiece variable, I had acciendently fetched
        the same color pieces instead of the opposite color pieces. My sanity is no longer exists.

        for i in otherPiece:
            i.recursionStopper = False
            if i.piece != 6:
                isKingInCheck.append(i.findLegalMoves(board, self.lastPieceMoved)[1])
            i.recursionStopper = True

        if any(isKingInCheck):
            return [legalMoves, kingInPath]
        '''

        if self.check(board, otherPiece, 6):
            return [legalMoves, kingInPath]

        if self.numberOfMoves == 0 and self.y == 4:
            leftRook = board[self.x][self.y+3]
            rightRook = board[self.x][self.y-4]
            copyOfLegalMoves = copy.copy(legalMoves)
            if leftRook.piece == 4 and leftRook.color == self.color and leftRook.numberOfMoves == 0 and all([board[self.x][self.y+i].color == 0 for i in range(1, 3)]):
                results = self.checkValidMove(self.x, self.y+1, legalMoves, board)
                if results[0] != copyOfLegalMoves:
                    results = self.checkValidMove(self.x, self.y+2, legalMoves, board)
                    legalMoves = results[0]
            if rightRook.piece == 4 and rightRook.color == self.color and rightRook.numberOfMoves == 0 and all([board[self.x][self.y-i].color == 0 for i in range(1, 4)]):
                results = self.checkValidMove(self.x, self.y-1, legalMoves, board)
                if results[0] != copyOfLegalMoves:
                    results = self.checkValidMove(self.x, self.y-2, legalMoves, board)
                    legalMoves = results[0]

        return [legalMoves, kingInPath]

    def castling(self, board, x, y):
        if self.numberOfMoves == 0 and self.y == 4:
            leftRook = board[self.x][self.y+3]
            rightRook = board[self.x][self.y-4]
            if leftRook.piece == 4 and leftRook.color == self.color and leftRook.numberOfMoves == 0 and all([board[self.x][self.y+i].color == 0 for i in range(1, 3)]) and x == self.x and y == self.y+2:
                board[self.x][self.y+1] = piece(self.color, 4, self.x, self.y+1, self.size, 1)
                leftRook.color = 0
            if rightRook.piece == 4 and rightRook.color == self.color and rightRook.numberOfMoves == 0 and all([board[self.x][self.y-i].color == 0 for i in range(1, 4)]) and x == self.x and y == self.y-2:
                board[self.x][self.y-1] = piece(self.color, 4, self.x, self.y-1, self.size, 1)
                rightRook.color = 0

    def keepTrack(self, board):
        whitePieces = []
        blackPieces = []
        for i in range(8):
            for j in range(8):
                if board[i][j].color == -1:
                    whitePieces += [board[i][j]]
                elif board[i][j].color == 1:
                    blackPieces += [board[i][j]]
        return whitePieces, blackPieces

    def checkValidMove(self, i, j, legalMoves, board):

        if self.recursionStopper:

            copyOfBoard = [[None for i in range(8)] for i in range(8)]
            tempWhitePieces = []
            tempBlackPieces = []

            for a in range(8):
                for b in range(8):
                    copyOfBoard[a][b] = copy.copy(board[a][b])

            if copyOfBoard[i][j].color != self.color:
                prevPieceData = copyOfBoard[self.x][self.y]
                copyOfBoard[i][j] = piece(self.color, prevPieceData.piece, i, j, self.size, prevPieceData.numberOfMoves + 1)
                copyOfBoard[self.x][self.y].color = 0
            elif copyOfBoard[i][j].color == self.color:
                return legalMoves, 1, False

            results = self.keepTrack(copyOfBoard)
            tempWhitePieces = results[0]
            tempBlackPieces = results[1]

            if self.check(copyOfBoard, tempWhitePieces if self.color == 1 else tempBlackPieces, -1) == False:
                if board[i][j].color == self.color:
                    return legalMoves, 1, False
                elif board[i][j].color == (self.color*-1):
                    if self.piece == 1 and j == self.y:
                        return legalMoves, 1, False
                    legalMoves.append([i, j])
                    if board[i][j].piece == 6:
                        return legalMoves, 1, True
                    return legalMoves, 1, False
                elif self.piece == 1 and self.x != i and self.y != j and self.enPassantTry == False:
                    return legalMoves, 1, False
                legalMoves.append([i, j])
                return legalMoves, 0, False
            else:
                if board[i][j].color == self.color:
                    return legalMoves, 1, False
                elif board[i][j].color == (self.color*-1):
                    if self.piece == 1 and j == self.y:
                        return legalMoves, 1, False
                    if board[i][j].piece == 6:
                        return legalMoves, 1, True
                    return legalMoves, 1, False
                elif self.piece == 1 and self.x != i and self.y != j and self.enPassantTry == False:
                    return legalMoves, 1, False
                return legalMoves, 0, False

        else:
            if board[i][j].color == self.color:
                return legalMoves, 1, False
            elif board[i][j].color == (self.color*-1):
                if self.piece == 1 and j == self.y:
                    return legalMoves, 1, False
                legalMoves.append([i, j])
                if board[i][j].piece == 6:
                    return legalMoves, 1, True
                return legalMoves, 1, False
            elif self.piece == 1 and self.x != i and self.y != j and self.enPassantTry == False:
                return legalMoves, 1, False
            legalMoves.append([i, j])
            return legalMoves, 0, False

    def check(self, board, pieces, kingCheck):
        for i in pieces:
            i.recursionStopper = False
            if i.piece != kingCheck and i.findLegalMoves(board, self.lastPieceMoved)[1] == True:
                i.recursionStopper = True
                return True
            i.recursionStopper = True
        return False