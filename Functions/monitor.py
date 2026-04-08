import time

def monitor(tmcl, agent):
    while tmcl.sim_state is None:
        time.sleep(0.01)
    while True:
        acc, steer_raw = tmcl.last_action
        stuck_str = f"  ⚠ stuck {time.time()-tmcl.stuck_since:.1f}s" if tmcl.stuck_since else ""
        print(
            f"[Ep {tmcl.episode:3d}] Step {tmcl.step_count:5d} | "
            f"Speed: {tmcl.sim_state.display_speed:6.1f} km/h | "
            f"acc={int(acc)} steer={int(steer_raw*65536):+7d} ({steer_raw:+.3f}) | "
            f"wall hits: {tmcl.wall_hits:3d} | "
            f"ε:{agent.epsilon:.3f} noise:{agent.noise:.3f} buf:{len(agent.buffer)}"
            f"{stuck_str}"
        )
        time.sleep(2)