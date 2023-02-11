import copy

# Unicode chess symbols: https://qwerty.dev/chess-symbols-to-copy-and-paste/

### TO DO

# if king cant move, then check the rest of this turns pieces
# tak into account the king cant move at start, so maybe do
# a check on remaining pieces

# rename "old", "new" _idx. Idx is unprecise

# patt:
# for piece on board:
#   if piece can move: break
#
# check if same position 3 times

# check_mate func
# could be solved by:
# - only check surounding if in check
#   (only call func if in check)

# replace 98XX with piece: ord('♕') etc


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


class ChessGame:
    def __init__(self, board):
        self.board  = board
        self.length = len(board)
        self.width  = len(board[0])
        self.white_turn = False #True
        self.white_did_previous_2step_pawn_move = None # FIX None
        self.pos_to_be_taken_by_en_pessant = None      # FIX None
        self.valid_move = {'♔':self.king,   '♕':self.queen,  '♖':self.rock,
                           '♗':self.bishop, '♘':self.knight, '♙':self.pawn}
        self.pos_white_king = None
        self.pos_black_king = None
        self.set_pos_of_kings()
        self.white_can_castle_kingside  = (self.pos_white_king.y == self.length-1 and
                                           self.piece_at(Pos(self.width-1, self.length-1)) == '♜')
        self.white_can_castle_queenside = (self.pos_white_king.y == self.length-1 and
                                           self.piece_at(Pos(0, self.length-1)) == '♜')
        self.black_can_castle_kingside  = (self.pos_black_king.y == 0 and
                                           self.piece_at(Pos(self.width-1, 0)) == '♖')
        self.black_can_castle_queenside = (self.pos_black_king.y == 0 and
                                           self.piece_at(Pos(0, 0)) == '♖')
        self.castling_step = 2
        print(self.white_can_castle_kingside, self.white_can_castle_queenside,
              self.black_can_castle_kingside, self.black_can_castle_queenside)
        self.white_in_check = False
        self.black_in_check = False

        """
        1. Sjekker om old_pos er på samme diagonal som kongen
        2. Sjekker om new_pos er langs old_pos-konge-diagonalen; EQ eller NEQ
        top_left_to_bottom_right = True if

        if on diagonal with king and piece is pawn, queen, or bishhop
        3. Telle fra kongen. Finnes det en lagbrikke, return False
           finnes en fiende av type dronning eller løper, return True
        
        """
    
    def set_pos_of_kings(self):
        row_count = 0
        for row in self.board:
            col_count = 0
            for piece in row:
                if ((piece == '♚') and self.pos_white_king) or ((piece == '♔') and self.pos_black_king):
                    raise ValueError(f"Chessgame does not support multiple pieces of type '{piece}' in chessboard array.")
                if piece == '♚':
                    self.pos_white_king = Pos(col_count, row_count)
                elif piece == '♔':
                    self.pos_black_king = Pos(col_count, row_count)
                col_count += 1
            row_count += 1
        if not(self.pos_white_king and self.pos_white_king):
            raise ValueError("Missing unicode character '♚'  or '♔' in chessboard array")

    def move_cause_self_check(self, old_pos, new_pos):
        if self.piece_at(old_pos) == chr(9812+6*self.white_turn): return False
        print('CAUSE SELF CHECK?')
        pos_of_turns_king = self.pos_white_king if self.white_turn else self.pos_black_king
        iter_pos = old_pos.cadd(0,0)
        if abs(pos_of_turns_king.x - old_pos.x) == abs(pos_of_turns_king.y - old_pos.y): # old_pos is on a diagonal axis from the king
            print('Check diagonal')
            print(abs(pos_of_turns_king.x - new_pos.x), abs(pos_of_turns_king.y - new_pos.y))
            if abs(pos_of_turns_king.x - new_pos.x) == abs(pos_of_turns_king.y - new_pos.y):
                if (   ord(self.piece_at(old_pos)) == 9817+6*self.white_turn
                    or ord(self.piece_at(old_pos)) == 9815+6*self.white_turn
                    or ( ord(self.piece_at(old_pos)) == 9813+6*self.white_turn
                    and (pos_of_turns_king.x > old_pos.x) == (pos_of_turns_king.x > new_pos.x)
                    and (pos_of_turns_king.y > old_pos.y) == (pos_of_turns_king.y > new_pos.y) )):
                    return False
            iter_pos = old_pos.cadd(0,0)
            x_step = 1 if pos_of_turns_king.x < old_pos.x else -1
            y_step = 1 if pos_of_turns_king.y < old_pos.y else -1
            for _ in range( min( abs((x_step==1)*(self.width-1)-old_pos.x), abs((y_step==1)*(self.length-1)-old_pos.y) ) ):
                observed_piece = self.piece_at(iter_pos.add(x_step,y_step))
                print('Loop:', observed_piece)
                if not observed_piece: continue
                if (   observed_piece == chr(9819-6*self.white_turn)
                    or observed_piece == chr(9821-6*self.white_turn)):
                    return True
                else: return False
        elif pos_of_turns_king.x == old_pos.x and new_pos.x != old_pos.x:
            print('Checking x-change')
            y_step = 1 if pos_of_turns_king.y < old_pos.y else -1
            for _ in range( abs( old_pos.y - (y_step==1)*(self.length-1) ) ):
                observed_piece = self.piece_at(iter_pos.add(0,y_step))
                print('Loop:', observed_piece)
                if not observed_piece: continue
                if (   observed_piece == chr(9819-6*self.white_turn)
                    or observed_piece == chr(9820-6*self.white_turn)):
                    return True
                else: return False
        elif pos_of_turns_king.y == old_pos.y and new_pos.y != old_pos.y:
            print('Checking y-change')
            x_step = 1 if pos_of_turns_king.x < old_pos.x else -1
            for _ in range( abs( old_pos.x - (x_step==1)*(self.width-1) ) ):
                observed_piece = self.piece_at(iter_pos.add(x_step,0))
                print('Loop:', observed_piece)
                if not observed_piece: continue
                if (   observed_piece == chr(9819-6*self.white_turn)
                    or observed_piece == chr(9820-6*self.white_turn)):
                    return True
                else: return False
        print('End of selfcheck check')
        return False

    def check_mate(self):
        return False
    
    def piece_at(self, pos):
        return self.board[pos.y][pos.x]
    
    def valid_input_format(self, inp) -> bool:
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
            if self.valid_input_format(inp):
                old_idx, new_idx = inp.split()
                old_pos = Pos(ord(old_idx[0].lower())-97, self.length-int(old_idx[1])) # Exmpl: C2 D4 -> 6,2 3,4
                if (        self.piece_at(old_pos)  #  Color of piece = color of turn
                    and ord(self.piece_at(old_pos)) >= 9812+6*self.white_turn
                    and ord(self.piece_at(old_pos)) <= 9817+6*self.white_turn):
                    new_pos = Pos(ord(new_idx[0].lower())-97, self.length-int(new_idx[1]))
                    if (        self.piece_at(new_pos)  #  No color of turn at destination
                        and ord(self.piece_at(new_pos)) >= 9812+6*self.white_turn
                        and ord(self.piece_at(new_pos)) <= 9817+6*self.white_turn):
                        print('Friendly fire is not cool!')
                        continue
                    break
                print('Not right piece!')
        return old_pos, new_pos
    
    def move(self):
        """Moves the piece if the move was legal and resets en pessant possibilitie"""
        while True:
            old_pos, new_pos = self.input_move()
            icon = self.piece_at(old_pos)
            #self.king_in_check() må sjekke om new_pos blokkerer eller om kongen er flyttet
            print(icon)
            if not icon: continue
            piece_type = chr(ord(icon)-6*self.white_turn) # 9823->9823 9817->9823
            if not self.valid_move[piece_type](old_pos, new_pos) or self.move_cause_self_check(old_pos, new_pos):
                print('Invalid move')
                continue
            icon = self.check_special_moves(old_pos, new_pos, icon)
            self.board[new_pos.y][new_pos.x] = icon
            print('Printing board:\n')
            self.draw_board()
            break
    
    def king_in_check(self):
        return self.pos_dangerous(self.pos_white_king if self.white_turn else self.pos_black_king)

    def check_special_moves(self, old_pos, new_pos, icon):
        """Move piece on board and check for pawn promotion."""
        # Reset possibility for en pessant
        if self.pos_to_be_taken_by_en_pessant and self.white_did_previous_2step_pawn_move != self.white_turn:
            self.pos_to_be_taken_by_en_pessant = None

        # Pawn promotion
        self.board[old_pos.y][old_pos.x] = ''
        if icon in '♙♟' and new_pos.y == (not self.white_turn)*(self.length-1): #self.length-1-self.white_turn*(self.length-1)
            while True:
                inp = input('Enter a single letter  Q R B N  to promote pawn: ').lower()
                if len(inp) == 1 and inp in 'qrbn':
                    break
            icon = chr(9813 + 'qrbn'.index(inp) + 6*self.white_turn)
        
        # Remove possibility for castling   # if icon == king or old_pos==rock_pos
        # Remove possibility for castling   #    icon != king or old_pos!=rock_pos   king->false or false     rock->true or false
        if self.white_can_castle_kingside:
            self.white_can_castle_kingside  = (icon != '♚') and not (old_pos.x == self.width-1 and old_pos.y == self.length-1)
        if self.black_can_castle_kingside:
            self.black_can_castle_kingside  = (icon != '♔') and not (old_pos.x == self.width-1 and old_pos.y == 0)
        if self.white_can_castle_queenside:
            self.white_can_castle_queenside = (icon != '♚') and not (old_pos.x == 0 and old_pos.y == self.length-1)
        if self.black_can_castle_queenside:
            self.black_can_castle_queenside = (icon != '♔') and not (old_pos.x == 0 and old_pos.y == 0)

        return icon
    
    def remis(self):
        return False
    
    def play(self):
        self.draw_board()
        while not self.check_mate() and not self.remis():
            print('Whites turn:', self.white_turn)
            self.move()
            self.white_turn = not self.white_turn
        if self.white_turn:
            print('Black won!')
        else:
            print('White won!')
    
    def draw_board(self):
        output = ''
        row_count = 0
        for row in self.board:
            output += str(self.length - row_count) + ' '
            for piece in row:
                if not piece: output += ' '
                output += piece + ' '
            output += '\n'
            row_count += 1
        output += '  '
        for i in range(self.width):
            output += chr(65+i) + ' '
        print(output + '\n')
    
    def pos_dangerous(self, pos):
        return (   self.pos_endangered_by_line(pos)
            or self.pos_endangered_by_diagonal(pos)
            or self.pos_endangered_by_knight(pos)
            or self.pos_endangered_by_king(pos))

    def pos_endangered_by_knight(self, pos):
        if pos.x <= self.width -3 and pos.y >= 1 and self.piece_at(pos.cadd(2,-1)) == chr(9822-6*self.white_turn):
            return True
        if pos.x <= self.width -2 and pos.y >= 2 and self.piece_at(pos.cadd(1,-2)) == chr(9822-6*self.white_turn):
            return True
        if pos.x >= 1 and pos.y >= 2 and self.piece_at(pos.cadd(-1,-2)) == chr(9822-6*self.white_turn):
            return True
        if pos.x >= 2 and pos.y >= 1 and self.piece_at(pos.cadd(-2,-1)) == chr(9822-6*self.white_turn):
            return True
        if pos.x >= 2 and pos.y <= self.length -2 and self.piece_at(pos.cadd(-2,1)) == chr(9822-6*self.white_turn):
            return True
        if pos.x >= 1 and pos.y <= self.length -3 and self.piece_at(pos.cadd(-1,2)) == chr(9822-6*self.white_turn):
            return True
        if pos.x <= self.width -2 and pos.y <= self.length -3 and self.piece_at(pos.cadd(1,2)) == chr(9822-6*self.white_turn):
            return True
        if pos.x <= self.width -3 and pos.y <= self.length -2 and self.piece_at(pos.cadd(2,1)) == chr(9822-6*self.white_turn):
            return True
        return False
        """
        if pos.x <= self.width - 3 and pos.y >= 2: # 6 <= 8 -3 and 5 >= 2
            if ( (self.piece_at(pos.cadd(2,-1)) == chr(9822-6*self.white_turn))
              or (self.piece_at(pos.cadd(1,-2)) == chr(9822-6*self.white_turn)) ):
                return True
        if pos.x >= 2 and pos.y >= 2:
            if ( (self.piece_at(pos.cadd(-1,-2)) == chr(9822-6*self.white_turn))
              or (self.piece_at(pos.cadd(-2,-1)) == chr(9822-6*self.white_turn)) ):
                return True
        if pos.x >= 2 and pos.y <= self.width - 3:
            if ( (self.piece_at(pos.cadd(-2,1)) == chr(9822-6*self.white_turn))
              or (self.piece_at(pos.cadd(-1,2)) == chr(9822-6*self.white_turn)) ):
                return True
        if pos.x >= self.width - 3 and pos.y <= self.width - 3:
            if ( (self.piece_at(pos.cadd(1,2)) == chr(9822-6*self.white_turn))
              or (self.piece_at(pos.cadd(2,1)) == chr(9822-6*self.white_turn)) ):
                return True
        return False
        """
    
    def pos_endangered_by_king(self, pos):
        if pos.y != 0:
            if self.piece_at(pos.cadd(0,-1))  == chr(9818-6*self.white_turn):
                return True
            if (pos.x >= 1 and
                  (self.piece_at(pos.cadd(-1,-1)) == chr(9818-6*self.white_turn)
                or self.piece_at(pos.cadd(-1, 0)) == chr(9818-6*self.white_turn))):
                return True
            if (pos.x <= self.width-2 and
                  (self.piece_at(pos.cadd(1,-1)) == chr(9818-6*self.white_turn)
                or self.piece_at(pos.cadd(1, 0)) == chr(9818-6*self.white_turn))):
                return True

        if pos.y != self.length-1:
            if self.piece_at(pos.cadd(0,1)) == chr(9818-6*self.white_turn):
                return True
            if pos.x >= 1 and self.piece_at(pos.cadd(-1,1)) == chr(9818-6*self.white_turn):
                return True
            if pos.x <= self.width-2 and self.piece_at(pos.cadd(1,1)) == chr(9818-6*self.white_turn):
                return True
        """
        if (   self.piece_at(pos.cadd(1,0))   == chr(9818-6*self.white_turn)
            or self.piece_at(pos.cadd(1,-1))  == chr(9818-6*self.white_turn)
            or self.piece_at(pos.cadd(0,-1))  == chr(9818-6*self.white_turn)
            or self.piece_at(pos.cadd(-1,-1)) == chr(9818-6*self.white_turn)
            or self.piece_at(pos.cadd(-1,0))  == chr(9818-6*self.white_turn)
            or self.piece_at(pos.cadd(-1,1))  == chr(9818-6*self.white_turn)
            or self.piece_at(pos.cadd(0,1))   == chr(9818-6*self.white_turn)
            or self.piece_at(pos.cadd(1,1))   == chr(9818-6*self.white_turn)):
            return True
        """
        return False
    
    def pos_endangered_by_line(self, pos):
        iter_pos = pos.cadd(0,0)
        for _ in range( self.width-1-pos.x ):
            if self.piece_at(iter_pos.add(1,0)) == chr(9819-6*self.white_turn) or self.piece_at(iter_pos) == chr(9820-6*self.white_turn):
                return True
            if self.piece_at(iter_pos): break
        iter_pos = pos.cadd(0,0)
        for _ in range( pos.y ):
            if self.piece_at(iter_pos.add(0,-1)) == chr(9819-6*self.white_turn) or self.piece_at(iter_pos) == chr(9820-6*self.white_turn):
                return True
            if self.piece_at(iter_pos): break
        iter_pos = pos.cadd(0,0)
        for _ in range( pos.x ):
            if self.piece_at(iter_pos.add(-1,0)) == chr(9819-6*self.white_turn) or self.piece_at(iter_pos) == chr(9820-6*self.white_turn):
                return True
            if self.piece_at(iter_pos): break
        iter_pos = pos.cadd(0,0)
        for _ in range( self.length-1-pos.y ):
            if self.piece_at(iter_pos.add(0,1)) == chr(9819-6*self.white_turn) or self.piece_at(iter_pos) == chr(9820-6*self.white_turn):
                return True
            if self.piece_at(iter_pos): break
        return False
    
    def pos_endangered_by_diagonal(self, pos):
        if (pos.x >= 1 and pos.y != (not self.white_turn)*(self.length-1)
            and self.piece_at(pos.cadd(-1, 1-2*self.white_turn)) == chr(9823-6*self.white_turn)):
            return True
        if (pos.x <= self.width-2 and pos.y != (not self.white_turn)*(self.length-1)
            and self.piece_at(pos.cadd(1, 1-2*self.white_turn)) == chr(9823-6*self.white_turn)):
            return True
        iter_pos = pos.cadd(0,0)
        for _ in range( min( self.width-1-pos.x, pos.y ) ):
            if self.piece_at(iter_pos.add(1,-1)) == chr(9819-6*self.white_turn) or self.piece_at(iter_pos) == chr(9821-6*self.white_turn):
                return True
            if self.piece_at(iter_pos): break
        iter_pos = pos.cadd(0,0)
        for _ in range( min( pos.x, pos.y ) ):
            if self.piece_at(iter_pos.add(-1,-1)) == chr(9819-6*self.white_turn) or self.piece_at(iter_pos) == chr(9821-6*self.white_turn):
                return True
            if self.piece_at(iter_pos): break
        iter_pos = pos.cadd(0,0)
        for _ in range( min( pos.x, self.length-1-pos.y ) ):
            if self.piece_at(iter_pos.add(-1,1)) == chr(9819-6*self.white_turn) or self.piece_at(iter_pos) == chr(9821-6*self.white_turn):
                return True
            if self.piece_at(iter_pos): break
        iter_pos = pos.cadd(0,0)
        for _ in range( min(self.width-1-pos.x, self.length-1-pos.y) ):
            if self.piece_at(iter_pos.add(1,1)) == chr(9819-6*self.white_turn) or self.piece_at(iter_pos) == chr(9821-6*self.white_turn):
                return True
            if self.piece_at(iter_pos): break
        return False

    def castling_pos_dangerous(self, pos):
        pos_endangered_by_vertical_line = False
        iter_pos = pos.cadd(0,0)
        for _ in range( self.length-1 ):
            if self.piece_at(iter_pos.add(0,1-2*self.white_turn)) == chr(9819-6*self.white_turn) or self.piece_at(iter_pos) == chr(9820-6*self.white_turn):
                pos_endangered_by_vertical_line = True
                break
            if self.piece_at(iter_pos): break

        return (    pos_endangered_by_vertical_line
            or self.pos_endangered_by_diagonal(pos)
            or self.pos_endangered_by_knight(pos)
            or self.pos_endangered_by_king(pos))
    
    def castling_granted(self, old_pos, new_pos):
        if new_pos.y != old_pos.y: return False

        step = new_pos.x-old_pos.x
        if abs(step) != self.castling_step: return False
        if self.white_turn:
            if (self.white_in_check or not (
                      (self.white_can_castle_kingside  and (step>0))
                   or (self.white_can_castle_queenside and (step<0)) )):
                return False
        else:
            if (self.black_in_check or not (
                      (self.black_can_castle_kingside  and (step>0))
                   or (self.black_can_castle_queenside and (step<0)) )):
                return False

        iter_pos = old_pos.cadd(0,0)
        for _ in range(abs(step)+1):
            if self.castling_pos_dangerous(iter_pos): return False
            iter_pos.add(2*(step>0)-1,0)

        iter_pos = old_pos.cadd(0,0) # ['♜','', '', '', '♚', '',  '','♜']]
        #                                0   1   2   3    4    5    6   7
        for i in range( (step>0)*(self.width-1-old_pos.x) + (step<0)*old_pos.x - 1 ): # check if any pieces between new_pos of king and castle to do castling with
            if self.piece_at(iter_pos.add(2*(step>0)-1,0)): return False

        # if self.piece_at(Pos((self.width-1)*(step>0), old_pos.y)) == chr(9814+6*self.white_turn):
        self.board[old_pos.y][old_pos.x+1-2*(step<0)]  = chr(9814+6*self.white_turn)
        self.board[old_pos.y][(self.width-1)*(step>0)] = ''
        return True

    
    def king(self, old_pos, new_pos) -> bool:
        if abs(new_pos.y-old_pos.y) > 1 or self.pos_dangerous(new_pos): return False
        if abs(new_pos.x-old_pos.x) == 1 or abs(new_pos.y-old_pos.y) == 1:
            if self.white_turn: self.pos_white_king.add(new_pos.x-old_pos.x, new_pos.y-old_pos.y)
            else              : self.pos_black_king.add(new_pos.x-old_pos.x, new_pos.y-old_pos.y)
            return True

        # Castling
        return self.castling_granted(old_pos, new_pos)


    def pawn(self, old_pos, new_pos) -> bool:
        """Check if valid pawn move and remove enemy pawn when doing en pessant"""
        if old_pos.y - new_pos.y == 2*self.white_turn-1 and abs(new_pos.x - old_pos.x) == 1:
            if self.piece_at(new_pos): return True
            if self.pos_to_be_taken_by_en_pessant and not self.piece_at(new_pos):
                if (self.pos_to_be_taken_by_en_pessant.x == new_pos.x
                    and self.pos_to_be_taken_by_en_pessant.y == new_pos.y+2*self.white_turn-1): # 6,3  # 3 == 2+1-2*1 # 3 == 2+2*self.white_turn-1
                    self.board[self.pos_to_be_taken_by_en_pessant.y][self.pos_to_be_taken_by_en_pessant.x] = ''
                    return True
        if new_pos.x == old_pos.x and not self.piece_at(new_pos):
            if old_pos.y-new_pos.y == 2*self.white_turn-1:
                return True
            if ( old_pos.y == 1+self.white_turn*(self.length-3) and old_pos.y-new_pos.y == -2+4*self.white_turn and
                    not self.piece_at(old_pos.cadd(0,1-2*self.white_turn)) ):
                self.white_did_previous_2step_pawn_move = True if self.white_turn else False
                self.pos_to_be_taken_by_en_pessant = new_pos
                return True
        return False
    

    def rock(self, old_pos, new_pos) -> bool:
        iter_pos = old_pos.cadd(0,0)
        if new_pos.y == old_pos.y:
            x_step = 1 if new_pos.x > old_pos.x else -1
            for _ in range(abs(new_pos.x-old_pos.x)-1):
                if self.piece_at(iter_pos.add(x_step,0)):
                    return False
            return True
        if new_pos.x == old_pos.x:
            y_step = 1 if new_pos.y > old_pos.y else -1
            for _ in range(abs(new_pos.y-old_pos.y)-1):
                if self.piece_at(iter_pos.add(0,y_step)):
                    return False
            return True
        return False

        """
        if new_pos.x != old_pos.x and new_pos.y != old_pos.y:
            return False
        iter_pos = old_pos.cadd(0,0)
        if new_pos.y == old_pos.y and new_pos.x > old_pos.x:
            for x in range(old_pos.x, new_pos.x-1):
                if self.piece_at(iter_pos.add(1,0)):
                    return False
        elif new_pos.y < old_pos.y and new_pos.x == old_pos.x:
            for x in range(old_pos.y, new_pos.y-1):
                if self.piece_at(iter_pos.add(0,-1)):
                    return False
        elif new_pos.y == old_pos.y and new_pos.x < old_pos.x:
            for x in range(old_pos.x, new_pos.x-1):
                if self.piece_at(iter_pos.add(-1,0)):
                    return False
        elif new_pos.y > old_pos.y and new_pos.x == old_pos.x:
            for x in range(old_pos.y, new_pos.y-1):
                if self.piece_at(iter_pos.add(0,1)):
                    return False
        return True
        """
    
    def bishop(self, old_pos, new_pos) -> bool:
        if abs(new_pos.x - old_pos.x) != abs(new_pos.y - old_pos.y):
            return False
        iter_pos = old_pos.cadd(0,0)
        x_step = 1 if new_pos.x > old_pos.x else -1
        y_step = 1 if new_pos.y > old_pos.y else -1
        for _ in range(abs(new_pos.x-old_pos.x)-1):
            if self.piece_at(iter_pos.add(x_step,y_step)):
                return False
        return True
    
    def queen(self, old_pos, new_pos) -> bool:
        return self.bishop(old_pos, new_pos) or self.rock(old_pos, new_pos)
    
    def knight(self, old_pos, new_pos) -> bool:
        if abs(new_pos.x-old_pos.x) == 2 and abs(new_pos.y-old_pos.y) == 1:
            return True
        if abs(new_pos.y-old_pos.y) == 2 and abs(new_pos.x-old_pos.x) == 1:
            return True
        return False
        


def main():
    """board = [['♖', '♘', '♗', '♕', '♔', '♗', '♘', '♖'],
             ['♙', '♙', '♙', '♙', '♙', '♙', '♙', '♙'],
             [  '',   '',   '',  '',   '',   '',   '',  ''],
             [  '',   '',   '',  '',   '♛',   '',   '',  ''],
             [  '',   '♕',   '',  '',   '♕',   '♞',   '',  '♕'],
             [  '',   '',   '',  '',   '',   '',   '',  ''],
             ['♟', '♟', '♟', '♟', '♝', '♝', '♟', '♟'],
             ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜']]
    """
    board = [['♖','', '', '', '♔',  '', '','♖'],
             ['','', '','', '♙','', '',''],
             ['','','', '', '', '', '',''],
             ['','', '', '','', '♟','♙',''],
             ['','','', '', '', '','',''],
             ['','', '','', '','', '',''],
             ['','', '', '', '', '',  '',''],
             ['♜','', '', '', '♚', '',  '','♜']]

             # if u take the piece it cant treathen the king
 
    Chess = ChessGame(board)
    Chess.play()


if __name__ == '__main__':
    main()