import copy
from typing import Optional
import numpy as np

# check if any king is in check in __init__
# check if king is at start_pos.x. Think about different boardsizes
# move all draw funcs within update methode
# is self.dircation problem when not checking if on perp og diag line from king?
# Feel like we got too many self.piece_at checks...
# Check for draw in __init__
# If game_over anymoment, stop imediately?


class Pos:
    """ Index of 2D array. Example: left corner is (0,0)"""
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
    
    def __lt__(self, __o: object) -> bool:
        """Used to sort Pos objects by their x-position."""
        return self.x < __o.x
    
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
        
        self.valid_move = {'K':self.king,   'Q':self.queen,  'R':self.rock,
                           'B':self.bishop, 'N':self.knight, 'P':self.pawn}
        self.friendly_icon = {'K':chr(9818-6*self.white_turn), 'Q':chr(9819-6*self.white_turn),
                                'R':chr(9820-6*self.white_turn), 'B':chr(9821-6*self.white_turn),
                                'N':chr(9822-6*self.white_turn), 'P':chr(9823-6*self.white_turn)}
        self.enemy_icon    = {'K':chr(9812+6*self.white_turn), 'Q':chr(9813+6*self.white_turn),
                                'R':chr(9814+6*self.white_turn), 'B':chr(9815+6*self.white_turn),
                                'N':chr(9816+6*self.white_turn), 'P':chr(9817+6*self.white_turn)}
        self.type_from_icon = dict((v, k) for k, v in self.friendly_icon.items()) | dict((v, k) for k, v in self.enemy_icon.items())
        print(self.type_from_icon)
        piece_types = list(self.friendly_icon.values()) + list(self.enemy_icon.values())
        self.pieces = dict()
        self.total_pieces = 0
        for icon in piece_types:
            self.pieces[icon] = np.array([])
        row_idx = 0
        for row in self.board:
            col_idx = 0
            for icon in row:
                if icon:
                    self.pieces[icon] = np.append(self.pieces[icon], Pos(col_idx, row_idx))
                    self.total_pieces += 1
                col_idx += 1
            row_idx += 1
        for key, val in self.pieces.items():
            print(key)
            [print(p) for p in val]

        assert len(self.pieces['♔']) == 1 and len(self.pieces['♚']) == 1, f"There must be excactly one king of each color."
    
        self.castling_step = 2
        pwk = self.pieces['♔'][0]
        pbk = self.pieces['♚'][0]
        self.white_castle_kingside  = (pwk.y == self.length-1 and self.piece_at(Pos(self.width-1, self.length-1)) == '♖')
        self.white_castle_queenside = (pwk.y == self.length-1 and self.piece_at(Pos(0, self.length-1)) == '♖')
        self.black_castle_kingside  = (pbk.y == 0 and self.piece_at(Pos(self.width-1, 0)) == '♜')
        self.black_castle_queenside = (pbk.y == 0 and self.piece_at(Pos(0, 0)) == '♜')
        
        print(self.white_castle_kingside, self.white_castle_queenside,
              self.black_castle_kingside, self.black_castle_queenside)

        self.game_over = False
        self.draw = False
        self.pos_attackers = []
        self.white_2step_pawn_move = None
        self.pos_en_pessant = None
        self.board_positions = dict()
        self.threefold_repetition_rule()
        self.turns_since_capture_or_pawn_move = 0
        self.enemy_king_trapped = True # FIX check if init board actually traps king
    
    def ptc(self, pos: Pos) -> str:
        """Convert Pos type coordinated to chesscoordinates."""
        return chr(pos.x+65) + str(self.length-pos.y)
    
    def piece_at(self, pos: Pos) -> bool:
        """Return chess character in boardarray given pos."""
        self.pos_checks_count += 1
        return self.board[pos.y][pos.x]

    def friendly(self, pos: Pos, piece_types: tuple[str]='ALL') -> Optional[bool]:
        """Return True if piece at pos is one of the friendly piece_types. Accepts all types by default."""
        icon = self.piece_at(pos)
        if icon == '': return False
        if piece_types == 'ALL': return self.friendly_icon.get(icon)

        for type in piece_types:
            if icon == self.friendly_icon[type]:
                return True
        return False

    def enemy(self, pos: Pos, piece_types: tuple[str]='ALL') -> Optional[bool]:
        """Return True if piece at pos is one of the enemy piece_types. Accepts all types by default."""
        icon = self.piece_at(pos)
        if not icon: return False
        if piece_types == 'ALL': return self.enemy_icon.get(icon)

        for type in piece_types:
            if icon == self.enemy_icon[type]:
                return True
        return False
    
    def out_of_board(self, pos: Pos) -> bool:
        """Return True if pos is outside the board."""
        if pos.x < 0 or pos.y < 0: return True
        try:
            self.board[pos.y][pos.x]
            return False
        except IndexError: return True
    
    def direction(self, from_pos: Pos, to_pos: Pos) -> tuple[int]:
        """Return direction old_pos has to travel to get to new_pos. Works only for perpendicular and diagonal positions."""
        x_step = 0
        if   from_pos.x < to_pos.x: x_step =  1
        elif from_pos.x > to_pos.x: x_step = -1
        y_step = 0
        if   from_pos.y < to_pos.y: y_step =  1
        elif from_pos.y > to_pos.y: y_step = -1
        return x_step, y_step
    
    def line_treath(self, pos: Pos, piece_types: tuple[str], x_step: int, y_step: int) -> Optional[Pos]:
        """Return position of enemy piece if piece in piece_types. Checks all positions from pos to edge og board."""
        pos = copy.copy(pos)
        try:
            while True:
                if self.enemy(pos.add(x_step, y_step), piece_types): return pos
                if self.piece_at(pos): break
        except IndexError: return None

    def line_defend(self, new_pos: Pos, x_step: int, y_step: int, steps: int) -> Optional[Pos]:
        """Return position of friendly piece if piece can defend attack along line, without causing selfcheck."""
        pos = copy.copy(new_pos)
        try:
            i = 0
            while i<steps:
                if self.can_attack_pos(pos.add(x_step, y_step)):
                    defenders_pos = self.can_attack_pos(new_pos)
                    if defenders_pos and not self.move_cause_self_check(defenders_pos, new_pos): return defenders_pos
            i += 1
        except IndexError: return None
    
    def promote_pawn(self) -> str:
        """Player choose new piecetype and return new icon of promoted pawn."""
        while True:
            inp = input('Enter a single letter  Q R B N  to promote pawn: ').upper()
            if len(inp) == 1 and inp in 'QRBN':
                return self.friendly_icon[inp]
    
    def update_en_pessant_and_castling(self, old_pos: Pos, icon: str) -> None:
        """Resets posibility for en pessant and sets castling-flags to False"""
        # Reset possibility for en pessant
        if self.pos_en_pessant and self.white_2step_pawn_move != self.white_turn:
            self.pos_en_pessant = None
        # Remove possibility for castling
        if self.white_castle_kingside:
            self.white_castle_kingside  = (icon != '♚') and not (old_pos.x == self.width-1 and old_pos.y == self.length-1)
        if self.black_castle_kingside:
            self.black_castle_kingside  = (icon != '♔') and not (old_pos.x == self.width-1 and old_pos.y == 0)
        if self.white_castle_queenside:
            self.white_castle_queenside = (icon != '♚') and not (old_pos.x == 0 and old_pos.y == self.length-1)
        if self.black_castle_queenside:
            self.black_castle_queenside = (icon != '♔') and not (old_pos.x == 0 and old_pos.y == 0)
    
    def valid_input_format(self, inp: str) -> bool:
        """Checks if input string is formatted correctly."""
        if (   len(inp) == 5 and inp[0].isalpha() and inp[1].isnumeric() and
            inp[2].isspace() and inp[3].isalpha() and inp[4].isnumeric()):
  
            if (    97 <= ord(inp[0]) and ord(inp[0]) < 97 + self.width
                and  1 <= int(inp[1]) and int(inp[1]) <= self.length
                and 97 <= ord(inp[3]) and ord(inp[3]) < 97 + self.width
                and  1 <= int(inp[4]) and int(inp[4]) <= self.length):
                return True
        return False

    def move(self) -> tuple[Pos, Pos, str]:
        """Takes input, checks if valid input and legal move."""
        while True:
            inp = ''                  ## FIX - test
            if not self.auto_moves:   ## FIX - test
                inp = input('Please enter move: ')
            else:                     ## FIX - test
                inp = self.auto_moves.pop(0)
            if not self.valid_input_format(inp): continue
            # Check if old_pos and new_pos are valid
            old_idx, new_idx = inp.split()
            print(old_idx, new_idx)
            old_pos = Pos(ord(old_idx[0].lower())-97, self.length-int(old_idx[1])) # Exmpl: C2 D4 -> 6,2 3,4
            print(old_pos, self.out_of_board(old_pos), not self.friendly(old_pos))
            if self.out_of_board(old_pos) or self.friendly(old_pos): print('Not right piece!'); continue
            new_pos = Pos(ord(new_idx[0].lower())-97, self.length-int(new_idx[1]))
            if self.friendly(new_pos): print('Friendly fire is not cool!'); continue
            
            icon = self.piece_at(old_pos)
            print('*****', 1, icon, ' ', self.ptc(old_pos), '->', self.ptc(new_pos))
            piece_type = self.type_from_icon[icon]
            if not self.valid_move[piece_type](old_pos, new_pos): continue
            print('*****', 2, 'Valid move')

            if self.move_cause_self_check(old_pos, new_pos): continue
            print('*****', 3, 'No selfcheck')

            self.set_pos_of_attackers(old_pos, new_pos)
            if self.pos_attackers:
                print('*****', 4.1, 'Check!', [(self.ptc(p), self.piece_at(p)) for p in self.pos_attackers])
                if self.check_mate():
                    self.game_over = True
                    return False
                continue
            if self.piece_at(new_pos): self.total_pieces -= 1
            return old_pos, new_pos, icon
    
    def update_board(self, old_pos: Pos, new_pos: Pos, icon: str) -> None:
        """Updates states and board, checks for draw."""

        self.fifthy_move_rule(old_pos, icon)

        self.update_en_pessant_and_castling(old_pos, icon)
    
        old_idx = np.where(self.pieces[icon] == old_pos)
        if self.friendly_icon['P'] and new_pos.y == (self.length-1)*(not self.white_turn):
            np.delete(self.pieces[icon], old_idx) 
            icon = self.promote_pawn()
            self.pieces[icon] = np.append(self.pieces[icon], new_pos)
        else:
            self.pieces[icon][old_idx] = new_pos
        self.board[old_pos.y][old_pos.x] = ''
        self.board[new_pos.y][new_pos.x] = icon

        self.threefold_repetition_rule()
            
        print('\n\n\n')
    
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
    
    def switch_turn(self) -> None:
        """Switch player turn and update 'self.enenmy_pieces' and 'self.friendly_icon."""
        self.white_turn = not self.white_turn
        self.friendly_icon, self.enemy_icon = self.enemy_icon, self.friendly_icon
    
    def game_loop(self) -> None:
        self.draw_board()
        while not self.game_over:
            print('Whites turn:', self.white_turn)
            old_pos, new_pos, icon = self.move()
            self.update_board(old_pos, new_pos, icon)
            self.draw_board()
            print('Checks: ', self.pos_checks_count)
            self.switch_turn()
        if self.draw:
            print('Draw!')
        elif self.white_turn:
            print('White won!')
        else:
            print('Black won!')
        print('Checks: ', self.pos_checks_count)
    
    def castling_granted(self, old_pos: Pos, new_pos: Pos) -> bool:
        """Return True if castling is allowed."""
        if new_pos.y != old_pos.y: return False
        step = new_pos.x-old_pos.x
        if abs(step) != self.castling_step: return False
        if self.white_turn:
            if ( not (self.white_castle_kingside  and (step>0))
                  or (self.white_castle_queenside and (step<0)) ):
                return False
        else:
            if ( not (self.black_castle_kingside  and (step>0))
                  or (self.black_castle_queenside and (step<0)) ):
                return False
        # Check if king path in danger
        iter_pos = copy.copy(old_pos)
        for _ in range(abs(step)+1):
            if self.dangerous(iter_pos): return False
            iter_pos.add(2*(step>0)-1,0)

        # Check if any pieces between new_pos of king and rock
        iter_pos = copy.copy(old_pos)
        for i in range( (step>0)*(self.width-1-old_pos.x) + (step<0)*old_pos.x - 1 ):
            if self.piece_at(iter_pos.add(2*(step>0)-1,0)): return False
        # Update pos of rock
        icon = self.friendly_icon['R']
        old_x = (self.width-1)*(step>0)
        new_x = new_pos.x-1+2*(step<0)
        old_idx = np.where(self.pieces[icon] == old_pos)
        self.pieces[icon][old_idx] = new_pos
        self.board[old_pos.y][new_x]  = icon
        self.board[old_pos.y][old_x] = ''
        return True
    
    def king(self, old_pos: Pos, new_pos: Pos) -> bool:
        if abs(new_pos.y-old_pos.y) > 1: return False
        if abs(new_pos.x-old_pos.x) == 1 or abs(new_pos.y-old_pos.y) == 1:
            return True
        return self.castling_granted(old_pos, new_pos)
    
    def queen(self, old_pos: Pos, new_pos: Pos) -> bool:
        return self.rock(old_pos, new_pos) or self.bishop(old_pos, new_pos)
    
    def rock(self, old_pos: Pos, new_pos: Pos) -> bool:
        x_step, y_step = self.direction(old_pos,new_pos)
        if abs(x_step) == abs(y_step): return False
        steps = abs(new_pos.x-old_pos.x if x_step else new_pos.y-old_pos.y)-1
        print('STEPS:', steps)
        iter_pos = copy.copy(old_pos)
        for _ in range(steps):
            if self.piece_at(iter_pos.add(x_step,y_step)):
                return False
        return True
    
    def bishop(self, old_pos: Pos, new_pos: Pos) -> bool:
        x_step, y_step = self.direction(old_pos,new_pos)
        if abs(x_step) != y_step: return False
        iter_pos = copy.copy(old_pos)
        for _ in range(abs(new_pos.x-old_pos.x)-1):
            if self.piece_at(iter_pos.add(x_step,y_step)):
                return False
        return True
    
    def knight(self, old_pos: Pos, new_pos: Pos) -> bool:
        if abs(new_pos.x-old_pos.x) == 2 and abs(new_pos.y-old_pos.y) == 1:
            return True
        if abs(new_pos.x-old_pos.x) == 1 and abs(new_pos.y-old_pos.y) == 2:
            return True
        return False

    def pawn(self, old_pos: Pos, new_pos: Pos) -> bool:
        """Check if valid pawn move and remove enemy pawn when doing en pessant."""
        if old_pos.y - new_pos.y == 2*self.white_turn-1 and abs(new_pos.x - old_pos.x) == 1:
            if self.piece_at(new_pos): return True
            if self.pos_en_pessant and not self.piece_at(new_pos):
                if (self.pos_en_pessant.x == new_pos.x
                    and self.pos_en_pessant.y == new_pos.y+2*self.white_turn-1): # 6,3  # 3 == 2+1-2*1 # 3 == 2+2*self.white_turn-1
                    self.board[self.pos_en_pessant.y][self.pos_en_pessant.x] = ''
                    return True
        if new_pos.x == old_pos.x and not self.piece_at(new_pos):
            if old_pos.y-new_pos.y == 2*self.white_turn-1:
                return True
            if ( old_pos.y == 1+self.white_turn*(self.length-3) and old_pos.y-new_pos.y == -2+4*self.white_turn and
                    not self.piece_at(old_pos.cadd(0,1-2*self.white_turn)) ):
                self.white_2step_pawn_move = True if self.white_turn else False
                self.pos_en_pessant = new_pos
                return True
        return False
    
    def dangerous(self, pos: Pos) -> bool:
        """Return True if position is in danger from perpendicular, diagonaly, from knight, or king.
        Does not take en pessant into account."""
        # Perpendicular
        poses = np.concatenate((self.pieces[self.enemy_icon['Q']], self.pieces[self.enemy_icon['R']]))
        for enemy_pos in poses:
            if self.rock(enemy_pos, pos): return True # Dont care about selfcheck
        # Diagonal
        poses = np.concatenate((self.pieces[self.enemy_icon['Q']], self.pieces[self.enemy_icon['B']]))
        for enemy_pos in poses:
            if self.bishop(enemy_pos, pos): return True # Dont care about selfcheck
        try:
            if (   self.enemy(Pos(pos.x-1, pos.y+2*self.white_turn-1), ('P'))
                or self.enemy(Pos(pos.x+1, pos.y+2*self.white_turn-1), ('P'))):
                return True
        except IndexError: pass
        # Knight
        poses = self.enemy_icon['N']
        for enemy_pos in poses:
            if self.knight(enemy_pos, pos): return True # Dont care about selfcheck
        # King
        king_pos = self.enemy_icon['K']
        for enemy_pos in king_pos:
            if self.king(enemy_pos, pos): return True # Dont care about selfcheck

        return False
    
    def can_attack_pos(self, pos: Pos) -> bool:
        """True if friendly can obtain pos."""
        self.switch_turn()
        danger = self.dangerous(pos)
        self.switch_turn()
        return danger
    
    def move_cause_self_check(self, old_pos: Pos, new_pos: Pos) -> bool:
        """Return True if move causes players king to be in check."""
        if self.friendly(old_pos, ('K')):
            icon = self.piece_at(old_pos)
            self.board[old_pos.y][old_pos.x] = '' # Temporarly removes king incase it gets shielding from it's old_pos
            is_danger = self.dangerous(new_pos)
            self.board[old_pos.y][old_pos.x] = icon
            return is_danger
        pos_friendly_king = self.pieces[self.friendly_icon['K']][0]
        x_step_old, y_step_old = self.direction(pos_friendly_king, old_pos)
        x_step_new, y_step_new = self.direction(pos_friendly_king, new_pos)

        if x_step_new == x_step_old and y_step_new == y_step_old:
            return False # Moved along line of attack
        
        if x_step_new == x_step_old or y_step_new == y_step_old:
            if self.line_treath(old_pos, ('Q','R'), x_step_old, y_step_old):
                return True # Perpendicular attack
        
        if abs(x_step_new) == abs(abs(x_step_new)):
            if self.line_treath(old_pos, ('Q','B'), x_step_old, y_step_old):
                return True # Diagonal attack
        
        return False
    
    def set_pos_of_attackers(self, old_pos: Pos, new_pos: Pos) -> None:
        """Set position of attackers if they threaten king of next turn."""
        # Checked by move
        self.pos_attackers = []
        piece_type = self.type_from_icon[self.piece_at(old_pos)]
        enemy_king_pos = self.pieces[self.enemy_icon['K']][0]
        if self.valid_move[piece_type](new_pos, enemy_king_pos):
            self.pos_attackers.append(new_pos)
        # Checked by discovered attack
        x_step, y_step = self.direction(enemy_king_pos, old_pos)
        piece_types = ['Q']
        if x_step==0 or y_step==0: piece_types.append('R')
        else:                      piece_types.append('B')
        discovered_attack = self.line_treath(old_pos, piece_types, x_step, y_step)
        if discovered_attack: self.pos_attackers.append(discovered_attack)
    
    def enemy_king_cant_move(self) -> None:
        icon = self.enemy_icon['K']
        pos = self.pieces[icon]
        king_moves = (pos.cadd( 1, 0), pos.cadd( 1,-1),
                      pos.cadd( 0,-1), pos.cadd(-1,-1),
                      pos.cadd(-1, 0), pos.cadd(-1, 1),
                      pos.cadd( 0, 1), pos.cadd( 1, 1))
        self.board[pos.y][pos.x] = '' # Temporarly removes king to incase it gets shielding form it's old_pos
        for move in king_moves:
            if self.out_of_board(move) or self.enemy(move) or self.can_attack_pos(move):
                continue
            self.board[pos.y][pos.x] = icon
            self.enemy_king_trapped = True
            break
        self.enemy_king_trapped = False
        self.board[pos.y][pos.x] = icon
    
    def check_mate(self) -> None:
        """True if enemy can't defend attack and unable to move king."""
        self.enemy_king_cant_move() # FIX ugly
        if not self.enemy_king_trapped: return False # FIX ugly
        # Enemy can block attack
        if len(self.pos_attackers) > 1: return True
        pos_attacker = self.pos_attackers[0]
        defender_pos = self.can_attack_pos(pos_attacker)
        if defender_pos and self.move_cause_self_check(defender_pos, pos_attacker): 
            return False
        if self.friendly(pos_attacker, ('N')): return True

        pos_enemy_king = self.enemy_icon['K']
        x_step, y_step = self.direction(pos_enemy_king, pos_attacker)
        steps = abs(pos_enemy_king.x - pos_attacker.x) if x_step else abs(pos_enemy_king.y - pos_attacker.y)
        return self.line_defend(pos_enemy_king, x_step, y_step, steps)
    

    def threefold_repetition_rule(self):
        """The board-setup is identical for the third turn for either player. Including same right to castling and en pessant."""
        hashed_board = hash((self.board.tobytes(), self.white_castle_kingside, self.white_castle_queenside, self.black_castle_kingside, self.black_castle_queenside))
        try:
            self.board_positions[hashed_board] += 1
        except KeyError: self.board_positions[hashed_board] = 1
        if self.board_positions[hashed_board] >= 3:
            self.game_over = True
            self.draw = True
        print(self.board_positions)
    
    def fifthy_move_rule(self, new_pos, icon) -> None:
        """There has been no capture or pawn move last 50 turns for either player."""
        if self.type_from_icon[icon] == 'P' or self.piece_at(new_pos):
            self.turns_since_capture_or_pawn_move = 0
            return
        self.turns_since_capture_or_pawn_move += 1
        if self.turns_since_capture_or_pawn_move >= 50:
            self.game_over = True
            self.draw = True
    
    def stale_mate(self, new_pos: Pos) -> None:
        if not self.enemy_king_trapped: return
        """
        for i in friendly_pieces:
            if i.can_move(): return
        self.game_over = True
        self.draw = True
        """
        
    
    def dead_position(self, new_pos: Pos) -> None:
        # Check if insufficient material
        if self.total_pieces >= 4 or not self.piece_at(new_pos): return
        if (   self.pieces[self.friendly_icon['Q']]
            or self.pieces[self.enemy_icon['Q']]
            or self.pieces[self.friendly_icon['R']]
            or self.pieces[self.enemy_icon['R']]): return
        try:
            if self.pieces[self.friendly_icon['B'][0].x]%2 == self.pieces[self.enemy_icon['B'][0].x]%2:
                return
        except TypeError: pass
        if self.total_pieces == 3: return
        
        # Check if kings are trapped on each side of pawn wall and bishops cant take pawns

        """   
        
        friendlies_alive = np.append(friendlies_alive, poses)

                
        self.valid_move = {'K':self.king,   'Q':self.queen,  'R':self.rock,
                           'B':self.bishop, 'N':self.knight, 'P':self.pawn}
        self.friendly_icon = {'K':chr(9818-6*self.white_turn), 'Q':chr(9819-6*self.white_turn),
                                'R':chr(9820-6*self.white_turn), 'B':chr(9821-6*self.white_turn),
                                'N':chr(9822-6*self.white_turn), 'P':chr(9823-6*self.white_turn)}
        self.enemy_icon    = {'K':chr(9812+6*self.white_turn), 'Q':chr(9813+6*self.white_turn),
                                'R':chr(9814+6*self.white_turn), 'B':chr(9815+6*self.white_turn),
                                'N':chr(9816+6*self.white_turn), 'P':chr(9817+6*self.white_turn)}
        """

def main():
    board = [['♜','', '', '', '♚',  '', '','♜'],
             ['','', '','', '♟','', '',''],
             ['','','', '', '', '', '',''],
             ['','', '', '','', '♙','♟',''],
             ['','','', '', '', '','',''],
             ['','', '','', '','', '',''],
             ['','', '', '', '', '',  '',''],
             ['♖','', '', '', '♔', '',  '','♖']]
    Chess = ChessGame(board)
    Chess.game_loop()


if __name__ == '__main__':
    main()