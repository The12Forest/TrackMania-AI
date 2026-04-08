import random
import threading
from collections import deque

class ReplayBuffer:
    def __init__(self, capacity=50_000):
        self.buffer = deque(maxlen=capacity)
        self.lock   = threading.Lock()

    def push(self, state, action, reward, next_state, done):
        with self.lock:
            self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        with self.lock:
            return random.sample(self.buffer, batch_size)

    def __len__(self):
        with self.lock:
            return len(self.buffer)