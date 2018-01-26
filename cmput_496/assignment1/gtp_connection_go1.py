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
from collections import defaultdict

class GtpConnectionGo1(gtp_connection.GtpConnection):

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
        self.commands["hello"] = self.hello_cmd
        self.commands["score"] = self.score
    

    def hello_cmd(self, args):
        """ Dummy Hello Command """
        self.respond("Hello! " + self.go_engine.name)

    def score(self, args):	
        # EmptyPoints = []
        # GoBoard = self.board.get_twoD_board()
        # for row in range(len(GoBoard)):
        # 	for position in range(len(GoBoard[row])):
        # 		if(GoBoard[row][position] == 0):
        # 			value =  self.board.NS*row + position
        # 			EmptyPoints.append(value)

        # print(EmptyPoints)
        # print(self.board.get_empty_positions(1))

        GoBoard = self.board

        # Initalize Variables
        whiteposition = 2
        whitescore = self.komi
        blackposition = 1
        blackscore = 0


        # Count of Stones
        for row in GoBoard.get_twoD_board():
            for position in row:
                if(position == whiteposition):
                    whitescore +=1
                elif(position == blackposition):
                    blackscore +=1

        black = GoBoard.get_empty_positions(1)
        white = GoBoard.get_empty_positions(2)



        # print(black)
        # print(white)

        empty = list(set(black).union(white))

        valid_moves_empty = []
        valid_position = []

        for positions in empty:
        	neighbours = GoBoard._neighbors(positions)
        	for i in neighbours:
        		if(i in empty):
        			valid_position.append(i)
        	valid_moves_empty.append(valid_position)
        	valid_position = []

        # print(empty)
        # print(valid_moves_empty)

        dictionary = {}

        # print(len(empty), len(valid_moves_empty))

        for i in range(len(empty)):
        	dictionary[empty[i]] = valid_moves_empty[i]

        # Empty points: Valid neighbours
        # print(dictionary)

        list_Territory = []
        Territory = []

        #print(next(iter(dictionary.values())))
        #print(next(iter(dictionary)))

    	# Territory.append(next(iter(dictionary)))
        while(len(dictionary) > 0):
    	    Territory = self.dfs(dictionary, next(iter(dictionary)), [])
    	    for n in Territory:
    	    	dictionary.pop(n)
    	    list_Territory.append(Territory)
    	    Territory = []

    	# print(list_Territory, '\n')
        color_territory = []
        color_of_territory = []
    	# dictionary_color_territory = defaultdict(list)

        for ter in list_Territory:
       		for val in ter:
       			check_color = (GoBoard._neighbors(val))
       			for i in check_color:
       				if(GoBoard.get_color(i) == 1 or GoBoard.get_color(i) == 2):
       					color_territory.append(GoBoard.get_color(i))
       		# print(color_territory)
       		color_of_territory.append(color_territory)
       		color_territory = []

        # print(list_Territory, '\n\n', color_of_territory)

        size_of_territory = []
        color = []
        i=0

        while(i < len(list_Territory)):
        	size_of_territory.append(len(list_Territory[i]))
        	if 1 not in color_of_territory[i]: whitescore += size_of_territory[i]
        	elif 2 not in color_of_territory[i]: blackscore += size_of_territory[i]

        	i = i + 1
        # print(size_of_territory, "\n\n", color)
        


        ############# ############# #############
        # Final print score logic DO NOT CHANGE
        if(blackscore>whitescore):
            self.respond(' B+' + str(blackscore-whitescore))
        elif (blackscore<whitescore):
            self.respond(' W+' + str(whitescore-blackscore))
        else:
            self.respond(' ' + str(0))

    def dfs(self, graph, node, visited):
    	if node not in visited:
    		visited.append(node)
    		for n in graph[node]:
    			self.dfs(graph, n, visited)
    	return visited