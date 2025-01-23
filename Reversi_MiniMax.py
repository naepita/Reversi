import flet as ft
import numpy as np
import random
import time  # <-- 2秒待機のため
from itertools import chain

#オセロの内部を定義
class OthelloGame:
    def __init__(self):
        self.board_size = 8
        self.DIRECTIONS = [
            (-1, 0),   # 上
            (1, 0),    # 下
            (0, -1),   # 左
            (0, 1),    # 右
            (-1, -1),  # 左上
            (-1, 1),   # 右上
            (1, -1),   # 左下
            (1, 1),    # 右下
        ]
        self.board_state = None
        self.current_player = None
        self.user_player = None
        self.ai_player = None
        self.valid_moves = []
        self.white_count = 0
        self.black_count = 0
        self.flippable_pos = []

    #ボードを初期化
    def initialize_board(self):
        board = np.full((self.board_size+2, self.board_size+2), "w", dtype=object)
        board[1:-1, 1:-1] = 0
        c = self.board_size // 2
        board[c, c] = 1
        board[c+1, c+1] = 1
        board[c, c+1] = -1
        board[c+1, c] = -1
        return board

    #ゲームを初期化
    def initialize_game(self, first_player):
        self.current_player = first_player
        self.board_state = self.initialize_board()
        self.valid_moves = self.find_valid_moves(self.board_state, self.current_player)
        self.white_count, self.black_count = self.count_stones(self.board_state)
        self.flippable_pos = []

    #プレイヤーの切り替え
    def change_player(self, current_player):
        return -current_player

    #石を数える
    def count_stones(self, board_state):
        flat = list(chain.from_iterable(board_state))
        return flat.count(1), flat.count(-1)

    #石の数から勝者を決める
    def judge_winner(self):
        if self.white_count > self.black_count:
            return "白の勝ちです！"
        elif self.black_count > self.white_count:
            return "黒の勝ちです！"
        else:
            return "引き分けです！"

    #石を置けるかを判定
    def can_place_stone(self, board, row, col, player):
        if board[row][col] != 0:
            return False
        for dr, dc in self.DIRECTIONS:
            r, c = row + dr, col + dc
            flipped_count = 0
            while 0 <= r < (self.board_size+2) and 0 <= c < (self.board_size+2) and board[r][c] == -player:
                r += dr
                c += dc
                flipped_count += 1
            if flipped_count > 0:
                if 0 <= r < (self.board_size+2) and 0 <= c < (self.board_size+2):
                    if board[r][c] == player:
                        return True
        return False

    #石が置けるマスを探す
    def find_valid_moves(self, board, player):
        valid = []
        for r in range(1, self.board_size+1):
            for c in range(1, self.board_size+1):
                if self.can_place_stone(board, r, c, player):
                    valid.append((r, c))
        return valid

    #ひっくり返せる場所を探す
    def find_flippable(self, board, row, col, player):
        flippable = []
        for dr, dc in self.DIRECTIONS:
            r, c = row + dr, col + dc
            tmp = []
            while 0 <= r < (self.board_size+2) and 0 <= c < (self.board_size+2) and board[r][c] == -player:
                tmp.append((r, c))
                r += dr
                c += dc
            if len(tmp) > 0:
                if 0 <= r < (self.board_size+2) and 0 <= c < (self.board_size+2) and board[r][c] == player:
                    flippable.extend(tmp)
        return flippable

    #オセロの状態を更新
    def update_state(self, row, col):
        self.board_state[row][col] = self.current_player
        self.flippable_pos = self.find_flippable(self.board_state, row, col, self.current_player)
        for (r, c) in self.flippable_pos:
            self.board_state[r][c] = self.current_player

        self.white_count, self.black_count = self.count_stones(self.board_state)

        nxt = self.change_player(self.current_player)
        nxt_valid = self.find_valid_moves(self.board_state, nxt)
        if not nxt_valid:
            nxt2 = self.change_player(nxt)
            nxt2_valid = self.find_valid_moves(self.board_state, nxt2)
            if not nxt2_valid:
                self.current_player = 0  # 終了
                self.valid_moves = []
                return
            else:
                self.current_player = nxt2
                self.valid_moves = nxt2_valid
        else:
            self.current_player = nxt
            self.valid_moves = nxt_valid

    #ミニマックス法を用いたAI
    def ai_move(self, depth=2):
        moves = self.find_valid_moves(self.board_state, self.current_player)
        if not moves:
            return None

        if self.current_player == 1:
            best_val = float('-inf')
        else:
            best_val = float('inf')
        best_move = None

        for (r, c) in moves:
            board_copy = np.copy(self.board_state)
            self.simulate_move(board_copy, r, c, self.current_player)
            val = self.minimax(board_copy, depth - 1,
                               self.change_player(self.current_player),
                               alpha=float('-inf'), beta=float('inf'))
            if self.current_player == 1:
                if val > best_val:
                    best_val = val
                    best_move = (r, c)
            else:
                if val < best_val:
                    best_val = val
                    best_move = (r, c)
        return best_move

    #ボードの状態をコピー
    def simulate_move(self, board, row, col, player):
        board[row][col] = player
        to_flip = self.find_flippable(board, row, col, player)
        for (r, c) in to_flip:
            board[r][c] = player

    #盤面を評価
    def minimax(self, board, depth, player, alpha, beta):
        if depth == 0 or self.is_game_over(board):
            return self.evaluate_board(board)
        moves = self.find_valid_moves(board, player)
        if not moves:
            return self.minimax(board, depth, self.change_player(player), alpha, beta)

        if player == 1:  
            value = float('-inf')
            for (r, c) in moves:
                board_copy = np.copy(board)
                self.simulate_move(board_copy, r, c, player)
                value = max(value, self.minimax(board_copy, depth - 1,
                                                self.change_player(player), alpha, beta))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:  
            value = float('inf')
            for (r, c) in moves:
                board_copy = np.copy(board)
                self.simulate_move(board_copy, r, c, player)
                value = min(value, self.minimax(board_copy, depth - 1,
                                                self.change_player(player), alpha, beta))
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    #ゲームオーバー
    def is_game_over(self, board):
        v1 = self.find_valid_moves(board, 1)
        v2 = self.find_valid_moves(board, -1)
        return (not v1) and (not v2)

    #評価値を計算
    def evaluate_board(self, board):
        flat = list(chain.from_iterable(board))
        w = flat.count(1)
        b = flat.count(-1)
        return w - b

