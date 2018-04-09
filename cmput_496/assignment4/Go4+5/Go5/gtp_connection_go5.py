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


    def prior_knowledge_cmd(self,args):
        move, probs = self.probability(self.board)
        sim_probs = self.sim(probs, move)
        win_rate = self.winrates(probs, move)

        # print("winrates " + str(win_rate))
        wins = np.zeros(self.board.maxpoint)


        for num1 in range(len(move)):
            for num2 in range(0, len(move)-num1-1):
                if move[num2] != move[num2+1]:
                    if win_rate[move[num2]] < win_rate[move[num2+1]]:
                        move[num2], move[num2+1] = move[num2+1], move[num2]
                    elif win_rate[move[num2]]==win_rate[move[num2+1]]:
                        move1 = GoBoardUtilGo4.format_point(self.board._point_to_coord(move[num2]))
                        move2 = GoBoardUtilGo4.format_point(self.board._point_to_coord(move[num2+1]))

                        if(move1[0]>move2[0]):
                            move[num2] , move[num2+1] = move[num2+1] , move[num2]
        for elem in move:
            # print(GoBoardUtilGo4.format_point(self.board._point_to_coord(elem)), sim_probs[elem], win_rate[elem])
            wins[elem] = int(round(sim_probs[elem] * win_rate[elem]))
            # after calculating wins, we need to round simulation
            sim_probs[elem] = int(round(sim_probs[elem]))
            # wins[elem] = sim_probs[elem] * win_rate[elem]

        values = []

        for elem in move:
            # print(elem)
            elem2 = elem
            if elem == 0:
                elem2 = 'Pass'
                # print((elem2), sim_probs[elem], wins[elem])
                values.append(elem2)
                values.append(int(wins[elem]))
                values.append(int(sim_probs[elem]))

            else:
                # print(GoBoardUtilGo4.format_point(self.board._point_to_coord(elem2)), sim_probs[elem], wins[elem])
                values.append(GoBoardUtilGo4.format_point(self.board._point_to_coord(elem)))
                values.append(int(wins[elem]))
                values.append(int(sim_probs[elem]))

        str1 = ' '.join(str(e) for e in values)
        self.respond(''.join(str1))

    def prior_knowledge_cmd_return(self):
        move, probs = self.probability(self.board)
        sim_probs = self.sim(probs, move)
        win_rate = self.winrates(probs, move)

        # print("winrates " + str(win_rate))
        wins = np.zeros(self.board.maxpoint)

        for num1 in range(len(move)):
            for num2 in range(0, len(move)-num1-1):
                if move[num2] != move[num2+1]:
                    if win_rate[move[num2]] < win_rate[move[num2+1]]:
                        move[num2], move[num2+1] = move[num2+1], move[num2]
                    elif win_rate[move[num2]]==win_rate[move[num2+1]]:
                        move1 = GoBoardUtilGo4.format_point(self.board._point_to_coord(move[num2]))
                        move2 = GoBoardUtilGo4.format_point(self.board._point_to_coord(move[num2+1]))

                        if(move1[0]>move2[0]):
                            move[num2] , move[num2+1] = move[num2+1] , move[num2]


        for elem in move:
            # print(GoBoardUtilGo4.format_point(self.board._point_to_coord(elem)), sim_probs[elem], win_rate[elem])
            wins[elem] = int(round(sim_probs[elem] * win_rate[elem]))
            # after calculating wins, we need to round simulation
            sim_probs[elem] = int(round(sim_probs[elem]))
            # wins[elem] = sim_probs[elem] * win_rate[elem]

        values2 = []

        for elem in move:
            values = []
            # print(elem)
            elem2 = elem
            if elem == 0:
                elem2 = 'Pass'
                # print((elem2), sim_probs[elem], wins[elem])
                values.append(elem2)
                values.append(wins[elem])
                values.append(sim_probs[elem])
                values2.append(values)
            else:
                # print(GoBoardUtilGo4.format_point(self.board._point_to_coord(elem2)), sim_probs[elem], wins[elem])
                values.append(GoBoardUtilGo4.format_point(self.board._point_to_coord(elem)))
                values.append(wins[elem])
                values.append(sim_probs[elem])
                values2.append(values)

        return ((values2))

    def sim(self, probs, move):

        probs2 = np.zeros(self.board.maxpoint)
        max_prob = max(probs)
        for elem in move:
            probs2[elem] = 10*probs[elem]/max_prob

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
        # print(Features_weight)
        assert len(Features_weight) != 0

        #legal moves
        moves = []

        gamma_sum = 0.0

        legal_moves_broad = Feature.legal_moves_on_board(board)
        legal_moves = []

        for elem in legal_moves_broad:
            if not board.is_eye(elem, board.current_player):
                legal_moves.append(elem)

        legal_moves.append(0)

        probs = np.zeros(board.maxpoint)

        feature_legal_move = Feature.find_all_features(board)

        for move in legal_moves:
            if move == 0:
                probs[move] = Feature.compute_move_gamma(Features_weight, feature_legal_move['PASS'])
            else:
                probs[move] = Feature.compute_move_gamma(Features_weight, feature_legal_move[move])
            gamma_sum += probs[move]

        if len(legal_moves) != 0.0:
            assert gamma_sum != 0.0
            for m in legal_moves:
                probs[m] = probs[m]/gamma_sum

        return legal_moves, probs


        # empty_points = board.get_empty_points()

        # color = board.current_player

        # probs = np.zeros(board.maxpoint)
        # # return board.maxpoint

        # all_board_features = Feature.find_all_features(board)

        # for move in empty_points:
        #     if board.check_legal(move, color) and not board.is_eye(move, color):
        #         moves.append(move)
        #         probs[move] = Feature.compute_move_gamma(Features_weight, all_board_features[move])
        #         gamma_sum += probs[move]
        # if len(moves) != 0:
        #     assert gamma_sum != 0.0
        #     for m in moves:
        #         probs[m] = probs[m] / gamma_sum
        # return (moves), (probs)

    def genmove_cmd(self,args):
        moves = self.prior_knowledge_cmd_return()
        if moves is not None:
            # self.respond(moves[0][0])
            if moves[0][0] == 'Pass':
                self.respond('pass')
            else:
                self.respond(moves[0][0])
