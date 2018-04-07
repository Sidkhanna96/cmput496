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
        self.respond("Working")
        