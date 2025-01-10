import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Add, Subtract
from tensorflow.keras.optimizers import Adam
from othello_game import OthelloGame
from dqn_agent import DQNAgent

#DQNを構築
def build_model(state_size, action_size):
    inputs = Input(shape=(state_size,))
    hidden = Dense(128, activation='relu')(inputs)  
    hidden = Dense(128, activation='relu')(hidden)

    advantage = Dense(action_size, activation='linear')(hidden)
    mean_advantage = Dense(1, activation='linear')(advantage)  
    adjusted_advantage = Subtract()([advantage, mean_advantage])

    value = Dense(1, activation='linear')(hidden)
    q_values = Add()([value, adjusted_advantage])

    model = Model(inputs=inputs, outputs=q_values)
    model.compile(optimizer=Adam(learning_rate=0.0005), loss='mse')  
    return model

#訓練する
def train_dqn(episodes, batch_size=64):
    state_size = (8, 8)  
    action_size = 64  
    agent = DQNAgent(state_size, action_size)  
    reward_log = [] 

    for e in range(episodes):
        game = OthelloGame()
        state = game.board.reshape(1, 8, 8, 1)  
        total_reward = 0

        while not game.is_game_over():
            valid_moves = game.get_valid_moves(game.current_player)
            if not valid_moves:
                game.current_player *= -1  
                continue

            # 合法手のみを渡す
            valid_actions = [x * 8 + y for x, y in valid_moves]
            action = agent.act(state, valid_actions)
            move = (action // 8, action % 8)

            # 合法手以外を選べないようにする
            if move not in valid_moves:
                move = valid_moves[np.random.choice(len(valid_moves))]

            # 石を置く処理
            game.make_move(move, game.current_player)
            flipped_stones = np.sum(game.board == game.current_player) - np.sum(state[0, :, :, 0] == game.current_player)

            # 報酬
            reward = flipped_stones  # 石をひっくり返した数
            if move in [(0, 0), (0, 7), (7, 0), (7, 7)]:  # 角を取る行動
                reward += 15  # 報酬を増加
            elif move in [(1, 1), (1, 6), (6, 1), (6, 6)]:  # 不利なX-square
                reward -= 10
            elif move in [(0, 1), (1, 0), (1, 7), (0, 6), (6, 0), (7, 1), (6, 7), (7, 6)]:  # 不利なC-square
                reward -= 5

            # 次の状態を取得
            next_state = game.board.reshape(1, 8, 8, 1)  # 形状を (1, 8, 8, 1) に変換

            # 勝敗判定後の追加報酬
            if game.is_game_over():
                if game.get_winner() == game.current_player:
                    reward += 30  # 勝利時の報酬を増加
                elif game.get_winner() == -game.current_player:
                    reward -= 30  # 敗北時のペナルティを増加

            # 経験を保存して、学習
            done = game.is_game_over()
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward

            # ターン交代
            game.current_player *= -1

        agent.replay(batch_size=batch_size)

        agent.epsilon = max(agent.epsilon * agent.epsilon_decay, agent.epsilon_min)

        reward_log.append(total_reward)
        print(f"エピソード {e+1}/{episodes} 終了 - 累積報酬: {total_reward}")

    # モデルを保存
    agent.save("ver1_fixed.keras")  
    print("モデルを保存しました。")

    return reward_log

#報酬ログ
def plot_rewards(reward_log):
    plt.plot(reward_log)
    plt.xlabel('Episode')
    plt.ylabel('Cumulative Reward')
    plt.title('Training Progress')
    plt.grid()
    plt.show()

if __name__ == "__main__":
    episodes = 100  
    reward_log = train_dqn(episodes=episodes)

    # 報酬ログをプロット
    plot_rewards(reward_log)