#GUIを定義
class GUI:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page_width = 1000
        self.page_height = 800
        self.grid_size = 8
        self.grid = []
        self.create_board()
        self.create_buttons()
        self.join_GUI()
        self.isgame = False
        self.game = None

    #オセロ盤を作成
    def create_board(self):
        col_controls = []
        self.grid_px = self.page_height * 0.75 // 8 * 0.95

        for row in range(self.grid_size):
            row_controls = []
            for col in range(self.grid_size):
                row_controls.append(
                    ft.Container(
                        content=None,
                        width=self.grid_px,
                        height=self.grid_px,
                        bgcolor="green",
                        border=ft.border.all(2, "black"),
                        ink=True,
                        on_click=lambda e, r=row, c=col: self.handle_click(r, c)
                    )
                )
            self.grid.append(row_controls)
            col_controls.append(
                ft.Row(
                    controls=row_controls,
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER))

        self.board_container = ft.Container(
            content=ft.Column(
                controls=col_controls,
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            width=self.page_height*0.75,
            height=self.page_height*0.75,
            bgcolor="black",
            border_radius=ft.border_radius.all(10),
            alignment=ft.alignment.center
        )

    #ボタンなどを作成
    def create_buttons(self):
        self.change_switch = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("ノーマルモード"),
                    ft.Switch(),  # AIモード ON/OFF
                    ft.Text("AI対戦モード")
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            bgcolor="white",
            border=ft.border.all(2, "black"),
            margin=ft.margin.all(5),
            border_radius=ft.border_radius.all(10),
            expand=1,
        )

        self.info_text = ft.Container(
            content=ft.Text("info_text", size=20),
            bgcolor="white",
            border=ft.border.all(2, "black"),
            margin=ft.margin.all(5),
            border_radius=ft.border_radius.all(10),
            alignment=ft.alignment.center,
            expand=4,
        )

        self.othello_count = ft.Container(
            content=ft.Text("白: 枚 黒: 枚", size=20),
            bgcolor="white",
            border=ft.border.all(2, "black"),
            margin=ft.margin.all(5),
            border_radius=ft.border_radius.all(10),
            alignment=ft.alignment.center,
            expand=4,
        )

        self.control_buttons = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Button(
                        text="スタート",
                        expand=5,
                        on_click=self.start_game
                    ),
                    ft.Button(
                        text="リセット",
                        expand=5,
                        on_click=self.reset_game
                    )
                ],
            ),
            bgcolor="white",
            border=ft.border.all(2, "black"),
            border_radius=ft.border_radius.all(10),
            margin=ft.margin.all(5),
            expand=1,
        )

        self.buttons = ft.Column(
            controls=[
                self.change_switch,
                self.info_text,
                self.othello_count,
                self.control_buttons
            ],
            spacing=0
        )

    #GUIを結合
    def join_GUI(self):
        self.gui_container = ft.Container(
            content=ft.Row(
                controls=[
                    self.board_container,
                    ft.Container(
                        content=self.buttons,
                        bgcolor="#008800",
                        height=self.page_height,
                        expand=True
                    )
                ],
                spacing=0,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            expand=True,
            bgcolor="#008800",
            border_radius=ft.border_radius.all(5)
        )

    #スタートボタンの処理
    def start_game(self, e):
        if not self.isgame:
            self.game = OthelloGame()
            is_ai_mode = self.change_switch.content.controls[1].value
            first_player = random.choice([-1, 1])
            self.game.initialize_game(first_player)

            if is_ai_mode:
                self.game.user_player = first_player
                self.game.ai_player = -first_player
            else:
                self.game.user_player = None
                self.game.ai_player = None

            self.initialize_game()
            self.isgame = True

    #リセットボタンの処理
    def reset_game(self, e):
        if self.isgame:
            self.del_valid_moves()
            # 全マスをクリア
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    self.grid[r][c].content = None
                    self.grid[r][c].border = ft.border.all(2, "black")
            self.info_text.content = ft.Text("ゲームをリセットしました。スタートボタンを押してください。", size=20)
            self.othello_count.content = ft.Text("黒: 2\n白: 2", size=20)
            self.isgame = False
            self.page.update()

    #盤面の初期化
    def initialize_game(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                val = self.game.board_state[row+1][col+1]
                if val == 1:
                    self.grid[row][col].content = ft.CircleAvatar(
                        radius=self.grid_px // 2, bgcolor="white"
                    )
                    self.grid[row][col].on_click = None
                elif val == -1:
                    self.grid[row][col].content = ft.CircleAvatar(
                        radius=self.grid_px // 2, bgcolor="black"
                    )
                    self.grid[row][col].on_click = None
                else:
                    self.grid[row][col].content = None
                    self.grid[row][col].on_click = lambda e, r=row, c=col: self.handle_click(r, c)

        msg = "白が先行です" if self.game.current_player == 1 else "黒が先行です"
        self.info_text.content = ft.Text(msg, size=20)

        self.othello_count.content = ft.Text(
            f"黒:{self.game.black_count}\n白:{self.game.white_count}",
            size=20
        )

        self.draw_valid_moves()
        self.page.update()

    #石を置ける場所を描画
    def draw_valid_moves(self):
        for (r, c) in self.game.valid_moves:
            self.grid[r-1][c-1].border = ft.border.all(2, "yellow")

    #描画を削除
    def del_valid_moves(self):
        for (r, c) in self.game.valid_moves:
            self.grid[r-1][c-1].border = ft.border.all(2, "black")

    #マスのクリック処理
    def handle_click(self, row, col):
        if not self.isgame:
            return

        cp = self.game.current_player
        if cp == 0:
            return

        is_ai_mode = self.change_switch.content.controls[1].value
        if is_ai_mode and cp == self.game.ai_player:
            print("AIのターンです。ユーザーは置けません。")
            return

        br, bc = row + 1, col + 1
        if (br, bc) not in self.game.valid_moves:
            print("そこには置けません！")
            return

        self.del_valid_moves()

        self.game.update_state(br, bc)
        self.draw_circle(row, col, cp)
        for (rr, cc) in self.game.flippable_pos:
            self.draw_circle(rr-1, cc-1, cp)

        self.othello_count.content = ft.Text(
            f"黒:{self.game.black_count}\n白:{self.game.white_count}",
            size=20
        )

        if self.game.current_player == 0:
            self.info_text.content = ft.Text(
                f"両者に置ける場所がありません。\n{self.game.judge_winner()}",
                size=20
            )
            self.page.update()
            return

        msg = "白のターンです" if self.game.current_player == 1 else "黒のターンです"
        self.info_text.content = ft.Text(msg, size=20)

        if is_ai_mode and self.game.current_player == self.game.ai_player and self.game.current_player != 0:
            self.draw_valid_moves()
            self.page.update()

            time.sleep(1)

            self.del_valid_moves()
            ai_pos = self.game.ai_move(depth=2)
            if ai_pos is not None:
                old_cp = self.game.current_player 
                self.game.update_state(ai_pos[0], ai_pos[1])
                self.draw_circle(ai_pos[0]-1, ai_pos[1]-1, old_cp)
                for (rr, cc) in self.game.flippable_pos:
                    self.draw_circle(rr-1, cc-1, old_cp)

                self.othello_count.content = ft.Text(
                    f"黒:{self.game.black_count}\n白:{self.game.white_count}",
                    size=20
                )
                if self.game.current_player == 0:
                    self.info_text.content = ft.Text(
                        f"両者に置ける場所がありません。\n{self.game.judge_winner()}",
                        size=20
                    )
                else:
                    msg2 = "白のターンです" if self.game.current_player == 1 else "黒のターンです"
                    self.info_text.content = ft.Text(msg2, size=20)

        self.draw_valid_moves()
        self.page.update()

    #石を描画
    def draw_circle(self, row, col, player):
        if player == 1:
            self.grid[row][col].content = ft.CircleAvatar(
                radius=self.grid_px // 2, bgcolor="white"
            )
        else:
            self.grid[row][col].content = ft.CircleAvatar(
                radius=self.grid_px // 2, bgcolor="black"
            )
        self.grid[row][col].on_click = None


def main(page: ft.Page):
    gui = GUI(page)
    page.title = "オセロ"
    page.window.width = gui.page_width
    page.window.height = gui.page_height
    page.add(gui.gui_container)

ft.app(target=main)
