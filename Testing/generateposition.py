import json
import os
import math
import sys
from tminterface.interface import TMInterface
from tminterface.client import Client, run_client
import time

# ─── USER SETTINGS ───────────────────────────────────────────────────────────
RECORD_EVERY_SECONDS = 1       # change to 0.5 for every half second, etc.
OUTPUT_FOLDER = "."            # folder to save JSON files, "." = same folder as script
# ─────────────────────────────────────────────────────────────────────────────

RECORD_EVERY_MS = int(RECORD_EVERY_SECONDS * 1000)
time.sleep(5)
class RecorderClient(Client):
    def __init__(self):
        super().__init__()
        self.points = []
        self.last_recorded_ms = -RECORD_EVERY_MS  # so we record at t=0
        self.track_name = None
        self.output_path = None

    def on_registered(self, iface: TMInterface):
        print(f'Connected to {iface.server_name}')
        print(f'Recording a point every {RECORD_EVERY_SECONDS}s')

    def on_run_step(self, iface: TMInterface, _time: int):
        if _time < 0:
            return

        # Get track name once
        if self.track_name is None:
            try:
                self.track_name = iface.get_map_name()
            except:
                self.track_name = "unknown_track"
            self.track_name = os.path.splitext(os.path.basename(self.track_name))[0]
            self.output_path = os.path.join(OUTPUT_FOLDER, f"{self.track_name}.json")
            print(f'Track: {self.track_name}')
            print(f'Saving to: {self.output_path}')

        # Only record every RECORD_EVERY_MS
        if _time - self.last_recorded_ms < RECORD_EVERY_MS:
            return

        state = iface.get_simulation_state()

        # Position
        pos = state.position

        # Velocity
        vel = state.velocity
        speed_ms = math.sqrt(vel[0]**2 + vel[1]**2 + vel[2]**2)
        speed_kmh = round(speed_ms * 3.6, 1)

        # Yaw / pitch / roll (radians)
        ypr = state.yaw_pitch_roll

        point = {
            "time_s":    round(_time / 1000, 2),
            "position":  pos,
            "faceing":   ypr,
            "velocity":  vel
        }

        self.points.append(point)
        self.last_recorded_ms = _time

        # Save/overwrite JSON every entry
        with open(self.output_path, 'w') as f:
            json.dump(self.points, f, indent=2)

        print(f't={point["time_s"]}s | pos=({pos}) | yaw={ypr} | {vel}')

    def on_deregistered(self, iface: TMInterface):
        print(f'\nDisconnected. {len(self.points)} points saved to {self.output_path}')


server_name = f'TMInterface{sys.argv[1]}' if len(sys.argv) > 1 else 'TMInterface1'
print(f'Connecting to {server_name}...')
run_client(RecorderClient(), server_name)