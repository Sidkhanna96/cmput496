"""
Module for playing games of Go using GoTextProtocol

This code is based off of the gtp module in the Deep-Go project
by Isaac Henrion and Aamos Storkey at the University of Edinburgh.
"""
from multiprocessing import Process
import time
import traceback
import sys
import os
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, FLOODFILL
import gtp_connection
import numpy as np
import re

class GtpConnectionGo2(gtp_connection.GtpConnection):

    def __init__(self, go_engine, board, outfile = 'gtp_log', debug_mode = False):
        """
        GTP connection of Go1

        Parameters
        ----------
        go_engine : GoPlayer
            a program that is capable of playing go by reading GTP commands
        komi : float
            komi used for the current game
        board: GoBoard
            SIZExSIZE array representing the current board state
        """
        gtp_connection.GtpConnection.__init__(self, go_engine, board, outfile, debug_mode)
        self.commands["go_safe"] = self.safety_cmd
        self.commands["timelimit"] = self.timelimit
        self.commands["genmove"] = self.genmove
        self.commands["solve"] = self.solve

        self.argmap["go_safe"] = (1, 'Usage: go_safe {w,b}')
        self.argmap["timelimit"] = (1, 'Usage: timelimit {seconds}')
        self.argmap["genmove"] = (1, 'Usage: genmove {player}')
        self.timelimit = 30
        self.time=0
        self.winning = False
        self.currentplayer = BLACK
        self.final_winner=[]
        self.dic={}
        self.oldscore=0


    def safety_cmd(self, args):
        try:
            color= GoBoardUtil.color_to_int(args[0].lower())
            safety_list = self.board.find_safety(color)
            safety_points = []
            for point in safety_list:
                x,y = self.board._point_to_coord(point)
                safety_points.append(GoBoardUtil.format_point((x,y)))
            self.respond(safety_points)
        except Exception as e:
            self.respond('Error: {}'.format(str(e)))

    def timelimit(self,*args):
        """
        This command sets the maximum time to use for all following genmove or solve commands

        Arguments
        ---------
        args[0] : {seconds}
        """
        try:
            # print(args[0])
            if(args[0][0].isalpha()):
                raise ValueError("Value Is Not A Number")
            if(len(args)>1 or len(args[0])>1):
                raise ValueError("Invalid command line arguments")

            seconds = int(args[0][0])
            # print(seconds)
            if(seconds>100 or seconds<1):
                raise ValueError("Value Is Out Of Bounds")
            self.timelimit = seconds
        except Exception as e:
            self.respond('Error: {}'.format(str(e)))


    def genmove(self,args):
        #original code from util
        
        """
        generate a move for the specified color

        Arguments
        ---------
        args[0] : {'b','w'}
            the color to generate a move for
            it gets converted to  Black --> 1 White --> 2
            color : {0,1}
            board_color : {'b','w'}
        """
        try:
            board_color = args[0].lower()
            color = GoBoardUtil.color_to_int(board_color)
            self.debug_msg("Board:\n{}\nko: {}\n".format(str(self.board.get_twoD_board()),
                                                          self.board.ko_constraint))
            
            solver_color,solver_move = self.solve("1")
            move = self.go_engine.get_move(self.board, color)
            if move is None:
                self.respond("pass")
                return

            if(solver_color==self.color_convert(color)):
                moves = list(GoBoardUtil.move_to_coord(solver_move,self.board.size))
                solver_move = self.board._coord_to_point(moves[0],moves[1])
                move = solver_move

            elif not self.board.check_legal(move, color):
                move = self.board._point_to_coord(move)
                board_move = GoBoardUtil.format_point(move)
                self.respond("Illegal move: {}".format(board_move))
                raise RuntimeError("Illegal move given by engine")

            # move is legal; play it
            self.board.move(move,color)

            self.debug_msg("Move: {}\nBoard: \n{}\n".format(move, str(self.board.get_twoD_board())))
            move = self.board._point_to_coord(move)
            board_move = GoBoardUtil.format_point(move)
            self.respond(board_move)
        except Exception as e:
            self.respond('Error: {}'.format(str(e)))

    def resultForBlack(self):
        self.currentplayer = self.board.current_player
        result = self.negamaxBoolean()
        if self.board.current_player == BLACK:
            return result
        else:
            return not result

    def solve(self,args):
        self.winning = False
        self.currentplayer = BLACK
        self.final_winner=[]
        self.oldscore=0
        self.time = time.time()
        self.solver()
    
        try:
            length = len(self.final_winner)-1
            
            if(self.color_check()==self.final_winner[length][0]):
                if(self.final_winner[0][0]==self.final_winner[length][0]):
                    self.respond("{} {}".format(self.final_winner[0][0],self.final_winner[0][1]))
                    return self.final_winner[0][0],self.final_winner[0][1]
                else:
                    self.respond("{} {}".format(self.final_winner[length][0],self.final_winner[length][1]))
                    return self.final_winner[length][0],self.final_winner[length][1]
            else:
                self.respond(self.final_winner[length][0])
                return self.final_winner[length][0],None
        except:
            self.respond("unknown")
            return "unknown",None
        

    def solver(self): 
        global DRAW_WINNER
        DRAW_WINNER = WHITE
        win = self.resultForBlack()
        return
        # if win:
        #     return BLACK
        # else:
        #     DRAW_WINNER = BLACK
        #     winOrDraw = self.resultForBlack()
        #     if winOrDraw:
        #         return EMPTY
        #     else:
        #         return WHITE

    def color_check(self):
        if(self.board.current_player == 2):
            return "w"
        else:
            return "b"
   
    def color_convert(self,color):
        if(color == 2):
            return "w"
        else:
            return "b"
    
    def negamaxBoolean(self):
        # self.respond(self.legal_moves_cmd(self.color_check())
        # if (len(self.legal_moves_cmd(self.color_check())) == 0 or self.legal_moves_cmd(self.color_check())==None):
        #     return self.isSuccess()    
        #S, E, S_eyes = self.board.find_S_and_E(BLACK)
        # print(GoBoardUtil.format_point(1,1))
        # return
        elapsed_time = time.time() - self.time
        if(elapsed_time>=self.timelimit):
            return

        if(self.legal_moves_cmd(self.color_check()).split(" ")==['']):
            return self.isSuccess()
       
        if(self.winning == True):
            return True
            
        for m in self.legal_moves_cmd(self.color_check()).split(" "):
            args = [self.color_check(), m]
            self.play_cmd(args)
            success = not self.negamaxBoolean()
            try:
                self.board.undo_move()  
            except:
                pass

            if success:
                self.winning=True
                self.final_winner.append(args)
                
                return True

            self.final_winner.append(args)
            
        return False

    DRAW_WINNER = BLACK

    def isSuccess(self):
        global player
        global player_score
        global DRAW_WINNER
       
        #black
        color = self.board.score(self.go_engine.komi)
        size = self.board.size**2
        
        player = color[0]
        player_score = color[1]
        
        if(player_score>size/2 and player_score>self.oldscore):
            self.oldscore = player_score
            return True
        
        self.oldscore = player_score
        return False