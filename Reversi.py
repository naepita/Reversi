import flet as ft
import numpy as np
import random
from itertools import chain 

class OthelloGame:
    def __init__(self):
        self.board_size = 8
        self.DIRECTIONS = [
            (-1, 0),  # 上
            (1, 0),   # 下
            (0, -1),  # 左
            (0, 1),   # 右
            (-1, -1), # 左上
            (-1, 1),  # 右上
            (1, -1),  # 左下
            (1, 1),   # 右下
        ]
        self.initialize_game()

    #先行を決める
    def decide_first(self):
        #-1で黒が先行、1で白が先行
        return random.choice([-1, 1])
    
    #オセロの状態を初期化
    def initialize_board(self):
        board = np.full((self.board_size+2, self.board_size+2), "w", dtype=object)
        board[1: -1, 1: -1] = 0
        center = self.board_size // 2
        board[center, center] = 1
        board[center+1, center+1] = 1
        board[center, center+1] = -1
        board[center+1, center] = -1

        for row in board:
            print(" ".join(f"{str(cell):>2}" for cell in row))
        
        return board
    
    #ゲームの初期化
    def initialize_game(self):
        self.current_player = -1
        print(self.current_player)
        self.board_state = self.initialize_board()
        self.valid_moves = self.find_valid_moves(self.board_state, self.current_player)
        print(self.valid_moves)
        self.white_count, self.black_count = self.count_stones(self.board_state)
        print("石の数", self.white_count, self.black_count)
    
    #オセロの状態を更新
    def update_state(self, row, col):
        #石が置かれた場所の状態を更新
        if self.current_player == 1:
            self.board_state[row][col] = 1
        else:
            self.board_state[row][col] = -1

        #ひっくり返せる場所を更新
        self.flippable_pos = self.find_flippable(self.board_state, row, col, self.current_player)
        for row, col in self.flippable_pos:
            if self.current_player == 1:
                self.board_state[row][col] = 1
            else:
                self.board_state[row][col] = -1

        for row in self.board_state:
            print(" ".join(f"{str(cell):>2}" for cell in row))

        #石の数を数える
        self.white_count, self.black_count = self.count_stones(self.board_state)
        
        #次のプレイヤーのひっくり返せる場所を探す。
        next_player = self.change_player(self.current_player)
        self.valid_moves = self.find_valid_moves(self.board_state, next_player)

        #次のプレイヤーが置ける場所がない場合スキップ
        if not self.valid_moves:
            next_player = self.change_player(self.current_player)
            self.valid_moves = self.find_valid_moves(self.board_state, next_player)

            if not self.valid_moves:
                self.current_player = 0
                #最後の集計
                self.white_count, self.black_count = self.count_stones(self.board_state)
        

        print(self.valid_moves)

    def change_player(self, current_player):
        next_player = current_player * -1
        return next_player
    
    #石を置けるかの判定
    def can_place_stone(self, board, row, col, player):

        #すでに石が置かれている場合は置けない
        if board[row][col] != 0:
            return False
        
        for dr, dc in self.DIRECTIONS:
            r, c = row + dr, col + dc
            #隣のマスが相手の石でなければ無効
            if board[r][c] != -player:
                continue
            
            #相手の石が終わるまで進む
            while board[r][c] == -player:
                r += dr
                c += dc
            
            #ループの終了時、自分の石にいたら有効
            if board[r][c] == player:
                return True
            
        #どれも無効の場合は置けない
        return False
    
    #全体から有効なマスを探す
    def find_valid_moves(self, board, player):
        valid_moves = []
        for row in range(1, len(board) - 1):
            for col in range(1, len(board) - 1):
                if self.can_place_stone(board, row, col, player):
                    valid_moves.append((row, col))
        
        #有効なマスのインデックスを返す
        return valid_moves
    
    #ひっくり返せる場所を探す
    def find_flippable(self, board, row, col, player):
        filippable_pos = []

        for dr, dc in self.DIRECTIONS:
            r, c = row + dr, col + dc
            temp_pos = []

            # 隣が相手の石でなければ次の方向へ
            while board[r][c] == -player:
                temp_pos.append((r, c))
                r += dr
                c += dc

            # 自分の石に到達した場合だけひっくり返せる
            if board[r][c] == player:
                filippable_pos.extend(temp_pos)

        print(filippable_pos)
        return filippable_pos
    
    #石の数を数える
    def count_stones(self, board_state):
        flattened = list(chain.from_iterable(board_state))
        white_count = flattened.count(1)
        black_count = flattened.count(-1)

        return white_count, black_count
    
    #勝者を決める　
    def judge_winner(self):
        if self.white_count > self.black_count:
            return "白の勝ちです！"
        elif self.black_count > self.white_count:
            return "黒の勝ちです！"
        else:
            return "引き分けです！"

        
