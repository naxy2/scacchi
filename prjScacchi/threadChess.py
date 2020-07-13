import chess
import pygame as py
import random
import threading

lato = 60

r = py.transform.scale(py.image.load("pezzi/torre_nera.png")    , (lato,lato))
n = py.transform.scale(py.image.load("pezzi/cavallo_nero.png")  , (lato,lato))
b = py.transform.scale(py.image.load("pezzi/alfiere_nero.png")  , (lato,lato))
q = py.transform.scale(py.image.load("pezzi/regina_nera.png")   , (lato,lato))
k = py.transform.scale(py.image.load("pezzi/re_nero.png")       , (lato,lato))
p = py.transform.scale(py.image.load("pezzi/pedone_nero.png")   , (lato,lato))

R = py.transform.scale(py.image.load("pezzi/torre_bianca.png")  , (lato,lato))
N = py.transform.scale(py.image.load("pezzi/cavallo_bianco.png"), (lato,lato))
B = py.transform.scale(py.image.load("pezzi/alfiere_bianco.png"), (lato,lato))
Q = py.transform.scale(py.image.load("pezzi/regina_bianca.png") , (lato,lato))
K = py.transform.scale(py.image.load("pezzi/re_bianco.png")     , (lato,lato))
P = py.transform.scale(py.image.load("pezzi/pedone_bianco.png") , (lato,lato))

immagini = [r, n, b, q, k, p, R, N, B, Q, K, P]
lettere = ['r', 'n', 'b', 'q', 'k', 'p', 'R', 'N', 'B', 'Q', 'K', 'P']


chiaro = (255,255,255)
scuro = (100,100,100)

schermo = py.display.set_mode((lato*8, lato*8))
py.display.set_caption("Scacchi")

board = chess.Board()

class prugna:
    def __init__(self, alpha, beta):
        self.alpha  = alpha
        self.beta = beta

def evaluate(board):
    if board.result() == "1-0":
        return 1000
    elif board.result() == "0-1":
        return -1000
    else:
        pezzi = list(board.fen().split(' ')[0])
        val = 0
        val += pezzi.count('P')*1
        val += pezzi.count('R')*5
        val += pezzi.count('N')*3
        val += pezzi.count('B')*3
        val += pezzi.count('Q')*9
        val += pezzi.count('K')*100
        val -= pezzi.count('p')*1
        val -= pezzi.count('r')*5
        val -= pezzi.count('n')*3
        val -= pezzi.count('b')*3
        val -= pezzi.count('q')*9
        val -= pezzi.count('k')*100
        return val

def comp(mv):
    return len(mv.uci())

def comp2(mv):
    cl = mv[1].color_at(mv[0].to_square)
    if (cl != None):
        return 0
    else:
        return len(mv[0].uci())

def minimax(position, depth, alpha, beta, maximizingPlayer):
    if (depth == 0) | position.is_game_over():
        return (evaluate(position), None)

    if maximizingPlayer:
        maxEval = -999
        mossa = None
        childs = random.sample(list(position.legal_moves), position.legal_moves.count())
        #childs = list(position.legal_moves)
        tmp = [(mos, position, maximizingPlayer) for mos in childs]
        tmp.sort(key=comp2)
        childs = [ele[0] for ele in tmp]
        #childs.sort(key=comp)

        for child in childs:
            newPosition = position.copy()
            newPosition.push(child)
            eval = minimax(newPosition, depth-1, alpha, beta, False)[0]
            if (eval > maxEval):
                maxEval = eval
                mossa = child

            alpha = max(alpha, eval)
            if beta <= alpha:
                return (maxEval, mossa)
        return (maxEval, mossa)

    else:
        minEval = 999
        mossa = None
        childs = random.sample(list(position.legal_moves), position.legal_moves.count())
        #childs = list(position.legal_moves)
        childs.sort(key=comp)

        for child in childs:
            newPosition = position.copy()
            newPosition.push(child)
            eval = minimax(newPosition, depth-1, alpha, beta, True)[0]
            if (eval < minEval):
                minEval  = eval
                mossa = child

            beta = min(beta, eval)
            if (beta<= alpha):
                return (minEval, mossa)
        return (minEval, mossa)

def pos_to_square(pos):
    let = ['a','b','c','d','e','f','g','h']
    x = int(pos[0]/lato)
    y = int(pos[1]/lato)
    return let[x]+str(8-y)


def disegna(schermo, board, colorati):
    schermo.fill(scuro)
    for i in range(8):
        for j in range(4):
            py.draw.rect(schermo, chiaro, py.Rect(i*lato, ((j*2)+(i%2))*lato, lato, lato))
    for colorato in colorati:
        x = colorato.to_square%8
        y = int(colorato.to_square/8)
        if (board.color_at(x+y*8) == None) | (board.color_at(x+y*8) == board.turn):
            py.draw.rect(schermo, (0,255,0), py.Rect((x * lato, (7-y) * lato, lato, lato)), 5)
        else:
            py.draw.rect(schermo, (255,0,0), py.Rect((x * lato, (7-y) * lato, lato, lato)), 5)

    pezzi = board.fen()

    i = 0
    j = 0
    while pezzi[i] != ' ':
        pezzo = pezzi[i]
        if pezzo == '/':
            pass
        elif (pezzo.isnumeric()):
            j+=int(pezzo)
        else:
            img = immagini[lettere.index(pezzo)]
            x = j%8
            y = int(j/8)
            schermo.blit(img, (x*lato, y*lato))
            j+=1

        i+=1

    py.display.update()


aspetta = True
run = True
sel = None
raggiungibili = []
while run:
    turno = board.turn

    for evento in py.event.get():
        if evento.type == py.QUIT:
            run = False
            aspetta = False
        elif evento.type == py.MOUSEBUTTONDOWN:
            pos = py.mouse.get_pos()
            square = pos_to_square(pos)
            numPos = chess.SQUARE_NAMES.index(square)
            pezzo = board.piece_at(numPos)

            if sel == None:
                if pezzo != None:   #se non hai premuto a vuoto
                    if pezzo.symbol().isupper() == turno:   #se hai premuto su un pezzo del tuo colore
                        sel = square
                        for legale in list(board.legal_moves):
                            if legale.from_square == numPos:
                                raggiungibili.append(legale)

            else:
                lista = [raggiungibile.to_square for raggiungibile in raggiungibili]
                if lista.__contains__(numPos):  #se selezioni una destinazione valida
                    try:
                        board.push_uci(sel + square)
                    except:
                        board.push_uci(sel+ square + "q")

                sel = None
                raggiungibili = []


    if not turno:
        lista = []
        for mossa in list(board.legal_moves):
            nb = board.copy()
            nb.push(mossa)

            mossa = minimax(board, 4, -999, 999, board.turn)[1]
            board.push(mossa)


    if board.is_game_over() | board.is_insufficient_material():
        print("Vincono i  bianchi") if turno else print("vincono i neri")
        run = False


    disegna(schermo, board, raggiungibili)


while aspetta:
    for evento in py.event.get():
        if evento.type == py.QUIT:
            aspetta = False
    disegna(schermo, board, [])

