"""
Module for playing games of Go using GoTextProtocol

This code is based off of the gtp module in the Deep-Go project
by Isaac Henrion and Aamos Storkey at the University of Edinburgh.
"""
import traceback
import sys
import os
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, FLOODFILL
import gtp_connection
import numpy as np
import re

class GtpConnectionGo3(gtp_connection.GtpConnection):

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
        self.commands["policy_moves"] = self.policy_moves_cmd
        self.argmap["go_safe"] = (1, 'Usage: go_safe {w,b}')

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

    def policy_moves_cmd(self, args):
        """
        Return list of policy moves for the current_player of the board
        """
        #ATARI CAPTURE 
        if self.board.last_move != None:
            moves = self.board.last_moves_empty()
            diagonal = self.board._diag_neighbors(self.board.last_move)
            capture_moves = list(set(moves) - set(diagonal))
            capture_moves = GoBoardUtil.filter_moves(self.board,capture_moves, self.go_engine.check_selfatari)

            if(len(capture_moves)==1):
                if(self.board._liberty(capture_moves[0],self.board._points_color(capture_moves[0])) == 1):
                    policy_moves, type_of_move = capture_moves, 'AtariCapture'
                    response = type_of_move + " " + GoBoardUtil.sorted_point_string(policy_moves, self.board.NS)
                    self.respond(response)
                    # self.respond("akjhfjkasdhfkjahsd")
                    return
            
            # # ATARI DEFENCE
            # else:
            #     defence_moves=[]
            #     moves = self.board._neighbors(self.board.last_move)
            #     # moves.extend(board._diag_neighbors2(board.last_move))

        
                
            #     for move in moves:
            #         if(self.board._single_liberty(move,self.board.current_player)!=None):
            #             # print(self.board._single_liberty(move,self.board.current_player))
            #             # print(self.board._point_to_coord(move))
            #             defence_moves.append(self.board._single_liberty(move,self.board.current_player))
                        
            #     if(defence_moves != []):
            #         defence_moves  = GoBoardUtil.filter_moves(self.board, defence_moves, self.go_engine.check_selfatari)
            #         policy_moves, type_of_move =  defence_moves, 'AtariDefense'
            #         response = type_of_move + " " + GoBoardUtil.sorted_point_string(policy_moves, self.board.NS)
            #         self.respond(response)
            #         return

        defence_moves= []
        lm = self.board.last_move
        if lm != None:
            current_play = self.board.current_player
            opponent = GoBoardUtil.opponent(self.board.current_player)
            for elem in self.board._neighbors(lm):
                val = GoBoardUtil.color_to_int(self.board._points_color(elem))
                if current_play == val:
                    # print(self.board._neighbors(elem))
                    # if self.board._neighbors(val) != None:
                    if (self.board._single_liberty(elem, GoBoardUtil.int_to_color(val)) != None):
                        if(self.board._liberty(self.board._single_liberty(elem, GoBoardUtil.int_to_color(val)), GoBoardUtil.int_to_color(val))) > 1:
                            defence_moves.append(self.board._single_liberty(elem, GoBoardUtil.int_to_color(val)))

            ng = self.board._neighbors(lm)
            dg = self.board._diag_neighbors(self.board.last_move)
            all_ng = ng + dg
            # print(all_ng)
            count = 0
            for elem in all_ng:
                val = GoBoardUtil.color_to_int(self.board._points_color(elem))
                if opponent == val:
                    # print(self.board._single_liberty(elem, GoBoardUtil.int_to_color(val)))
                    if (self.board._single_liberty(elem, GoBoardUtil.int_to_color(val)) != None):
                        # print(elem)
                        for i in self.board._neighbors(elem):
                            # print(i)
                            val2 = GoBoardUtil.color_to_int(self.board._points_color(i))
                            if(val2 == opponent):
                                # print(self.board._liberty(i, GoBoardUtil.int_to_color(val2)))
                                if(self.board._liberty(i, GoBoardUtil.int_to_color(val2)) != None):
                                    count += 1
                        # print(count)
                        if (count == 0):
                            defence_moves.append(self.board._single_liberty(elem, GoBoardUtil.int_to_color(val)))
                        count = 0


        # print(self.board.co defence_moves)
        # for v in defence_moves:
        #     print(v)
        defence_moves = GoBoardUtil.filter_moves(self.board,defence_moves, self.go_engine.check_selfatari)
        defence_moves = GoBoardUtil.sorted_point_string(defence_moves, self.board.NS)
        if len(defence_moves) > 0:
            # defence_moves = GoBoardUtil.filter_moves(self.board,defence_moves, self.go_engine.check_selfatari)
            self.respond("AtariDefense " + defence_moves)
            return
                 
        policy_moves, type_of_move = GoBoardUtil.generate_all_policy_moves(self.board,
                                                        self.go_engine.use_pattern,
                                                        self.go_engine.check_selfatari)
        if len(policy_moves) == 0:
            self.respond("Pass")
        else:
            response = type_of_move + " " + GoBoardUtil.sorted_point_string(policy_moves, self.board.NS)
            self.respond(response)
            return
