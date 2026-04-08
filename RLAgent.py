import numpy as np
import tensorflow as tf
import threading
import random
from RLAgent_Buffer import ReplayBuffer

def build_actor(input_dim=11, output_dim=2):
    inputs = tf.keras.Input(shape=(input_dim ,))
    hidden = tf.keras.layers.Dense(128, activation='relu')(inputs)
    hidden = tf.keras.layers.Dense(128,  activation='relu')(hidden)
    output = tf.keras.layers.Dense(output_dim, activation='sigmoid')(hidden)
    return tf.keras.Model(inputs, output)

class RLAgent:
    def __init__(self):
        self.actor      = build_actor()
        self.optimizer  = tf.keras.optimizers.Adam(1e-3)
        self.buffer     = ReplayBuffer()
        self.gamma      = 0.99
        self.epsilon    = 1.2
        self.eps_min    = 0.07
        self.eps_decay  = 0.9995
        self.batch_size = 64
        self.noise      = 0.3
        self._lock      = threading.Lock()
        
    def select_action(self, state):
        with self._lock:
            pred = self.actor(state[np.newaxis], training=False).numpy()[0]
            acc_p = float(pred[0])
            steer_o = float(pred[1])

        if random.random() < self.epsilon:
            return bool(random.random() > 0.5), random.uniform(-1.0, 1.0)

        steer = np.clip((steer_o * 2.0 - 1.0) + np.random.normal(0, self.noise), -1.0, 1.0)
        return (
            acc_p > 0.5,
            float(steer)
        )

    def train_step(self):
        if len(self.buffer) < self.batch_size:
            return

        batch       = self.buffer.sample(self.batch_size)
        states      = np.array([b[0] for b in batch], dtype=np.float32)
        actions     = [b[1] for b in batch]
        rewards     = np.array([b[2] for b in batch], dtype=np.float32)
        next_states = np.array([b[3] for b in batch], dtype=np.float32)
        dones       = np.array([b[4] for b in batch], dtype=np.float32)

        acc_t   = np.array([[float(a[0])] for a in actions], dtype=np.float32)
        steer_t = np.array([[a[1]]         for a in actions], dtype=np.float32)

        with self._lock:
            next_pred = self.actor(next_states, training=False)
            next_steer = next_pred[:, 1:2]
            next_val  = tf.reduce_mean(tf.abs(next_steer), axis=1).numpy()
            advantage = rewards + self.gamma * next_val * (1 - dones)
            advantage = (advantage - advantage.mean()) / (advantage.std() + 1e-8)
            advantage = advantage.astype(np.float32)

            with tf.GradientTape() as tape:
                pred = self.actor(states, training=True)
                p_acc = pred[:, 0:1]
                p_steer = pred[:, 1:2]
                loss_acc   = tf.keras.losses.binary_crossentropy(acc_t, p_acc)
                loss_steer = tf.reduce_mean(tf.square(steer_t - p_steer), axis=1)
                loss       = tf.reduce_mean((loss_acc + loss_steer) * advantage)

            grads = tape.gradient(loss, self.actor.trainable_variables)
            self.optimizer.apply_gradients(zip(grads, self.actor.trainable_variables))

        self.epsilon = max(self.eps_min, self.epsilon * self.eps_decay)
        self.noise   = max(0.05, self.noise * 0.995)
