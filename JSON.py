import json
import numpy as np

with open("A01.json", "r") as f:
    points = json.load(f)
    points_len = len(points)

all_x = [p["position"][0] for p in points]
all_y = [p["position"][1] for p in points]
all_z = [p["position"][2] for p in points]
POS_MIN = np.array([min(all_x), min(all_y), min(all_z)], dtype=np.float32)
POS_MAX = np.array([max(all_x), max(all_y), max(all_z)], dtype=np.float32)
POS_RANGE = POS_MAX - POS_MIN + 1e-8