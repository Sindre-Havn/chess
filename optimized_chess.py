import copy
from typing import Union, Optional, overload
import numpy as np
import hashlib

# Unicode chess symbols: https://qwerty.dev/chess-symbols-to-copy-and-paste/

# Read: https://mathspp.com/blog/pydonts/pass-by-value-reference-and-assignment
# on how python arguments are passed - stop old_pos and new_pos from changing.


# Python pass by assignment:
# - Immutable arguments gets passed as value
# - default arguments to a function is stored
#   in a special place as a backup: func_name.__defaults__
#   SOLVED by Boolean short-circuiting:
#     * BAD  func_name(elem, l=[])
#     * GOOD func_name(elem, l=None)
#                lst = l or []
#
# Explanation: old_pos and new_pos is mutable, and gets
# passed by reference when entering a methode. Should
# use copy more frequently. __copy__ methode
# is prefered. Add to Pos so i can use copy library: copy.copy(old_pos)
# For example:
#
# def __copy__(self):
#     return Pos(self.x, self.y)
#
# Try-except is 30% faster (timeitx100x3) then checking if x,y pos is within borders



### TO DO

# 1. Clean up all prints
# 2. Replace all check if out of board with out_of_board methode

# rename "old", "new" _idx. Idx is unprecise

# Continuity on return bool or return None
# Continuity on return Pos allways or return bool
# Continuity on treath vs danger vs attacker
# Continuity on king names: king vs pos_friendly_king vs turns_king

# Optimize for creating new try-except block for every king move in out_of_board

# Not in use

# patt:
# for piece on board:
#   if piece can move: break
#
# check if same position 3 times
# Hash every 

