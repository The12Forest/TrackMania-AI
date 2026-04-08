import sys

# ── Config ────────────────────────────────────────────────────
FALLBACK_SERVER_NAME = "TMInterface0"
SERVER_NAME = f'TMInterface{sys.argv[1]}' if len(sys.argv) > 1 else FALLBACK_SERVER_NAME

INFER_EVERY_N_TICKS         = 5
TRAIN_INTERVAL_SEC          = 1
STUCK_SPEED_THRESHOLD       = 4.0
STUCK_TIME_LIMIT            = 1
ACTIVATE_LIVE_MONITOR       = False
RESET_COOLDOWN_STEPS        = 10


# ── Wall Hit Detection ────────────────────────────────────────
WALL_HIT_MIN_WEEL_COUNT     = 2.0
WALL_HIT_SPEED_DROP         = 2.0
WALL_HIT_PENALTY            = -15.0
WALL_HIT_PENALTY_DECAY      = 0.8