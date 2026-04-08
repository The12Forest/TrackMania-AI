from tminterface.interface import TMInterface
from tminterface.client import Client
import time
import numpy as np

from _SETTINGS import *
#from _Main import agent
from Functions.detect_wall_hit import detect_wall_hit
from Functions.get_track_progress import get_track_progress
from Functions.extract_state import extract_state

class MainClient(Client):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.sim_state   = None
        self.prev_state  = None
        self.last_action = (True, 0.0)
        self.step_count  = 0
        self.tick_count  = 0
        self.stuck_since = None
        self.episode     = 0
        self.prev_speed  = 0.0
        self.episode_buffer = []
        self.reset_cooldown = RESET_COOLDOWN_STEPS
        self.needs_reseting = False
        self.needs_reseting_count = 0
        self.prev_progress  = 0
        self.best_progress  = 0

    def on_registered(self, iface: TMInterface):
        print(f'Registered to {iface.server_name}')

    def _check_reset(self, speed):
        now = time.time()
        if speed < STUCK_SPEED_THRESHOLD:
            if self.stuck_since is None:
                self.stuck_since = now
            elif now - self.stuck_since >= STUCK_TIME_LIMIT:
                return True, f"stuck ({speed:.1f} km/h for {now-self.stuck_since:.1f}s)"
        else:
            self.stuck_since = None
        return False, ""

    def _do_reset(self, iface, reason):
        print(f"[Episode {self.episode:3d}] Resetting — {reason}")
        self.sim_state   = None
        self.prev_state  = None
        self.stuck_since = None
        self.last_action = (True, 0.0)
        self.prev_speed  = 0.0
        self.episode    += 1
        self.reset_cooldown = RESET_COOLDOWN_STEPS
        self.prev_progress  = 0   # NEW
        self.best_progress  = 0   # NEW
        iface.give_up()
        self.needs_reseting = True
        self.needs_reseting_count = 0
        
    def _flush_episode_buffer(self, final_reward, final_state, final_action):
        """Push episode buffer to replay with length-based reward scaling."""
        n = len(self.episode_buffer)
        if n == 0:
            return

        # Longer episode = bigger multiplier (capped at 3x)
        length_multiplier = min(3.0, 1.0 + n / 50.0)

        for step_idx, (s, a, r, ns, d) in enumerate(self.episode_buffer):
            # Earlier steps get MORE credit the longer the episode was
            # step_idx=0 is oldest → gets highest early_bonus
            early_bonus = (1.0 - step_idx / n)  # 1.0 at start, 0.0 at end
            scaled_reward = r * length_multiplier * (1.0 + early_bonus * 0.5)
            self.agent.buffer.push(s, a, scaled_reward, ns, d)

        # Push final step
        if final_state is not None:
            self.agent.buffer.push(final_state, final_action, final_reward * length_multiplier, final_state, True)

        self.episode_buffer = []

    def on_run_step(self, iface: TMInterface, _time: int):
        if _time < 0:
            return
        
        self.step_count += 1
        self.tick_count += 1
        # NEW
        self.sim_state   = iface.get_simulation_state()
        progress         = get_track_progress(self.sim_state.position)
        state            = extract_state(self.sim_state, progress)
        speed            = float(self.sim_state.display_speed)
        
        '''
        if self.needs_reseting:
            self.needs_reseting_count += 1
            if self.needs_reseting_count == 8:
                self.needs_reseting_count = 0
                self.needs_reseting = False
                self.prev_speed = 0
                self.prev_progress = 0
                p = points[random.randint(1, points_len - 1)]  # change index to pick spawn point (index = time in seconds)

                # Position
                self.sim_state.position = p["position"]

                # Facing (yaw, pitch, roll) — already in radians
                # NEU
                yaw, pitch, roll = p["faceing"]
                self.sim_state.rotation_matrix = ypw_to_mat3(yaw, pitch, roll)

                # Velocity — already in m/s
                self.sim_state.dyna.current_state.linear_speed[0] = p["velocity"][0]
                self.sim_state.dyna.current_state.linear_speed[1] = p["velocity"][1]
                self.sim_state.dyna.current_state.linear_speed[2] = p["velocity"][2]

                iface.rewind_to_state(self.sim_state)
        '''

        if self.reset_cooldown > 0:
            self.reset_cooldown -= 1
            self.prev_speed = speed
            return

        # ── Wall hit → immediate reset ────────────────────────
        if detect_wall_hit(self.prev_speed, speed, self.sim_state):
            self._flush_episode_buffer(WALL_HIT_PENALTY, state, self.last_action)
            self._do_reset(iface, f"wall hit! ({self.prev_speed:.1f}→{speed:.1f} km/h)")
            self.prev_speed = 0
            return

        # ── Stuck reset ───────────────────────────────────────
        should_reset, reason = self._check_reset(speed)
        if should_reset:
            self._flush_episode_buffer(-1.0, state, self.last_action)
            self._do_reset(iface, reason)
            return

        # ── Normal step ───────────────────────────────────────
        # Speed reward (normalized 0..1)
        speed_reward = speed / 250.0

        # Progress reward
        progress_delta = progress - self.prev_progress
        if progress_delta > 0:
            progress_reward = progress_delta * 0.5
        elif progress_delta < 0:
            progress_reward = progress_delta * 1.5
        else:
            progress_reward = 0.0

        # New best bonus
        new_best_bonus = 0.0
        if progress > self.best_progress:
            new_best_bonus = (progress - self.best_progress) * 0.3
            self.best_progress = progress

        reward = (
            speed_reward
            + progress_reward
            + new_best_bonus
        )

        self.prev_progress = progress

        if self.prev_state is not None:
            self.episode_buffer.append((self.prev_state, self.last_action, reward, state, False))

        if self.tick_count % INFER_EVERY_N_TICKS == 0:
            accelerate, steer_raw = self.agent.select_action(state)
            self.last_action = (accelerate, steer_raw)

        accelerate, steer_raw = self.last_action
        steer_int = int(np.clip(steer_raw * 65536, -65536, 65536))

        iface.set_input_state(
            accelerate=accelerate,
            brake=False,
            left=False,
            right=False,
            steer=steer_int
        )

        self.prev_state = state
        self.prev_speed = speed
