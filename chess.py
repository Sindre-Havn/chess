import numpy as np
import copy

"""
## TO DO ##

- Turn ChessBoard. into self.

- move lines:
        self.self.pos_to_be_taken_by_en_pessant = True
        self.white_did_previous_2step_pawn_move = None
  into pawn class

"""

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
    board = None
    length = None
    width = None
    white_turn = True
    white_did_previous_2step_pawn_move = None
    pos_to_be_taken_by_en_pessant = None
    
    @classmethod
    def piece_at(cls, pos):
        return cls.board[pos.y][pos.x]

class ChessGame(ChessBoard):
    def __init__(self):
        self.pieces = {'♚':7, '♛':8, '♜':9,
                       '♝':1, '♞':1, '♟':Pawn()} # '♙'
        self.white_in_check = False
        self.black_in_check = True

    def no_winner(self):
        return True
    
    def valid_input(self, inp) -> bool:
        if (   len(inp) == 5 and inp[0].isalpha() and inp[1].isnumeric() and
            inp[2].isspace() and inp[3].isalpha() and inp[4].isnumeric()):
  
            if (    97 <= ord(inp[0]) and ord(inp[0]) < 97 + ChessBoard.width
                and  1 <= int(inp[1]) and int(inp[1]) <= ChessBoard.length
                and 97 <= ord(inp[3]) and ord(inp[3]) < 97 + ChessBoard.width
                and  1 <= int(inp[4]) and int(inp[4]) <= ChessBoard.length):
                return True
        return False
    
    def input_move(self):
        while True:
            inp = input('Please enter move: ')
            if self.valid_input(inp):
                old_idx, new_idx = inp.split() # Exmpl: C2 C3 -> 6,2 4,2
                old_pos = Pos(ord(old_idx[0].lower())-97, ChessBoard.length-int(old_idx[1]))
                if (        ChessBoard.piece_at(old_pos)
                    and ord(ChessBoard.piece_at(old_pos)) >= 9812+6*ChessBoard.white_turn
                    and ord(ChessBoard.piece_at(old_pos)) <= 9817+6*ChessBoard.white_turn):
                    break
                print('Not right piece!')
        new_pos = Pos(ord(new_idx[0].lower())-97, ChessBoard.length-int(new_idx[1]))
        return old_pos, new_pos
    
    def move(self):
        if ChessBoard.pos_to_be_taken_by_en_pessant and ChessBoard.white_did_previous_2step_pawn_move == ChessBoard.white_turn:
            ChessBoard.pos_to_be_taken_by_en_pessant = None
            print(ChessBoard.pos_to_be_taken_by_en_pessant)
        while True:
            old_pos, new_pos = self.input_move()
            icon = ChessBoard.piece_at(old_pos)
            print(icon)
            if not icon: continue
            print('try', chr(ord(icon) + 6*(1-ChessBoard.white_turn)), ord(icon))
            print('rev', chr(ord(icon)))
            piece = self.pieces[chr(ord(icon)+6*(1-ChessBoard.white_turn))] # 9823->9823 9817->9823
            if piece.is_valid_move(old_pos, new_pos):
                self.rearrange_board(old_pos, new_pos, icon)
                print('Printing board:\n')
                self.print_board()
                break
            print('Invalid move')
    
    def rearrange_board(self, old_pos, new_pos, icon):
        """Move piece on board and check for pawn promotion."""
        ChessBoard.board[old_pos.y][old_pos.x] = ''
        if icon in '♙♟' and new_pos.y == ChessBoard.length-1-ChessBoard.white_turn*7:
            while True:
                inp = input('Enter a single letter  Q R B N  to promote pawn: ').lower()
                if len(inp) == 1 and inp in 'qrbn':
                    break
            icon = chr(9813 + 'qrbn'.index(inp) + ChessBoard.white_turn*6)
        ChessBoard.board[new_pos.y][new_pos.x] = icon
    
    def print_board(self):
        output = ''
        row_count = 0
        for row in ChessBoard.board:
            output += str(ChessBoard.length - row_count) + ' '
            for piece in row:
                output += piece + ' '
            output += '\n'
            row_count += 1
        output += '  '
        for i in range(ChessBoard.width):
            output += chr(65+i) + ' '
        print(output)


class Pawn:
    def __init__(self):
        pass

    def is_valid_move(self, old_pos, new_pos) -> bool:
        """Check if valid pawn move and remove enemy pawn when doing en pessant"""
        if old_pos.y - new_pos.y == 2*ChessBoard.white_turn-1 and abs(new_pos.x - old_pos.x) == 1:
            if ChessBoard.piece_at(new_pos):
                return True
            if ChessBoard.pos_to_be_taken_by_en_pessant and not ChessBoard.piece_at(new_pos):
                rmv_pos = old_pos.cadd(-1,0)
                if (ChessBoard.piece_at(rmv_pos) == chr(9823-ChessBoard.white_turn*6)):
                    rmv_pos = old_pos.cadd(-1,0)
                    ChessBoard.board[rmv_pos.y][rmv_pos.x] = ''
                    return True
                rmv_pos = old_pos.cadd(1,0)
                if (ChessBoard.piece_at(rmv_pos) == chr(9823-ChessBoard.white_turn*6)):
                    ChessBoard.board[rmv_pos.y][rmv_pos.x] = ''
                    return True
        if new_pos.x == old_pos.x and not ChessBoard.piece_at(new_pos):
            if old_pos.y-new_pos.y == 2*ChessBoard.white_turn-1:
                return True
            if ( old_pos.y == 1+ChessBoard.white_turn*(ChessBoard.length-3) and old_pos.y-new_pos.y == -2+4*ChessBoard.white_turn and
                    not ChessBoard.piece_at(old_pos.cadd(0,1-2*ChessBoard.white_turn)) ):
                ChessBoard.white_did_previous_2step_pawn_move = True if ChessBoard.white_turn else False
                ChessBoard.pos_to_be_taken_by_en_pessant = new_pos
                return True
        return False


def main():
    board_array = [['♖', '♘', '♗', '♕', '♔', '♗', '♘', '♖'], 
                  ['♙', '♙', '♙', '♙', '♙', '♙', '♙', '♙'], 
                  [  '',   '',   '',  '',   '',   '',   '',  ''], 
                  [  '',   '',   '',  '',   '',   '♙',   '',  ''], 
                  [  '',   '',   '♟',  '',   '',   '',   '',  ''], 
                  [  '',   '',   '',  '',   '',   '',   '',  ''], 
                  ['♟', '♟', '♟', '♟', '♟', '♟', '♟', '♟'], 
                  ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜']]
 
    ChessBoard.board  = board_array
    ChessBoard.length = len(board_array)
    ChessBoard.width  = len(board_array[0])
    Chess = ChessGame()
    while Chess.no_winner():
        print('Whites turn:', ChessBoard.white_turn)
        Chess.move()
        ChessBoard.white_turn = not ChessBoard.white_turn
        print(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
    if Chess.white_turn:
        print('Black won!')
    else:
        print('White won!')


if __name__ == '__main__':
    main()