import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

#from tminterface import util
from tminterface.client import run_client
import threading, time

from RLAgent import RLAgent
from JSON import *
from TM_Client import MainClient
from _SETTINGS import *
from Functions.monitor import monitor

agent = RLAgent()

def train_loop():
    while True:
        time.sleep(TRAIN_INTERVAL_SEC)
        agent.train_step()




# ── Entry Point ───────────────────────────────────────────────
print(f'Connecting to {SERVER_NAME}...')
tmcl = MainClient(agent)

if ACTIVATE_LIVE_MONITOR: 
    threading.Thread(target=monitor(tmcl, agent), daemon=True).start()
threading.Thread(target=train_loop, daemon=True).start()
run_client(tmcl, SERVER_NAME)
