from tminterface.interface import TMInterface
from tminterface.client import run_client
from tminterface.client import Client


class MainClient(Client):
    def __init__(self):
        super().__init__()
        self.sim_state   = None
        self.prev_speed = 0


    def on_registered(self, iface: TMInterface):
        print(f'Registered to {iface.server_name}')



    def on_run_step(self, iface: TMInterface, _time: int):
        if _time < 0:
            return
        
        state = iface.get_simulation_state()
        speed = state.display_speed

        if detect_wall_hit(self.prev_speed, speed, state):
            print("WALL_HIT!")

        self.prev_speed = speed
        
def detect_wall_hit(prev_speed: float, curr_speed: float, state: any) -> bool:
    if [w.real_time_state.has_ground_contact for w in state.simulation_wheels].count(True) >= 2:
        return (prev_speed - curr_speed) > 5
    else:
        return False
    

# ── Entry Point ───────────────────────────────────────────────
print(f'Connecting to TMInterface1...')
tmcl = MainClient()

run_client(tmcl, "TMInterface1")
