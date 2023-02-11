import numpy as np
import copy


class Pos:
    """ Index of 2D array. Top left corner is (0,0)"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, x, y):
        self.x += x
        self.y += y
        return self
    
    def cadd(self, x, y):
        """Return a copy of the object after an add"""
        return copy.copy(self).add(x,y)
    
    def p(self):
        print(self.x, self.y)


class ChessBoard:
    def __init__(self, board_array):
        self.board = board_array
        self.length = len(board_array)
        self.width = len(board_array[0])
        self.white_turn = True
        self.possible_en_pessant = True
    
    def piece_at(self, pos):
        return self.board[pos.y][pos.x]

class ChessGame(ChessBoard):
    def __init__(self, board_array):
        super().__init__(board_array)
        self.pieces = {'♔':1, '♕':2, '♖':3,
                       '♗':4, '♘':5, '♙':Pawn(board_array, False),
                       '♚':7, '♛':8, '♜':9,
                       '♝':1, '♞':1, '♟':Pawn(board_array, True)}
        self.white_in_check = False
        self.black_in_check = True

    def no_winner(self):
        return True
    
    def valid_input(self, inp) -> bool:
        if (   len(inp) == 5 and inp[0].isalpha() and inp[1].isnumeric() and
            inp[2].isspace() and inp[3].isalpha() and inp[4].isnumeric()):
                          
            if (    97 <= ord(inp[0]) and ord(inp[0]) < 97 + self.width
                and  1 <= int(inp[1]) and int(inp[1]) <= self.length
                and 97 <= ord(inp[3]) and ord(inp[3]) < 97 + self.width
                and  1 <= int(inp[4]) and int(inp[4]) <= self.length):
                return True
        return False
    
    def input_move(self):
        while True:
            inp = input('Please enter move: ')
            if self.valid_input(inp):
                from_idx, to_idx = inp.split() # Exmpl: C2 C3 -> 6,2 4,2
                pos = Pos(ord(from_idx[0].lower())-97, self.length-int(from_idx[1]))
                if (9812+6*self.white_turn <= ord(self.piece_at(pos))
                    and ord(self.piece_at(pos)) <= 9817+6*self.white_turn):
                    break
                print('Not right piece!')
        new_pos = Pos(ord(  to_idx[0].lower())-97, self.length-int(to_idx[1]))
        pos.p()
        new_pos.p()
        return pos, new_pos
    
    def move(self):
        while True:
            pos, new_pos = self.input_move()
            icon = self.piece_at(pos) #self.board[pos.y][pos.x]
            print(icon)
            if not icon: continue
            piece = self.pieces[icon]
            if piece.is_valid_move(pos, new_pos):
                self.rearrange_board(pos, new_pos, icon)
                print('Printing board:\n')
                self.print_board()
                break
            print('Invalid move')
    
    def rearrange_board(self, pos, new_pos, icon):
        """Move piece on board and check for pawn promotion."""
        pos.p()
        new_pos.p()
        self.board[pos.y][pos.x] = ''
        if icon in '♙♟' and new_pos.y == self.length-1-self.white_turn*7:
            while True:
                inp = input('Enter a single letter  Q R B N  to promote pawn: ').lower()
                if len(inp) == 1 and inp in 'qrbn':
                    break
            icon = chr(9813 + 'qrbn'.index(inp) + self.white_turn*6)
        self.board[new_pos.y][new_pos.x] = icon
    
    def print_board(self):
        output = ''
        for row in self.board:
            for piece in row:
                output += piece + '\t'
            output += '\n'
        print(output)


class Pawn(ChessBoard):
    def __init__(self, chess_board, is_white):
        super().__init__(chess_board)
        self.is_white = is_white
    
    def is_valid_move(self, pos, new_pos) -> bool:
        """Check if valid pawn move and remove enemy pawn when doing en pessant"""
        print('white turn:', self.white_turn)
        if pos.y - new_pos.y == 2*self.white_turn-1 and abs(new_pos.x - pos.x) == 1:
            if self.piece_at(new_pos):
                print('attack')
                return True
            if self.possible_en_pessant and not self.piece_at(new_pos):
                rmv_pos = pos.cadd(-1,0)
                if (self.piece_at(rmv_pos) == chr(9823-self.white_turn*6)):
                    rmv_pos = pos.cadd(-1,0)
                    self.board[rmv_pos.y][rmv_pos.x] = ''
                    print('HE', -1)
                    return True
                rmv_pos = pos.cadd(1,0)
                if (self.piece_at(rmv_pos) == chr(9823-self.white_turn*6)):
                    self.board[rmv_pos.y][rmv_pos.x] = ''
                    print('HE', 1)
                    return True
        if new_pos.x == pos.x and not self.piece_at(new_pos):
            print('new_x == x')
            if pos.y-new_pos.y == 2*self.white_turn-1:
                print('single step')
                return True
            print(( pos.y == 1+self.white_turn*(self.length-4), pos.y-new_pos.y == -2+4*self.white_turn,
                    not self.piece_at(pos.cadd(0,1-2*self.white_turn)) ))
            if ( pos.y == 1+self.white_turn*(self.length-4) and pos.y-new_pos.y == -2+4*self.white_turn and
                    not self.piece_at(pos.cadd(0,1-2*self.white_turn)) ):
                self.possible_en_pessant = True
                print('2 step')
                return True
            print('not 2 step')
        return False

        """
        w -> pos.y == 2+self.white_turn*(length-2)

        l=8          2+1*(8-4)
        l=9          2+1*(9-4)
        """
        """
        if self.is_white:
            print('white')
            if pos.y - new_pos.y == 1 and abs(new_pos.x - pos.x) == 1:
                if self.piece_at(new_pos):
                    print('attack')
                    return True
                if self.possible_en_pessant and not self.piece_at(new_pos):
                    rmv_pos = pos.cadd(-1,0)
                    if (2 <= pos.x and self.piece_at(rmv_pos) == chr(9823-self.white_turn*6)): # remove 2 <=
                        rmv_pos = pos.cadd(-1,0)
                        self.board[rmv_pos.y][rmv_pos.x] = ''
                        print('HE', -1)
                        return True
                    rmv_pos = pos.cadd(1,0)
                    if (pos.x <= self.length-1 and self.piece_at(rmv_pos) == chr(9823-self.white_turn*6)): # remove <= length
                        self.board[rmv_pos.y][rmv_pos.x] = ''
                        print('HE', 1)
                        return True
            if new_pos.x == pos.x and not self.piece_at(new_pos):
                print('new_x == x')
                if pos.y-new_pos.y == 1:
                    print('single step')
                    return True
                if ( pos.y == self.length-2 and pos.y-new_pos.y == 2 and
                    not self.piece_at(pos.cadd(0,-1)) ):
                    self.possible_en_pessant = True
                    print('2 step')
                    return True
                print('not 2 step')
        return False
        
        
        """


def main():
    chess_list = [['♖', '♘', '♗', '♕', '♔', '♗', '♘', '♖'], 
                  ['♙', '♙', '♙', '♙', '♙', '♙', '♙', '♙'], 
                  [  '',   '',   '',  '',   '',   '',   '',  ''], 
                  [  '',   '',   '',  '♙',   '♟',   '',   '',  ''], 
                  [  '',   '',   '',  '',   '',   '',   '',  ''], 
                  [  '',   '♞',   '',  '',   '',   '',   '',  ''], 
                  ['♟', '♟', '♟', '♟', '♟', '♟', '♟', '♟'], 
                  ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜']]

    Chess = ChessGame(chess_list)
    while Chess.no_winner():
        print('Whites turn:', Chess.white_turn)
        Chess.move()
        Chess.white_turn = not Chess.white_turn
    if Chess.white_turn:
        print('Black won!')
    else:
        print('White won!')


    """
    if    9812 <= ord(piece) <= 9817:
        white
    elif: 9818 <= ord(piece) <= 9823:
        black
    """


if __name__ == '__main__':
    main()