class Pos:
    """ Index of 2D array. Top left corner is (0,0)"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def add(self, x: int, y: int) -> object:
        """Add to x and y pos."""
        self.x += x
        self.y += y
        return self
    
    def cadd(self, x: int, y: int) -> object:
        """Return a copy of the object after an add."""
        return copy.copy(self).add(x,y)
    
    def __copy__(self) -> object:
        """Returns copy of object."""
        return Pos(self.x, self.y)

    def __eq__(self, __o: object) -> bool:
        return self.x == __o.x and self.y == __o.y
    
    def __str__(self) -> None:
        """Position as string"""
        return str(self.x) + ',' + str(self.y)


class ChessGame:
    def __init__(self, board):
        #mate self.auto_moves = ['e1 e2', 'e8 d8', 'a1 a8', 'd8 d7', 'h1 a1', 'h8 d8', 'a1 a7', 'd7 e8', 'a7 e7', 'e8 f8', 'e2 e1', 'f8 g8', 'a8 d8', 'e1 e2', 'g5 g4']
        self.auto_moves = ['a1 a2', 'a8 a7', 'a2 a1', 'a7 a8', 'a1 a2', 'a8 a7', 'a2 a1', 'a7 a8', 'a1 a2', 'a8 a7', 'a2 a1', 'a7 a8']
        self.pos_checks_count = 0

        self.board  = np.asarray(board, dtype=str)
        self.length = len(board)
        self.width  = len(board[0])
        self.white_turn = True
        self.white_did_previous_2step_pawn_move = None
        self.pos_to_be_taken_by_en_pessant = None
        self.valid_move = {'???':self.king,   '???':self.queen,  '???':self.rock,
                           '???':self.bishop, '???':self.knight, '???':self.pawn}
        self.pos_white_king = None
        self.pos_black_king = None
        self.set_pos_of_kings_and_count_pieces()
        self.white_can_castle_kingside  = (self.pos_white_king.y == self.length-1 and
                                           self.piece_at(Pos(self.width-1, self.length-1)) == '???')
        self.white_can_castle_queenside = (self.pos_white_king.y == self.length-1 and
                                           self.piece_at(Pos(0, self.length-1)) == '???')
        self.black_can_castle_kingside  = (self.pos_black_king.y == 0 and
                                           self.piece_at(Pos(self.width-1, 0)) == '???')
        self.black_can_castle_queenside = (self.pos_black_king.y == 0 and
                                           self.piece_at(Pos(0, 0)) == '???')
        self.castling_step = 2
        print(self.white_can_castle_kingside, self.white_can_castle_queenside,
              self.black_can_castle_kingside, self.black_can_castle_queenside)

        self.game_over = False
        self.draw = False
        self.pos_attackers = []
        self.friendly_piece_dict = {'K':chr(9812+6*self.white_turn), 'Q':chr(9813+6*self.white_turn),
                                    'R':chr(9814+6*self.white_turn), 'B':chr(9815+6*self.white_turn),
                                    'N':chr(9816+6*self.white_turn), 'P':chr(9817+6*self.white_turn)}
        self.enemy_piece_dict = {'K':chr(9818-6*self.white_turn), 'Q':chr(9819-6*self.white_turn),
                                 'R':chr(9820-6*self.white_turn), 'B':chr(9821-6*self.white_turn),
                                 'N':chr(9822-6*self.white_turn), 'P':chr(9823-6*self.white_turn)}
        self.board_positions = dict()
        self.threefold_repetition_rule()
        self.turns_since_capture_or_pawn_move = 0
    


    
    def switch_turn(self, new_pos: Pos) -> None:
        """Change turn from white to black and opposite. Update king position"""
        if self.turns_king(new_pos):
            if self.white_turn: self.pos_white_king = new_pos
            else              : self.pos_black_king = new_pos
        self.white_turn = not self.white_turn
        self.friendly_piece_dict = {'K':chr(9812+6*self.white_turn), 'Q':chr(9813+6*self.white_turn),
                                    'R':chr(9814+6*self.white_turn), 'B':chr(9815+6*self.white_turn),
                                    'N':chr(9816+6*self.white_turn), 'P':chr(9817+6*self.white_turn)}
        self.enemy_piece_dict = {'K':chr(9818-6*self.white_turn), 'Q':chr(9819-6*self.white_turn),
                                 'R':chr(9820-6*self.white_turn), 'B':chr(9821-6*self.white_turn),
                                 'N':chr(9822-6*self.white_turn), 'P':chr(9823-6*self.white_turn)}

    def set_pos_of_kings_and_count_pieces(self) -> None:
        """Set initial Pos for '???' and '???' in the chessboard array. Error if not excactly one '???' and one '???' in chessboard array."""
        row_count = 0
        for row in self.board:
            col_count = 0
            for piece in row:
                if not piece: continue
                if ((piece == '???') and self.pos_white_king) or ((piece == '???') and self.pos_black_king):
                    raise ValueError(f"Chessgame does not support multiple pieces of type '{piece}' in chessboard array.")
                if piece == '???':
                    self.pos_white_king = Pos(col_count, row_count)
                elif piece == '???':
                    self.pos_black_king = Pos(col_count, row_count)
                col_count += 1
            row_count += 1
        if not(self.pos_white_king and self.pos_white_king):
            raise ValueError("Missing unicode character '???'  or '???' in chessboard array")
    
    def ptc(self, pos: Pos) -> str:
        """Convert Pos type coordinated to chesscoordinates."""
        return chr(pos.x+65) + str(self.length-pos.y)

    def piece_at(self, pos: Pos) -> bool:
        """Return chess character in boardarray given pos"""
        self.pos_checks_count += 1
        return self.board[pos.y][pos.x]

    def turns_king(self, pos: Pos) -> bool:
        """Piece at pos is king of current turn"""
        return self.piece_at(pos) == chr(9812+6*self.white_turn)

    def perpendicular(self, pos1: Pos, pos2: Pos) -> bool:
        return pos1.x == pos2.x or pos1.y == pos2.y

    def diagonal(self, pos1: Pos, pos2: Pos) -> bool:
        return abs(pos1.x - pos2.x) == abs(pos1.y - pos2.y)

    @overload
    def friendly(self, icon: str) -> bool:
        """Return True if icon reprisents piece thats friendly."""
        return ord(icon) >= 9812+6*self.white_turn and ord(icon) <= 9817+6*self.white_turn

    def friendly(self, pos: Pos, piece_types: tuple[str]='ALL') -> bool:
        """Return True if piece at pos is one of the friendly piece_types. Accepts all types by default."""
        piece = self.piece_at(pos)
        if piece == '': return False
        if piece_types == 'ALL': self.friendly(piece)

        for type in piece_types:
            if piece == self.friendly_piece_dict[type]:
                return True
        return False

    @overload
    def enemy(self, icon: str) -> bool:
        """Return True if icon reprisents piece of enemy."""
        return ord(icon) >= 9818-6*self.white_turn and ord(icon) <= 9823-6*self.white_turn
    
    def enemy(self, pos: Pos, piece_types: tuple[str]='ALL') -> bool:
        """Return True if piece at pos is one of the enemy piece_types. Accepts all types by default."""
        piece = self.piece_at(pos)
        if not piece: return False
        if piece_types == 'ALL': return self.enemy(piece)

        for type in piece_types:
            if piece == self.enemy_piece_dict[type]:
                return True
        return False

    def line_treath(self, pos: Pos, piece_types: tuple[str], x_step: int, y_step: int) -> Optional[Pos]:
        """Return position of enemy piece if piece in piece_types. Checks all positions from pos to edge og board."""
        pos = copy.copy(pos)
        try:
            while True:
                if self.enemy(pos.add(x_step, y_step), piece_types): return pos
                if self.piece_at(pos): break
        except IndexError: return False

    def line_defend(self, new_pos: Pos, x_step: int, y_step: int, steps: int) -> Optional[Pos]:
        """Return position of friendly piece if piece can defend attack along line, without causing selfcheck."""
        pos = copy.copy(new_pos)
        try:
            for _ in range(steps):
                if self.can_attack_pos(pos.add(x_step, y_step)):
                    pos_of_defender = self.can_attack_pos(new_pos)
                    if pos_of_defender and self.move_cause_self_check(pos_of_defender, new_pos): return pos_of_defender
        except IndexError: return False
    
    def move_cause_self_check(self, old_pos: Pos, new_pos: Pos=None) -> bool:
        """Return True if move causes players king to be in check."""
        if self.turns_king(old_pos) and new_pos:
            icon = self.piece_at(old_pos)
            self.board[old_pos.y][old_pos.x] = '' # Temporarly removes king to incase it gets shielding form it's old_pos
            is_danger = self.dangerous(new_pos)
            self.board[old_pos.y][old_pos.x] = icon
            return is_danger
        pos_friendly_king = self.pos_white_king if self.white_turn else self.pos_black_king
        x_step = 1 if pos_friendly_king.x < old_pos.x else -1
        y_step = 1 if pos_friendly_king.y < old_pos.y else -1

        if self.diagonal(pos_friendly_king, old_pos):
            if self.diagonal(pos_friendly_king, new_pos):
                if (   self.friendly(old_pos, ('B','P'))
                    or (self.friendly(old_pos, ('Q'))
                        and (pos_friendly_king.x > old_pos.x) == (pos_friendly_king.x > new_pos.x) # Same diagonal
                        and (pos_friendly_king.y > old_pos.y) == (pos_friendly_king.y > new_pos.y) )):
                    return
            treath = self.line_treath(old_pos, ('Q','B'), x_step, y_step)
            if treath: return True
        
        elif pos_friendly_king.y == old_pos.y and new_pos.y != old_pos.y:
            treath = self.line_treath(old_pos, ('Q','R'), x_step, 0)
            if treath: return True

        elif pos_friendly_king.x == old_pos.x and new_pos.x != old_pos.x:
            treath = self.line_treath(old_pos, ('Q','R'), 0, y_step)
            if treath: return True
        return False
    
    def valid_input_format(self, inp: str) -> bool:
        """Checks if input string is formated correctly."""
        if (   len(inp) == 5 and inp[0].isalpha() and inp[1].isnumeric() and
            inp[2].isspace() and inp[3].isalpha() and inp[4].isnumeric()):
  
            if (    97 <= ord(inp[0]) and ord(inp[0]) < 97 + self.width
                and  1 <= int(inp[1]) and int(inp[1]) <= self.length
                and 97 <= ord(inp[3]) and ord(inp[3]) < 97 + self.width
                and  1 <= int(inp[4]) and int(inp[4]) <= self.length):
                return True
        return False
    
    def input_move(self) -> tuple[Pos]:
        """Takes input, checks if valid format, checks if old position and new position on board are valid."""
        while True:
            inp = ''                  ## FIX - test
            if not self.auto_moves:   ## FIX - test
                inp = input('Please enter move: ')
            else:                     ## FIX - test
                inp = self.auto_moves.pop(0)
            if not self.valid_input_format(inp): continue
            old_idx, new_idx = inp.split()
            old_pos = Pos(ord(old_idx[0].lower())-97, self.length-int(old_idx[1])) # Exmpl: C2 D4 -> 6,2 3,4
            if self.out_of_board(old_pos) or not self.friendly(old_pos): print('Not right piece!'); continue
            print(old_pos)
            new_pos = Pos(ord(new_idx[0].lower())-97, self.length-int(new_idx[1]))
            if self.friendly(new_pos): print('Friendly fire is not cool!'); continue
            break
        return old_pos, new_pos
    
    def move(self) -> None:
        """Moves the piece if the move was legal and not game_over."""
        while True:
            old_pos, new_pos = self.input_move()
            icon = self.piece_at(old_pos)
            print('*****', 1, icon, ' ', self.ptc(old_pos), '->', self.ptc(new_pos))

            piece_type = chr(ord(icon)-6*self.white_turn)
            if not self.valid_move[piece_type](old_pos, new_pos): continue
            print('*****', 2, 'Valid move')

            if self.move_cause_self_check(old_pos, new_pos): continue
            print('*****', 3, 'No selfcheck')

            self.set_pos_of_attackers(old_pos, new_pos)
            if self.pos_attackers:
                print('*****', 4.1, 'Check!', [(self.ptc(p), self.piece_at(p)) for p in self.pos_attackers])
                self.white_turn = not self.white_turn # Temporarly switch turn
                if self.friendly_king_can_move() or self.friendly_can_defend_attack():
                    self.white_turn = not self.white_turn # Switch back
                    continue
                self.game_over = True
                break

            print('*****', 3, 'King is safe')

            self.fifthy_move_rule(old_pos, icon)

            icon = self.check_special_moves(old_pos, new_pos, icon)
            self.board[old_pos.y][old_pos.x] = ''
            self.board[new_pos.y][new_pos.x] = icon
            self.draw_board()
            print('Checks: ', self.pos_checks_count)

            self.threefold_repetition_rule()
            self.switch_turn(new_pos)
            print('\n\n\n')
            break
    """
    piece_count = dict('???':0, '???':0, '???':0, '???':0, '???':0, '???':0,
                       '???':0, '???':0, '???':0, '???':0, '???':0, '???':0)
    self.dead_position_pieces = ('???','???','???','???')
    if self.piece_at(new_pos): piece_count[piece] -= 1
    for key, value in piece_count.items():
        if ord(key)
    
    for key, value in self.piece_count.items(): # FIX
        dead_position_count = 0
        if value > 0 and key not in self.dead_position_pieces:
            return False
        dead_position_count += self.piece_count[piece]
        if 
        if dead_position_count >= 2: return False
        if dead_position_count == 2:
        if self.piece_count['???']==1 and self.piece_count['???']==1 and 
        self.game_over = True
        self.draw = True
        return True

    if sum(self.dead_position_pieces)
    
    for row in self.board:
        for piece in row:
            print()

    if pawn_promotion:
        piece_count[chr(9817+6*self.white_turn)] -= 1
        piece_count[icon] += 1
    

    
    def stale_mate(self):
        for row in board:
            for piece in row:
                if not piece: continue
                if self.friendly(piece) and piece.can_move():
                    return False
        self.game_over = True
        se


    
    """
    
    #### FIX - not in use
    def dead_position(self):
        """Not enough material for either player to pull of a checkmate"""
        pass
    
    def threefold_repetition_rule(self):
        """The board-setup is identical for the third turn for either player. Including same right to castling and en pessant."""
        hashed_board = hash((self.board.tostring(), self.white_can_castle_kingside, self.white_can_castle_queenside, self.black_can_castle_kingside, self.black_can_castle_queenside))
        try:
            self.board_positions[hashed_board] += 1
        except KeyError: self.board_positions[hashed_board] = 1
        if self.board_positions[hashed_board] >= 3:
            self.game_over = True
            self.draw = True
        print(self.board_positions)

    #### FIX - not in use
    def fifthy_move_rule(self, new_pos, icon) -> None:
        """There has been no capture or pawn move last 50 turns for either player."""
        if icon == chr(9817+6*self.white_turn) or self.piece_at(new_pos):
            self.turns_since_capture_or_pawn_move = 0
            return
        self.turns_since_capture_or_pawn_move += 1
        if self.turns_since_capture_or_pawn_move >= 50:
            self.game_over = True
            self.draw = True

    #### FIX - not in use
    def stalemate(self):
        """The currentplayer have no valid moves"""
        pass
    
    def play(self) -> None:
        self.draw_board()
        while not self.game_over:
            print('Whites turn:', self.white_turn)
            self.move()
        if self.draw:
            print('Draw!')
        elif self.white_turn:
            print('White won!')
        else:
            print('Black won!')
        print('Checks: ', self.pos_checks_count)
    
    def draw_board(self) -> None:
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
    
    def friendly_can_defend_attack(self) -> bool:
        """Return True if friendly piece can eliminate treath or block it."""
        if len(self.pos_attackers) > 1: return False
        attackers_pos = self.pos_attackers[0]
        if self.enemy(attackers_pos, ('N')):
            old_pos = self.can_attack_pos(attackers_pos)
            print('OLD_POS, ', [self.ptc(p) for p in old_pos])
            if old_pos and self.move_cause_self_check(old_pos): return True
            return False

        pos_friendly_king = self.pos_white_king if self.white_turn else self.pos_black_king
        x_step = 1 if pos_friendly_king.x < attackers_pos.x else -1
        y_step = 1 if pos_friendly_king.y < attackers_pos.y else -1
        if self.diagonal(attackers_pos, pos_friendly_king):            # Steps from king pos, to attackers pos
            defend = self.line_defend(pos_friendly_king, x_step, y_step, min( abs((x_step==1)*(self.width-1)-pos_friendly_king.x), abs((y_step==1)*(self.length-1)-pos_friendly_king.y) ))
            if defend: return True
        
        elif pos_friendly_king.y == attackers_pos.y:
            defend = self.line_defend(pos_friendly_king, x_step, 0, abs(pos_friendly_king.x - (x_step==1)*(self.width-1)))
            if defend: return True

        elif pos_friendly_king.x == attackers_pos.x:
            defend = self.line_defend(pos_friendly_king, 0, y_step, abs(pos_friendly_king.y - (y_step==1)*(self.length-1)) )
            if defend: return True
        
        return False
    
    def can_attack_pos(self, pos: Pos) -> list[Pos]:
        """pos can be attacked by friendly pieces."""
        return self.dangerous(pos)
    
    def out_of_board(self, pos: Pos) -> bool:
        """Return True if pos is outside the board."""
        if pos.x < 0 or pos.y < 0: return True
        try:
            self.board[pos.y][pos.x]
            return False
        except IndexError: return True
    
    def friendly_king_can_move(self) -> bool:
        """Return True if friendly king has legal moves."""
        king = self.pos_white_king if self.white_turn else self.pos_black_king
        king_moves = (king.cadd( 1, 0), king.cadd( 1,-1),
                      king.cadd( 0,-1), king.cadd(-1,-1),
                      king.cadd(-1, 0), king.cadd(-1, 1),
                      king.cadd( 0, 1), king.cadd( 1, 1))
        icon = self.piece_at(king)
        self.board[king.y][king.x] = '' # Temporarly removes king to incase it gets shielding form it's old_pos
        for move in king_moves:
            if self.out_of_board(move) or self.friendly(move) or self.dangerous(move): continue
            self.board[king.y][king.x] = icon
            return True
        self.board[king.y][king.x] = icon
        return False
    
    def king_in_check(self) -> bool:
        """Return True if king is under attack."""
        return len(self.pos_attackers) != 0

    def check_special_moves(self, old_pos: Pos, new_pos: Pos, icon: str) -> str:
        """Resets posibility for en pessant, does pawn promotion, and sets castling-flags to False"""
        # Reset possibility for en pessant
        if self.pos_to_be_taken_by_en_pessant and self.white_did_previous_2step_pawn_move != self.white_turn:
            self.pos_to_be_taken_by_en_pessant = None

        # Pawn promotion
        if icon in '??????' and new_pos.y == (not self.white_turn)*(self.length-1): #self.length-1-self.white_turn*(self.length-1)
            while True:
                inp = input('Enter a single letter  Q R B N  to promote pawn: ').lower()
                if len(inp) == 1 and inp in 'qrbn':
                    break
            icon = chr(9813 + 'qrbn'.index(inp) + 6*self.white_turn)
        
        # Remove possibility for castling
        if self.white_can_castle_kingside:
            self.white_can_castle_kingside  = (icon != '???') and not (old_pos.x == self.width-1 and old_pos.y == self.length-1)
        if self.black_can_castle_kingside:
            self.black_can_castle_kingside  = (icon != '???') and not (old_pos.x == self.width-1 and old_pos.y == 0)
        if self.white_can_castle_queenside:
            self.white_can_castle_queenside = (icon != '???') and not (old_pos.x == 0 and old_pos.y == self.length-1)
        if self.black_can_castle_queenside:
            self.black_can_castle_queenside = (icon != '???') and not (old_pos.x == 0 and old_pos.y == 0)

        return icon

    
    def dangerous(self, pos) -> bool:
        """Return True if danger perpendicular, diagonaly, from knight, and from king; to 'pos'"""
        treath = self.perpendicular_treath(pos)
        if treath: return True
        treath = self.diagonal_treath(pos)
        if treath: return True
        treath = self.knight_treath(pos)
        if treath: return True
        treath = self.treath_from_king(pos)
        if treath: return True
        return False
        # when iterating trough, add up all the pos that could defend; check if new_pos is one of them

    def knight_treath(self, pos: Pos) -> Union[Pos, bool]:
        """Return position of first knight danger to 'pos', if no danger return False."""
        possible_knight_moves = (pos.cadd( 2,-1), pos.cadd( 1,-2),
                                 pos.cadd(-1,-2), pos.cadd(-2,-1),
                                 pos.cadd(-2, 1), pos.cadd(-1, 2),
                                 pos.cadd( 1, 2), pos.cadd( 2, 1))
        try:
            for move in possible_knight_moves:
                if self.enemy(move, ('N')): return pos
        except IndexError: pass
        return False
    
    def treath_from_king(self, pos: Pos) -> bool: # Write like other treath funcs, return Pos if king treath -^
        """Return True if any of the 8 positions surounding 'pos' is defended by the enemy king, if no danger return False."""
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
        return False
    
    def perpendicular_treath(self, pos: Pos) -> Optional[Pos]:
        """Return position of first perpendicular danger to 'pos', if no danger return None."""
        treath = self.line_treath(pos, ('Q','R'), x_step=1, y_step=0)
        if treath: return treath
        treath = self.line_treath(pos, ('Q','R'), x_step=0, y_step=-1)
        if treath: return treath
        treath = self.line_treath(pos, ('Q','R'), x_step=-1, y_step=0)
        if treath: return treath
        treath = self.line_treath(pos, ('Q','R'), x_step=0, y_step=1)
        if treath: return treath
    
    def pawn_treath(self, pos: Pos) -> Optional[Pos]:
        """Return position of pawn treathening pos."""
        potential_pawn = pos.cadd(-1, 1-2*self.white_turn)
        if (pos.x >= 1 and pos.y != (not self.white_turn)*(self.length-1)
            and self.enemy(potential_pawn, ('P'))):
            return potential_pawn
        potential_pawn = pos.cadd(1, 1-2*self.white_turn)
        if (pos.x <= self.width-2 and pos.y != (not self.white_turn)*(self.length-1)
            and self.enemy(potential_pawn, ('P'))):
            return potential_pawn
    
    def diagonal_treath(self, pos: Pos) -> Optional[Pos]:
        """Return position of first diagonal danger to 'pos', if no danger return False."""
        treath = self.pawn_treath(pos)
        if treath: return treath
        treath = self.line_treath(pos, ('Q','B'), x_step=1, y_step=-1)
        if treath: return treath
        treath = self.line_treath(pos, ('Q','B'), x_step=-1, y_step=-1)
        if treath: return treath
        treath = self.line_treath(pos, ('Q','B'), x_step=-1, y_step=1)
        if treath: return treath
        treath = self.line_treath(pos, ('Q','B'), x_step=1, y_step=1)
        if treath: return treath

    def castling_pos_dangerous(self, pos: Pos) -> tuple[Union[Pos, bool]]:
        vertical_treath = self.line_treath(pos, ('Q','R'), x_step=0, y_step=1-2*self.white_turn)
        return (    vertical_treath
            or self.diagonal_treath(pos)
            or self.knight_treath(pos)
            or self.treath_from_king(pos))
    
    def castling_granted(self, old_pos: Pos, new_pos: Pos) -> bool:
        """Return True if castling is allowed."""
        if new_pos.y != old_pos.y: return False
        step = new_pos.x-old_pos.x
        if abs(step) != self.castling_step: return False
        if self.white_turn:
            if ( not (self.white_can_castle_kingside  and (step>0))
                  or (self.white_can_castle_queenside and (step<0)) ):
                return False
        else:
            if ( not (self.black_can_castle_kingside  and (step>0))
                  or (self.black_can_castle_queenside and (step<0)) ):
                return False

        iter_pos = copy.copy(old_pos)
        for _ in range(abs(step)+1): # Includes checking if king in danger
            if self.castling_pos_dangerous(iter_pos): return False
            iter_pos.add(2*(step>0)-1,0)

        iter_pos = copy.copy(old_pos)
        for i in range( (step>0)*(self.width-1-old_pos.x) + (step<0)*old_pos.x - 1 ): # check if any pieces between new_pos of king and castle to do castling with
            if self.piece_at(iter_pos.add(2*(step>0)-1,0)): return False

        self.board[old_pos.y][old_pos.x+1-2*(step<0)]  = chr(9814+6*self.white_turn)
        self.board[old_pos.y][(self.width-1)*(step>0)] = ''
        return True
    
    def king(self, old_pos: Pos, new_pos: Pos) -> bool:
        if abs(new_pos.y-old_pos.y) > 1: return False
        if abs(new_pos.x-old_pos.x) == 1 or abs(new_pos.y-old_pos.y) == 1:
            return True

        return self.castling_granted(old_pos, new_pos)

    def pawn(self, old_pos: Pos, new_pos: Pos) -> bool:
        """Check if valid pawn move and remove enemy pawn when doing en pessant."""
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

    def rock(self, old_pos: Pos, new_pos: Pos) -> bool:
        iter_pos = copy.copy(old_pos)
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
    
    def bishop(self, old_pos: Pos, new_pos: Pos) -> bool:
        if not self.diagonal(new_pos, old_pos):
            return False
        iter_pos = copy.copy(old_pos)
        x_step = 1 if new_pos.x > old_pos.x else -1
        y_step = 1 if new_pos.y > old_pos.y else -1
        for _ in range(abs(new_pos.x-old_pos.x)-1):
            if self.piece_at(iter_pos.add(x_step,y_step)):
                return False
        return True
    
    def queen(self, old_pos: Pos, new_pos: Pos) -> bool:
        return self.bishop(old_pos, new_pos) or self.rock(old_pos, new_pos)
    
    def knight(self, old_pos: Pos, new_pos: Pos) -> bool:
        if abs(new_pos.x-old_pos.x) == 2 and abs(new_pos.y-old_pos.y) == 1:
            return True
        if abs(new_pos.y-old_pos.y) == 2 and abs(new_pos.x-old_pos.x) == 1:
            return True
        return False
    
    def set_pos_of_attackers(self, old_pos: Pos, new_pos: Pos) -> None:
        """Set position of attackers if they threaten king of next turn."""
        self.pos_attackers = []
        if self.enemy_checked(new_pos): self.pos_attackers.append(new_pos)
        treath = self.discovered_check(old_pos)
        if treath: self.pos_attackers.append(treath)

    def enemy_checked(self, new_pos: Pos) -> bool:
        """Return True if new_pos sets enemy king in check."""
        #pos_turns_king = self.pos_white_king if self.white_turn else self.pos_black_king
        pos_enemy_king = self.pos_black_king if self.white_turn else self.pos_white_king
        x_step = 1 if pos_enemy_king.x < new_pos.x else -1
        y_step = 1 if pos_enemy_king.y < new_pos.y else -1

        if self.diagonal(pos_enemy_king, new_pos) and self.enemy(new_pos, ('Q','B','P')):
            if self.pawn_treath(new_pos): return True
            if self.line_treath(pos_enemy_king, ('Q','B'), x_step, y_step):
                return True

        elif self.enemy(new_pos, ('Q','R')):
            if pos_enemy_king.y == new_pos.y:
                if self.line_treath(pos_enemy_king, ('Q','R'), x_step, 0):
                    return True
            if pos_enemy_king.y == new_pos.y:
                if self.line_treath(pos_enemy_king, ('Q','R'), 0, y_step=y_step):
                    return True

        elif self.enemy(new_pos, ('N')) and self.knight_treath(pos_enemy_king):
            return True
        return False

    def discovered_check(self, old_pos: Pos) -> Optional[Pos]:
        """When moving a piece, see if a piece behind get a line of attack on the enemy king. Return Pos of attacker or None."""
        #pos_turns_king = self.pos_white_king if self.white_turn else self.pos_black_king
        pos_enemy_king = self.pos_black_king if self.white_turn else self.pos_white_king
        x_step = 1 if pos_enemy_king.x < old_pos.x else -1
        y_step = 1 if pos_enemy_king.y < old_pos.y else -1

        if self.diagonal(pos_enemy_king, old_pos):
            treath = self.line_treath(old_pos, ('Q','B'), x_step, y_step)
            if treath: return treath
        elif pos_enemy_king.y == old_pos.y:    
            treath = self.line_treath(old_pos, ('Q','R'), x_step, 0)
            if treath: return treath
        elif pos_enemy_king.x == old_pos.x:              
            treath = self.line_treath(old_pos, ('Q','R'), 0, y_step)
            if treath: return treath

def main():
    """board = [['???', '???', '???', '???', '???', '???', '???', '???'],
             ['???', '???', '???', '???', '???', '???', '???', '???'],
             [  '',   '',   '',  '',   '',   '',   '',  ''],
             [  '',   '',   '',  '',   '???',   '',   '',  ''],
             [  '',   '???',   '',  '',   '???',   '???',   '',  '???'],
             [  '',   '',   '',  '',   '',   '',   '',  ''],
             ['???', '???', '???', '???', '???', '???', '???', '???'],
             ['???', '???', '???', '???', '???', '???', '???', '???']]
    """
    board = [['???','', '', '', '???',  '', '','???'],
             ['','', '','', '???','', '',''],
             ['','','', '', '', '', '',''],
             ['','', '', '','', '???','???',''],
             ['','','', '', '', '','',''],
             ['','', '','', '','', '',''],
             ['','', '', '', '', '',  '',''],
             ['???','', '', '', '???', '',  '','???']]
 
    Chess = ChessGame(board)
    Chess.play()


if __name__ == '__main__':
    main()