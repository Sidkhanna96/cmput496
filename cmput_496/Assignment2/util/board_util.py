EMPTY = 0
BLACK = 1
WHITE = 2
BORDER = 3
FLOODFILL = 4
import numpy as np
import random
import copy

class GoBoardUtil(object):
    
    @staticmethod
    def generate_legal_moves(board,color):
        """
        generate a list of legal moves

        Arguments
        ---------
        board : np.array
            a SIZExSIZE array representing the board
        color : {'b','w'}
            the color to generate the move for.
        """
        moves = board.get_empty_points()
        num_moves = len(moves)
        np.random.shuffle(moves)
        illegal_moves = []

        for i in range(num_moves):
            if board.check_legal(moves[i],color):
                continue
            else:
                illegal_moves.append(i)
        legal_moves = np.delete(moves,illegal_moves)
        gtp_moves=[]
        for point in legal_moves:
            x,y = board._point_to_coord(point)
            gtp_moves.append(GoBoardUtil.format_point((x,y)))
        sorted_moves = ' '.join(sorted(gtp_moves))
        return sorted_moves
    
    
    @staticmethod       
    def generate_random_move(board, color, is_eye_filter):
        """
        generate a random move

        Arguments
        ---------
        board : np.array
            a SIZExSIZE array representing the board
        color : {'b','w'}
            the color to generate the move for.
        """
        moves = board.get_empty_points()
        num_moves = len(moves)
        np.random.shuffle(moves)
        for i in range(num_moves):
            if is_eye_filter and board.is_eye(moves[i],color):
                continue
            move = moves[i]
            legal = board.check_legal(move,color)
            if not legal:
                continue
            return move
        return None
    
    @staticmethod
    def format_point(move):
        """
        Return coordinates as a string like 'a1', or 'pass'.

        Arguments
        ---------
        move : (row, col), or None for pass

        Returns
        -------
        The move converted from a tuple to a Go position (e.g. D4)
        """
        column_letters = "abcdefghjklmnopqrstuvwxyz"
        if move is None:
            return "pass"
        row, col = move
        if not 0 <= row < 25 or not 0 <= col < 25:
            raise ValueError
        return    column_letters[col-1]+ str(row) 
        
    @staticmethod
    def move_to_coord(point, board_size):
        """
        Interpret a string representing a point, as specified by GTP.

        Arguments
        ---------
        point : str
            the point to convert to a tuple
        board_size : int
            size of the board

        Returns
        -------
        a pair of coordinates (row, col) in range(1, board_size+1)

        Raises
        ------
        ValueError : 'point' isn't a valid GTP point specification for a board of size 'board_size'.
        """
        if not 0 < board_size <= 25:
            raise ValueError("board_size out of range")
        try:
            s = point.lower()
        except Exception:
            raise ValueError("invalid point")
        if s == "pass":
            return None
        try:
            col_c = s[0]
            if (not "a" <= col_c <= "z") or col_c == "i":
                raise ValueError
            if col_c > "i":
                col = ord(col_c) - ord("a")
            else:
                col = ord(col_c) - ord("a") + 1
            row = int(s[1:]) 
            if row < 1:
                raise ValueError
        except (IndexError, ValueError):
            raise ValueError("invalid point: '%s'" % s)
        if not (col <= board_size and row <= board_size):
            raise ValueError("point is off board: '%s'" % s)
        return row, col
    
    @staticmethod
    def opponent(color):
        opponent = {WHITE:BLACK, BLACK:WHITE} 
        try:
            return opponent[color]    
        except:
            raise ValueError("Wrong color provided for opponent function")
            
    @staticmethod
    def color_to_int(c):
        """convert character representing player color to the appropriate number"""
        color_to_int = {"b": BLACK , "w": WHITE, "e":EMPTY, "BORDER":BORDER, "FLOODFILL":FLOODFILL}
        try:
           return color_to_int[c] 
        except:
            raise ValueError("Valid color characters are: b, w, e, BORDER and FLOODFILL. please provide the input in this format ")
    
    @staticmethod
    def int_to_color(i):
        """convert number representing player color to the appropriate character """
        int_to_color = {BLACK:"b", WHITE:"w", EMPTY:"e", BORDER:"BORDER", FLOODFILL:"FLOODFILL"}
        try:
           return int_to_color[i] 
        except:
            raise ValueError("Provided integer value for color is invalid")
         
    @staticmethod
    def copyb2b(board,copy_board):
        """Return an independent copy of this Board."""
        copy_board.__dict__ = copy.deepcopy(board.__dict__)
        assert copy_board.board.all() == board.board.all()
        return copy_board
