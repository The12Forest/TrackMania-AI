from JSON import points
import math

# ── Track Progress ────────────────────────────────────────────
def get_centerline_distance(position, progress_idx) -> float:
    """Returns 3D perpendicular distance from the car to the track center line segment."""
    if progress_idx >= len(points) - 1:
        return 0.0

    px, py, pz = position[0], position[1], position[2]

    a = points[progress_idx]["position"]
    b = points[progress_idx + 1]["position"]

    ax, ay, az = a[0], a[1], a[2]
    bx, by, bz = b[0], b[1], b[2]

    dx, dy, dz = bx - ax, by - ay, bz - az
    seg_len_sq = dx*dx + dy*dy + dz*dz
    if seg_len_sq == 0:
        return math.sqrt((px-ax)**2 + (py-ay)**2 + (pz-az)**2)

    t = max(0.0, min(1.0, ((px-ax)*dx + (py-ay)*dy + (pz-az)*dz) / seg_len_sq))

    return math.sqrt((px - (ax + t*dx))**2 + (py - (ay + t*dy))**2 + (pz - (az + t*dz))**2)


def get_track_progress(position) -> int:
    """Returns index of the closest point in the JSON path (0 = start, len-1 = finish)."""
    px, py, pz = position[0], position[1], position[2]
    best_idx  = 0
    best_dist = float('inf')
    for i, p in enumerate(points):
        dx = px - p["position"][0]
        dy = py - p["position"][1]
        dz = pz - p["position"][2]
        dist = dx*dx + dy*dy + dz*dz  # no sqrt needed, just comparing
        if dist < best_dist:
            best_dist = dist
            best_idx  = i
    return best_idx