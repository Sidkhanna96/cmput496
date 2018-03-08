def resultForBlack(self):
        result = self.negamaxBoolean()
        if self.board.current_player == BLACK:
            return result
        else:
            return not result

    def solve(self, args): 
        global DRAW_WINNER
        DRAW_WINNER = WHITE
        win = self.resultForBlack()
        if win:
            return BLACK
        else:
            DRAW_WINNER = BLACK
            winOrDraw = self.resultForBlack(self)
            if winOrDraw:
                return EMPTY
            else:
                return WHITE

    def color_check(self):
        if(self.board.current_player == 2):
            return "w"
        else:
            return "b"

    def negamaxBoolean(self):
        # if(self.board.end_of_game()):
        if(self.legal_moves_cmd(self.color_check()).split(" ") == ['']):
            return self.isSuccess()
        for m in self.legal_moves_cmd(self.color_check()).split(" "):
            args = [self.color_check(), m]
            # print(args)
            self.play_cmd(args)
            success = not self.negamaxBoolean()
            self.board.undo_move()
            if success:
                return True
        return False

    DRAW_WINNER = BLACK


    def isSuccess(self):
        global DRAW_WINNER
        color = self.score_cmd(self.color_check())
        return (color == self.board.current_player or (color == EMPTY and self.board.current_player == DRAW_WINNER))

    