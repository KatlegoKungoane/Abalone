import numpy as np
from enum import IntEnum, StrEnum

class Directions(IntEnum):
    UpLeft = 0
    UpRight = 1
    Right = 2
    DownRight = 3
    DownLeft = 4
    Left = 5
    
class Cells(IntEnum):
    Invalid = 0
    PlayerOne = 1
    PlayerTwo = 2
    Empty = 3
    
class PieceInformation(IntEnum):
    OnBoard = 0
    OffBoard = 1
    Threshold = 2
    
class RenderModes(StrEnum):
    Human = 'human'
    Grid = 'grid'
    Painted = 'painted'

directions = {
    0: {  # Even rows
        Directions.UpLeft: np.array([-1, -1]),
        Directions.UpRight: np.array([-1, 0]),
        Directions.Right: np.array([0, 1]),
        Directions.DownRight: np.array([1, 0]),
        Directions.DownLeft: np.array([1, -1]),
        Directions.Left: np.array([0, -1])
    },
    1: {  # Odd rows
        Directions.UpLeft: np.array([-1, 0]),
        Directions.UpRight: np.array([-1, 1]),
        Directions.Right: np.array([0, 1]),
        Directions.DownRight: np.array([1, 1]),
        Directions.DownLeft: np.array([1, 0]),
        Directions.Left: np.array([0, -1])
    }
}

cube_directions = {
    Directions.UpLeft: np.array([0, 1, -1]),
    Directions.UpRight: np.array([1, 0, -1]),
    Directions.Right: np.array([1, -1, 0]),
    Directions.DownRight: np.array([0, -1, 1]),
    Directions.DownLeft: np.array([-1, 0, 1]),
    Directions.Left: np.array([-1, 1, 0])
}

def make_hex_grid(size, set_initial_position=True, piece_information=None):
    size = 2 * size -1
    grid = np.full(shape=(size, size), fill_value=Cells.Empty)
    if (set_initial_position):
        set_initial_player_configuration(grid, piece_information)
    mark_invalid_cells(grid)
    return grid

def mark_invalid_cells(grid):
    radius = grid.shape[0] // 2
    for row_index, row in enumerate(grid):
        axial_row = row_index - radius
        no_cols_in_row = 2 * radius + 1 - abs(axial_row)
        if radius % 2 == 0:
            starting_index = abs(axial_row) // 2
        else:
            starting_index = int(np.ceil(abs(axial_row) / 2))
        row[: starting_index] = Cells.Invalid
        row[starting_index + no_cols_in_row: ] = Cells.Invalid
        
def set_initial_player_configuration(grid, piece_information):
    match grid.shape[0]:
        case 3: 
            grid[0, 1:3] = Cells.PlayerOne
            grid[2, 1:3] = Cells.PlayerTwo
            
            piece_information[Cells.PlayerOne] = [2, 0, 1]
            piece_information[Cells.PlayerTwo] = [2, 0, 1]
        case 5: 
            grid[0, :] = Cells.PlayerOne
            grid[1, 1:3] = Cells.PlayerOne
            
            grid[-2, 1:3] = Cells.PlayerTwo
            grid[-1, :] = Cells.PlayerTwo
            
            piece_information[Cells.PlayerOne] = [5, 0, 2]
            piece_information[Cells.PlayerTwo] = [5, 0, 2]
        case 7: 
            grid[:2, :] = Cells.PlayerOne
            grid[2, 3:5] = Cells.PlayerOne
            
            grid[-2:, :] = Cells.PlayerTwo
            grid[-3, 3:5] = Cells.PlayerTwo
            
            piece_information[Cells.PlayerOne] = [11, 0, 5]
            piece_information[Cells.PlayerTwo] = [11, 0, 5]
        case 9: 
            grid[:2, :] = Cells.PlayerOne
            grid[2, 3:6] = Cells.PlayerOne
            
            grid[-2:, :] = Cells.PlayerTwo
            grid[-3, 3:6] = Cells.PlayerTwo
            
            piece_information[Cells.PlayerOne] = [14, 0, 6]
            piece_information[Cells.PlayerTwo] = [14, 0, 6]
        case 11: 
            grid[:3, :] = Cells.PlayerOne
            grid[3, 3:8] = Cells.PlayerOne
            
            grid[-3:, :] = Cells.PlayerTwo
            grid[-4, 3:8] = Cells.PlayerTwo
            
            piece_information[Cells.PlayerOne] = [29, 0, 7]
            piece_information[Cells.PlayerTwo] = [29, 0, 7]
        case _: raise NotImplementedError("Default configurations for grid sizes 3, 5, 7, 9 and 11")
        
def print_hex_grid(grid):
    size = grid.shape[0]    
    radius = grid.shape[0] // 2
    number_of_hashtags = (size + 1) // 2 + 1
    number_of_spaces = radius + 1 + radius % 2
    
    line = ''
    for _ in range(number_of_spaces):
        line += ' '
    for _ in range(number_of_hashtags):
        line += '# '
    print(line)
    
    for row_index, row in enumerate(grid):
        axial_row = row_index - radius
        no_cols_in_row = 2 * radius + 1 - abs(axial_row)
        if radius % 2 == 0:
            starting_index = abs(axial_row) // 2
        else:
            starting_index = int(np.ceil(abs(axial_row) / 2))
        
        line = ''
        if (row_index % 2 == 1):
            line += ' '
            
        if (row_index == 4):
            t = 1
            
        no_hashtags_drawn = 0
        for col_index, col in enumerate(row):
            if col_index == starting_index or col_index == starting_index + no_cols_in_row:
                line += '# '
                no_hashtags_drawn += 1
            line += col.astype(str)
            if (col_index != size - 1):
                line += ' '
            elif no_hashtags_drawn < 2:
                line += ' #'
        
        line = line.replace('0', ' ')
        line = line.replace('3', '-')
        print(line)
            
    line = ''
    for _ in range(number_of_spaces):
        line += ' '
    for _ in range(number_of_hashtags):
        line += '# '
    print(line)
        
def convert_odd_row_to_cube(odd_row_coordinate, radius, to_string=False):
    axial_row = odd_row_coordinate[0] - radius
    
    if radius % 2 == 0:
        starting_index = abs(axial_row) // 2
    else:
        starting_index = int(np.ceil(abs(axial_row) / 2))
    
    if odd_row_coordinate[0] < radius:
        center = starting_index + odd_row_coordinate[0]
    else: 
        center = starting_index + radius
    
    x = odd_row_coordinate[1] - center
    z = axial_row
    y = -x-z
    return np.array([x, y, z]) if not to_string else ','.join(np.array([x, y, z]).astype(str))

def determine_direction(starting_point, ending_point, radius):
    cube_starting_point = convert_odd_row_to_cube(starting_point, radius)
    cube_ending_point = convert_odd_row_to_cube(ending_point, radius)
    
    direction_vector = (cube_ending_point - cube_starting_point).astype(np.float64)
    
    magnitude = np.max(direction_vector)
    direction_vector /= magnitude
    direction_vector = direction_vector.astype(np.int64)
    magnitude += 1
    
    for direction in range(6):
        if np.equal(cube_directions[direction], direction_vector).all():
            return direction, magnitude

    return -1, magnitude

def is_point_in_grid(point, grid):
    return point[0] >= 0 \
        and point[1] >= 0 \
        and point[0] < grid.shape[0] \
        and point[1] < grid.shape[1] \
        and grid[tuple(point)] != Cells.Invalid
        
def add_direction_vector(point, direction):
    return point + directions[point[0] % 2][direction]