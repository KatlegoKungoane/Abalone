import numpy as np
import helper as h
from env.abaloneEnv import Abalone

# its column row, you fool

env = Abalone(hex_grid_size=3)

grid, info = env.reset()
h.print_hex_grid(grid)
print("")

next_grid, reward, _, done, info = env.step({
    'start': np.array([0, 3]),
    'end': np.array([1, 2]),
    'direction': h.Directions.DownLeft,
})

next_grid, reward, _, done, info = env.step({
    'start': np.array([4, 1]),
    'end': np.array([4, 1]),
    'direction': h.Directions.UpLeft,
})

next_grid, reward, _, done, info = env.step({
    'start': np.array([1, 2]),
    'end': np.array([2, 2]),
    'direction': h.Directions.DownLeft,
})

next_grid, reward, _, done, info = env.step({
    'start': np.array([4, 3]),
    'end': np.array([4, 3]),
    'direction': h.Directions.UpRight,
})

next_grid, reward, _, done, info = env.step({
    'start': np.array([2, 2]),
    'end': np.array([3, 1]),
    'direction': h.Directions.DownLeft,
})

next_grid, reward, _, done, info = env.step({
    'start': np.array([3, 3]),
    'end': np.array([3, 3]),
    'direction': h.Directions.UpRight,
})

next_grid, reward, _, done, info = env.step({
    'start': np.array([4, 1]),
    'end': np.array([3, 1]),
    'direction': h.Directions.UpRight,
})

next_grid, reward, _, done, info = env.step({
    'start': np.array([3, 0]),
    'end': np.array([3, 0]),
    'direction': h.Directions.DownRight,
})

next_grid, reward, terminated, truncated, info = env.step({
    'start': np.array([2, 2]),
    'end': np.array([3, 1]),
    'direction': h.Directions.DownLeft,
})

env.render()
print(info)
print("done", terminated)