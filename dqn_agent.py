import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Lambda, Add, Subtract, Conv2D, Flatten
from tensorflow.keras.optimizers import Adam
from collections import deque
import random

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size  # 状態の次元数 (8x8ボードの2D表現)
        self.action_size = action_size  # 行動の次元数 (64マス)
        self.memory = deque(maxlen=2000)  # 経験の保存メモリ
        self.gamma = 0.99  # 割引率
        self.epsilon = 1.0  # 探索率（ランダム行動の確率）
        self.epsilon_decay = 0.999  # 探索率の減少速度
        self.epsilon_min = 0.1  # 探索率の下限
        self.learning_rate = 0.001  # 学習率
        self.model = self._build_model()  # 主ネットワーク
        self.target_model = self._build_model()  # ターゲットネットワーク
        self.update_target_model()

    def _build_model(self):
        inputs = Input(shape=(self.state_size[0], self.state_size[1], 1))
        conv1 = Conv2D(64, kernel_size=(3, 3), activation='relu', padding='same')(inputs)
        conv2 = Conv2D(64, kernel_size=(3, 3), activation='relu', padding='same')(conv1)
        flat = Flatten()(conv2)
        dense1 = Dense(128, activation='relu')(flat)
        advantage = Dense(self.action_size, activation='linear')(dense1)
        value = Dense(1, activation='linear')(dense1)
        q_values = Add()([value, Subtract()([advantage, Lambda(lambda x: tf.reduce_mean(x, axis=1, keepdims=True))(advantage)])])

        model = Model(inputs=inputs, outputs=q_values)
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        return model

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, valid_actions):
        if np.random.rand() <= self.epsilon:
            return random.choice(valid_actions)  # ランダムに合法手を選択
        q_values = self.model.predict(state)
        best_action = max(valid_actions, key=lambda a: q_values[0][a])
        return best_action

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return

        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = self.model.predict(state)
            if done:
                target[0][action] = reward
            else:
                next_q_values = self.target_model.predict(next_state)
                target[0][action] = reward + self.gamma * np.amax(next_q_values[0])
            self.model.fit(state, target, epochs=1, verbose=0)

        # 探索率の更新
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model = tf.keras.models.load_model(name)

    def save(self, name):
        self.model.save(name)

if __name__ == "__main__":
    state_size = (8, 8)  
    action_size = 64  
    agent = DQNAgent(state_size, action_size)

    # 仮の状態と合法手
    state = np.random.rand(1, state_size[0], state_size[1], 1)
    valid_actions = [i for i in range(action_size)]

    # 行動を選択
    action = agent.act(state, valid_actions)
    print(f"選択された行動: {action}")

    # メモリに経験を保存
    next_state = np.random.rand(1, state_size[0], state_size[1], 1)
    reward = 1
    done = False
    agent.remember(state, action, reward, next_state, done)

    # 経験をリプレイ
    agent.replay(batch_size=32)
    print("経験のリプレイを実行しました。")

    # ターゲットネットワークの更新
    agent.update_target_model()
    print("ターゲットネットワークを更新しました。")
