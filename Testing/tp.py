import json
from tminterface.client import Client, run_client

with open("A01.json") as f:
    points = json.load(f)

from tminterface.interface import TMInterface
from tminterface.client import Client, run_client
import threading, time
import sys

accelerate = 1 
brake=0
steer=0

class MainClient(Client):
    def __init__(self) -> None:
        super(MainClient, self).__init__()
        self.state = None
        self.point = None

    def on_registered(self, iface: TMInterface) -> None:
        print(f'Registered to {iface.server_name}')

    def on_run_step(self, iface: TMInterface, _time: int):
        if _time < 0:
            return
        self.sim_state = iface.get_simulation_state()
        print(self.sim_state.velocity)

        # Position
        self.sim_state.position = [249.7171630859375, 9.025850296020508, 670.4503784179688]
        #state.position.y = self.point["y"]
        #state.position.z = self.point["z"]

        self.sim_state.yaw_pitch_roll

        # Velocity (speed in m/s along direction - NOT sure about field names)
        self.sim_state.dyna.current_state.linear_speed[0] = 30        # state.velocity.x = ...
        self.sim_state.dyna.current_state.linear_speed[1] = 0    # state.velocity.x = ...
        self.sim_state.dyna.current_state.linear_speed[2] = 0    # state.velocity.x = ...
        # state.velocity.z = ...
        iface.rewind_to_state(self.sim_state)

server_name = f'TMInterface{sys.argv[1]}' if len(sys.argv) > 1 else 'TMInterface1'
print(f'Connecting to {server_name}...')
tmcl = MainClient()

run_client(tmcl, server_name)  # main thread, no try/except needed