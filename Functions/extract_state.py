import numpy as np
import math

from JSON import points, POS_MIN, POS_RANGE
from Functions.get_track_progress import get_centerline_distance



def extract_state(sim_state, progress_idx) -> np.ndarray:
    pos   = np.array(sim_state.position, dtype=np.float32)
    vel   = sim_state.velocity
    rpy   = sim_state.yaw_pitch_roll
    speed = sim_state.display_speed

    pos_norm  = (pos - POS_MIN) / POS_RANGE
    vel_norm  = [vel[0] / 50.0, vel[1] / 50.0, vel[2] / 50.0]
    speed_norm = speed / 250.0
    yaw_norm  = rpy[0] / math.pi

    if progress_idx < len(points) - 1:
        next_p = points[progress_idx + 1]
        dx = next_p["position"][0] - pos[0]
        dz = next_p["position"][2] - pos[2]
        target_yaw = math.atan2(dz, dx)
        diff = math.atan2(math.sin(rpy[0] - target_yaw), math.cos(rpy[0] - target_yaw))
        rel_dir      = diff / math.pi
        dist_to_next = math.sqrt(dx*dx + dz*dz) / 100.0
    else:
        rel_dir      = 0.0
        dist_to_next = 0.0

    center_dist = get_centerline_distance(sim_state.position, progress_idx) / 20.0  # normalize, 20m ≈ track half-width

    return np.array([
        speed_norm,
        pos_norm[0], pos_norm[1], pos_norm[2],
        vel_norm[0], vel_norm[1], vel_norm[2],
        yaw_norm,
        rel_dir,
        dist_to_next,
        center_dist,
    ], dtype=np.float32)