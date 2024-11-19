from santoriniGame.game import Game


class RemoteGame(Game):
    def __init__(self):
        super().__init__(win=None, no_render=True)
        self.bot = None
        self.last_move_start_x = None
        self.last_move_start_y = None
        self.last_move_x = None
        self.last_move_y = None
        self.last_build_x = None
        self.last_build_y = None

    def _move(self, row: int, col: int):
        self.last_move_start_x = self.selected.col
        self.last_move_start_y = self.selected.row
        self.last_move_x = col
        self.last_move_y = row
        super()._move(row, col)
        
    def _build(self, row: int, col: int):
        self.last_build_x = col
        self.last_build_y = row
        super()._build(row, col)