class GUI:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page_width = 1000
        self.page_height = 800
        self.grid_size = 8
        self.grid = [] #オセロ盤のUIを保持
        self.create_board()
        self.create_buttons()
        self.join_GUI()
        self.isgame = False

    #オセロ盤を作る
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
                        #ここにオセロを置く処理を追加
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

    #ボタン、テキストボックスを作る
    def create_buttons(self):
        #モード切り替えスイッチ
        self.change_switch = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("ノーマルモード"),
                    ft.Switch(),
                    ft.Text("AI対戦モード")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor="white",
            border=ft.border.all(2, "black"),
            margin=ft.margin.all(5),
            border_radius=ft.border_radius.all(10),
            expand=1,
        )

        #ゲームの進行状況を表示する
        self.info_text = ft.Container(
            content=ft.Text("info_text", size=20),
            bgcolor="white",
            border=ft.border.all(2, "black"),
            margin=ft.margin.all(5),
            border_radius=ft.border_radius.all(10),
            alignment=ft.alignment.center,
            expand=4,
        )

        #オセロの枚数を数えて表示する
        self.othello_count = ft.Container(
            content=ft.Text("白: 枚 黒: 枚", size=20),
            bgcolor="white",
            border=ft.border.all(2, "black"),
            margin=ft.margin.all(5),
            border_radius=ft.border_radius.all(10),
            alignment=ft.alignment.center,
            expand=4,
        )

        #ゲームのスタート、リスタートボタン
        self.control_buttons = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Button(
                        text="スタート",
                        expand=5,
                        on_click=self.start_game,
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

    def join_GUI(self):
        self.gui_container = ft.Container(
            content=ft.Row(
                controls=[
                    self.board_container,
                    ft.Container(
                        #content=ft.Text("ボタン"),
                        content = self.buttons,
                        bgcolor="#008800",
                        height=self.page_height,
                        expand=True
                    )
                ],
                spacing=0,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            #調整しなきゃかも
            #width=self.page_width,
            #height=self.page_height*0.94,
            expand=True,
            bgcolor="#008800",
            border_radius=ft.border_radius.all(5)
        )

    #スタートボタンが押された時、ボードを初期化して石を描画
    def start_game(self, e):
        if self.isgame == False:
            self.game = OthelloGame()
            self.initialize_game() 
            self.isgame = True

    #リセットボタンが押された時の処理
    def reset_game(self, e):
        if self.isgame == True:
            self.del_valid_moves()
            self.game = OthelloGame()  # 新しいゲーム状態を作成
            self.initialize_game()     # ボードを初期化して描画
            self.del_valid_moves()

            # 情報表示をリセット
            self.info_text.content = ft.Text("ゲームをリセットしました。スタートボタンを押してください。", size=20)
            self.othello_count.content = ft.Text("黒: 2\n白: 2", size=20)

            self.isgame = False
            
            # ページを更新
            self.page.update()

    
    #初期化
    def initialize_game(self):
        print("オセロ盤を更新中...") 
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                #白石
                if self.game.board_state[row+1][col+1] == 1:
                    self.grid[row][col].content =  ft.CircleAvatar(radius=self.grid_px // 2, bgcolor="white")
                    self.grid[row][col].on_click = None
                #黒石
                elif self.game.board_state[row+1][col+1] == -1:
                    self.grid[row][col].content =  ft.CircleAvatar(radius=self.grid_px // 2, bgcolor="black")
                    self.grid[row][col].on_click = None
                else:
                    self.grid[row][col].on_click = lambda e, r=row, c=col: self.handle_click(r, c)
                    self.grid[row][col].content = None  

        #先行のプレイヤーをinfo_textに表示
        first_player = "白が先行です" if self.game.current_player == 1 else "黒が先行です"
        self.info_text.content = ft.Text(first_player, size=20)

        #石の数を表示
        self.othello_count.content = ft.Text(f"黒:{self.game.black_count}\n白:{self.game.white_count}", size=20)

        #石を置ける場所を描画
        self.draw_valid_moves()

        #ページを更新
        self.page.update() 

    #石を置けるマスを黄色で囲む
    def draw_valid_moves(self):
        for row, col in self.game.valid_moves:
            self.grid[row-1][col-1].border = ft.border.all(2, "yellow")
    #戻す
    def del_valid_moves(self):
        for row, col in self.game.valid_moves:
            self.grid[row-1][col-1].border = ft.border.all(2, "black")

    #石が置かれる処理
    def handle_click(self, row, col):
        if self.isgame == True:
            print(f"Clicked row:{row}, col{col}")

            if (row+1, col+1) not in set(self.game.valid_moves):
                print("ここには置けません！")
                return
            
            self.del_valid_moves()

            #クリックされたマスに円を描画
            self.draw_circle(row, col)

            #オセロの状態を更新
            self.game.update_state(row+1, col+1)
            filippable_pos = self.game.flippable_pos
            for row, col in filippable_pos:
                row -= 1
                col -= 1
                self.draw_circle(row, col)

            #石の数を表示
            self.othello_count.content = ft.Text(f"黒:{self.game.black_count}\n白:{self.game.white_count}", size=20)

            #次の番へ
            self.game.current_player = self.game.change_player(self.game.current_player)
            current_player = "白のターンです" if self.game.current_player == 1 else "黒のターンです"
            self.info_text.content = ft.Text(current_player, size=20)

            #スキップ
            if not self.game.valid_moves:
                skipped_player = "白のターンがスキップされました" if self.game.current_player == 1 else "黒のターンがスキップされました"
                self.game.current_player = self.game.change_player(self.game.current_player)
                self.info_text.content = ft.Text(skipped_player+"\n"+current_player, size=20)

                #終了判定
                if self.game.current_player == 0:
                        self.info_text.content = ft.Text("両者に置ける場所がないため、ゲーム終了です。" + "\n" + self.game.judge_winner(), size=20)

                
            #石が置ける場所を描画
            self.draw_valid_moves()

            #ページの更新
            self.page.update()
    
    #石を描画
    def draw_circle(self, row, col):
        if self.game.current_player == 1:
                self.grid[row][col].content = ft.CircleAvatar(radius=self.grid_px // 2, bgcolor="white")
                self.grid[row][col].on_click = None
        else:
            self.grid[row][col].content = ft.CircleAvatar(radius=self.grid_px // 2, bgcolor="black")
            self.grid[row][col].on_click = None




def main(page: ft.Page):
    gui = GUI(page)
    page.title = "オセロ"
    page.window.width = gui.page_width
    page.window.height = gui.page_height

    page.add(gui.gui_container)

ft.app(target=main)