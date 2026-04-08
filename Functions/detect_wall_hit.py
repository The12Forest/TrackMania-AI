from _SETTINGS import WALL_HIT_SPEED_DROP, WALL_HIT_MIN_WEEL_COUNT

def detect_wall_hit(prev_speed: float, curr_speed: float, state: any) -> bool:
    if [w.real_time_state.has_ground_contact for w in state.simulation_wheels].count(True) >= WALL_HIT_MIN_WEEL_COUNT:
        return (prev_speed - curr_speed) > WALL_HIT_SPEED_DROP
    else:
        return False
