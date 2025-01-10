import numpy as np

class OthelloGame:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_player = 1  # 1 = 黒, -1 = 白

    def initialize_board(self):
        board = np.zeros((8, 8), dtype=int)
        board[3][3], board[4][4] = -1, -1  # 白
        board[3][4], board[4][3] = 1, 1    # 黒
        return board

    def get_valid_moves(self, player):
        valid_moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for x in range(8):
            for y in range(8):
                if self.board[x][y] != 0:
                    continue
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    found_opponent = False
                    while 0 <= nx < 8 and 0 <= ny < 8:
                        if self.board[nx][ny] == -player:
                            found_opponent = True
                        elif self.board[nx][ny] == player and found_opponent:
                            valid_moves.append((x, y))
                            break
                        else:
                            break
                        nx, ny = nx + dx, ny + dy
        return valid_moves

    def make_move(self, move, player):
        x, y = move
        self.board[x][y] = player
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            stones_to_flip = []
            while 0 <= nx < 8 and 0 <= ny < 8:
                if self.board[nx][ny] == -player:
                    stones_to_flip.append((nx, ny))
                elif self.board[nx][ny] == player:
                    for fx, fy in stones_to_flip:
                        self.board[fx][fy] = player
                    break
                else:
                    break
                nx, ny = nx + dx, ny + dy

    def is_game_over(self):
        return len(self.get_valid_moves(1)) == 0 and len(self.get_valid_moves(-1)) == 0

    def get_winner(self):
        black_score = np.sum(self.board == 1)
        white_score = np.sum(self.board == -1)
        if black_score > white_score:
            return 1  # 黒の勝ち
        elif white_score > black_score:
            return -1  # 白の勝ち
        else:
            return 0  # 引き分け
