"""
Module for playing games of Go using GoTextProtocol

This code is based off of the gtp module in the Deep-Go project
by Isaac Henrion and Aamos Storkey at the University of Edinburgh.
"""
import traceback
import sys
import os
utilpath = sys.path[0] + "/../Go4/"
sys.path.append(utilpath)
utilpath = sys.path[0] + "/../util/"
sys.path.append(utilpath)
from gtp_connection import GtpConnection
from board_util_go4 import GoBoardUtilGo4
import numpy as np
import re

class GtpConnectionGo5(GtpConnection):

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
        GtpConnection.__init__(self, go_engine, board, outfile, debug_mode)
        self.commands["prior_knowledge"] = self.prior_knowledge_cmd
        self.commands["genmove"] = self.genmove_cmd
        self.argmap["prior_knowledge"] = (0, 'Usage: prior_knowledge')
        self.argmap["genmove"] = (1, 'Usage: genmove {w,b}')


    def genmove_cmd(self,args):
        self.respond("working")

    def prior_knowledge_cmd(self,args):
        move, probs = self.probability(self.board)

        # print(probs)


        sim_probs = self.sim(probs, move)
        win_rate = self.winrates(probs, move)

        for elem in move:
            print(GoBoardUtilGo4.format_point(self.board._point_to_coord(elem)), sim_probs[elem], win_rate[elem])


    def sim(self, probs, move):

        probs2 = np.zeros(self.board.maxpoint)
        max_prob = max(probs)
        for elem in move:
            probs2[elem] = round(10*probs[elem]/max_prob)

        return probs2

    def winrates(self, probs, move):
        min_val = 0
        max_val = max(probs)

        a = 0.5
        b = 1

        probs2 = np.zeros(self.board.maxpoint)

        for elem in move:
            probs2[elem] = self.convert(probs[elem], min_val, max_val, a, b)

        return probs2

    def convert(self, x, min_val, max_val, a, b):
        final_value = (((b-a)*(x-min_val))/(max_val-min_val)) + a
        return final_value


    def probability(self, board):
        from feature import Features_weight
        from feature import Feature
        assert len(Features_weight) != 0

        #legal moves
        moves = []

        gamma_sum = 0.0

        empty_points = board.get_empty_points()
        # empty_points.append('pass')

        color = board.current_player

        probs = np.zeros(board.maxpoint)
        # return board.maxpoint

        all_board_features = Feature.find_all_features(board)

        for move in empty_points:
            if board.check_legal(move, color) and not board.is_eye(move, color):
                moves.append(move)
                probs[move] = Feature.compute_move_gamma(Features_weight, all_board_features[move])
                gamma_sum += probs[move]
        if len(moves) != 0:
            assert gamma_sum != 0.0
            for m in moves:
                probs[m] = probs[m] / gamma_sum
        return (moves), (probs)
