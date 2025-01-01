# map_gen.py

import random
import math
import logging
from config import Config

logger = logging.getLogger(__name__)

def diamond_square(size: int, roughness: float = 0.45) -> list[list[float]]:
    """
    Generate a 2D fractal heightmap using the Diamond-Square algorithm.
    Returns a 2D list of floats (0.0 - 1.0).
    """
    arr = [[0.0 for _ in range(size)] for __ in range(size)]
    arr[0][0] = random.random()
    arr[0][size - 1] = random.random()
    arr[size - 1][0] = random.random()
    arr[size - 1][size - 1] = random.random()

    step = size - 1
    while step > 1:
        half = step // 2
        # Diamond step
        for y in range(0, size - 1, step):
            for x in range(0, size - 1, step):
                c1 = arr[y][x]
                c2 = arr[y][x + step]
                c3 = arr[y + step][x]
                c4 = arr[y + step][x + step]
                mid = (c1 + c2 + c3 + c4) / 4.0
                mid += (random.random() - 0.5) * roughness * step
                arr[y + half][x + half] = mid

        # Square step
        for y in range(0, size, half):
            for x in range((y + half) % step, size, step):
                pts = []
                if y - half >= 0:
                    pts.append(arr[y - half][x])
                if y + half < size:
                    pts.append(arr[y + half][x])
                if x - half >= 0:
                    pts.append(arr[y][x - half])
                if x + half < size:
                    pts.append(arr[y][x + half])
                if pts:
                    m = sum(pts) / len(pts)
                    m += (random.random() - 0.5) * roughness * step
                    arr[y][x] = m

        step //= 2
        roughness *= 0.7

    # Normalize
    mn = min(min(r) for r in arr)
    mx = max(max(r) for r in arr)
    rng = mx - mn
    if rng < 1e-7:
        return [[0.5]*size for _ in range(size)]
    for yy in range(size):
        for xx in range(size):
            arr[yy][xx] = (arr[yy][xx] - mn) / rng

    return arr

def generate_island_map() -> list[list[int]]:
    """
    Generate the island map using Diamond-Square + a radial fade,
    then convert to tile indices (volcano, forest, beach, water, etc.).
    """
    if Config.SEED is not None:
        random.seed(Config.SEED)
    else:
        Config.SEED = random.randint(0, 999999999)
        random.seed(Config.SEED)
        logger.info(f"No seed specified, using random seed {Config.SEED}.")

    w, h = Config.MAP_WIDTH, Config.MAP_HEIGHT
    ds = 1
    while ds < max(w, h):
        ds *= 2
    ds += 1

    big_map = diamond_square(ds, roughness=0.4)
    cx = ds // 2
    cy = ds // 2
    max_r = ds / 2

    # Radial fade
    for ry in range(ds):
        for rx in range(ds):
            dx = rx - cx
            dy = ry - cy
            dist = math.sqrt(dx*dx + dy*dy)
            fade = dist / max_r
            factor = max(0.0, 1.0 - fade*fade)
            big_map[ry][rx] *= factor

    # Convert to tile indices
    game_map = [[3 for _ in range(w)] for __ in range(h)]
    for row in range(h):
        for col in range(w):
            v = big_map[row][col]
            if v < 0.20:
                tile = 3  # Water
            elif v < 0.30:
                tile = 2  # Beach
            elif v < 0.80:
                tile = 1  # Forest
            else:
                tile = 0  # Volcano
            game_map[row][col] = tile

    # Optionally add mud
    land_tiles = [(x, y) for y in range(h) for x in range(w) if game_map[y][x] != 3]
    random.shuffle(land_tiles)
    total_land = len(land_tiles)
    mud_count = int(total_land * 0.03)
    for i in range(mud_count):
        lx, ly = land_tiles[i]
        game_map[ly][lx] = 4  # Mud

    # Optionally add spikes
    if Config.SPIKES_ENABLED:
        spike_count = int(total_land * 0.02)
        for i in range(spike_count):
            lx, ly = land_tiles[i + mud_count]
            game_map[ly][lx] = 5  # Spikes

    logger.info("Island map generated successfully.")
    return game_map
