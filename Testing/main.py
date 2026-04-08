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

    def on_registered(self, iface: TMInterface) -> None:
        print(f'Registered to {iface.server_name}')

    def on_run_step(self, iface: TMInterface, _time: int):
        if _time >= 0:
            self.state = iface.get_simulation_state()
            iface.set_input_state(
                accelerate=accelerate,
                brake=brake,
                left=False,
                right=False,
                steer=steer  # -65536 (full left) to 65536 (full right)
            )
    def on_run_step(self, iface: TMInterface, _time: int):
        if _time < 0:
            return
        self.sim_state = iface.get_simulation_state()
        if _time == 100:   # print once at tick 100
            print(dir(self.sim_state))
            print(vars(self.sim_state))

server_name = f'TMInterface{sys.argv[1]}' if len(sys.argv) > 1 else 'TMInterface1'
print(f'Connecting to {server_name}...')
tmcl = MainClient()

def loop():
    while tmcl.state is None:
        time.sleep(0.5)
        print("Sleep")
    while True:
        print(tmcl.state.display_speed)
        time.sleep(0.5)

threading.Thread(target=loop, daemon=True).start()
run_client(tmcl, server_name)  # main thread, no try/except needed


