import helper as h
import numpy as np
import gymnasium as gym
from gymnasium import spaces

# Todo, check if invalid moves throw error

class Abalone(gym.Env):
    # metadata = {'render_modes': ['human'], 'render_fps': 4}

    def __init__(self, render_mode=None, hex_grid_size=3):
        super().__init__()
        
        self.winner = -1
        self.radius = hex_grid_size-1
        self.piece_information = {
            h.Cells.PlayerOne: [0, 0, 0],
            h.Cells.PlayerTwo: [0, 0, 0]
        }
        hex_grid = h.make_hex_grid(hex_grid_size, piece_information=self.piece_information)
        grid_size = hex_grid.shape[0]
        
        self.action_space = spaces.Dict({
            "start": spaces.Box(low=0, high=grid_size-1, shape=(2,), dtype=np.int32),
            "end": spaces.Box(low=0, high=grid_size-1, shape=(2,), dtype=np.int32),
            "direction": spaces.Discrete(6)
        })
        self.observation_space = spaces.Box(
            low=0, high=3, shape=(grid_size, grid_size), dtype=np.int32
        )
        
        # Initialize state
        self.state = hex_grid
        self.turn = 0
        self.invalid_move_reasons = []
        
        # Rendering setup
        self.render_mode = h.RenderModes.Grid if render_mode is None else render_mode 
        
    def get_info(self):
        return {
            "turn": self.turn,
            "invalid_move_reasons": self.invalid_move_reasons,
            "piece information": self.piece_information,
            "winner": self.winner
        }

    def reset(self, seed=None, options=None):
        # Initialize random number generator
        super().reset(seed=seed)
        
        # Initialize state
        self.state = h.make_hex_grid(self.radius + 1, piece_information=self.piece_information)
        self.turn = 0
        self.winner = -1
        
        # Return initial observation and info dict
        return self.state, self.get_info()
    
    def render(self):
        if self.render_mode == h.RenderModes.Grid:
            h.print_hex_grid(self.state)
        if self.render_mode == h.RenderModes.Human:
            # Implement some pygame drawing function
            pass
        
    def close(self):
        # Clean up any resources
        pass
    
    def step(self, action):
        self.invalid_move_reasons = []
        
        # Execute action["and"] get next state
        # Your environment logic here
        
        # Example reward calculation
        reward = 0
        terminated = False
        truncated = False
        
        target_cell = h.Cells.PlayerOne if self.turn % 2 == 0 else h.Cells.PlayerTwo
        enemy_cell = h.Cells.PlayerTwo if self.turn % 2 == 0 else h.Cells.PlayerOne
        
        direction, magnitude = h.determine_direction(action["start"], action["end"], self.radius)
        
        # Direction is invalid and magnitude is not 1, or magnitude is more than 3
        if (direction == -1 and magnitude != 1 or magnitude > 3):
            
            if (direction == -1):
                self.invalid_move_reasons.append("Direction between point (" \
                    + h.convert_odd_row_to_cube(action['start'], self.radius, to_string=True) \
                    + ") and point (" \
                    + h.convert_odd_row_to_cube(action['end'], self.radius, to_string=True) \
                    + ") is invalid")
            if (magnitude > 3):
                self.invalid_move_reasons.append("Magnitude of " + str(magnitude) + " is greater than 3.")
            
            return self.state, 0, False, False, self.get_info()
        
        
        # Push Logic
        if (direction >= 0 and action["direction"] % 3 == direction % 3):
            current_point = action["end"] if action['direction'] == direction else action["start"]
            next_point = h.add_direction_vector(current_point, action['direction'])
            
            if (self.state[tuple(next_point)] == h.Cells.Empty):
                self.state[tuple(action['start'])] = h.Cells.Empty
                self.state[tuple(next_point)] = target_cell
                
            elif not h.is_point_in_grid(next_point, self.state) or self.state[tuple(next_point)] == target_cell:
                if not h.is_point_in_grid(next_point, self.state):
                    self.invalid_move_reasons.append(
                        "Grid at position (" + h.convert_odd_row_to_cube(next_point, self.radius, to_string=True) + ") " \
                        + "is not a valid grid position"
                    )
                
                if self.state[tuple(next_point)] == target_cell:
                    self.invalid_move_reasons.append(
                        "Grid at position (" + h.convert_odd_row_to_cube(next_point, self.radius, to_string=True) + ") " \
                        + "is the target cell. Cannot make a push move into yourself"
                    )
                    
                return self.state, 0, False, False, self.get_info()
            else:
                target_group = []
                is_push_off_board = False
                while len(target_group) < magnitude:
                    target_group.append(next_point)
                    
                    next_point = h.add_direction_vector(next_point, action['direction'])
                    
                    if not h.is_point_in_grid(next_point, self.state) or self.state[tuple(next_point)] == h.Cells.Empty:
                        is_push_off_board = not h.is_point_in_grid(next_point, self.state)
                        if is_push_off_board:
                            self.piece_information[enemy_cell][h.PieceInformation.OnBoard] -= 1
                            self.piece_information[enemy_cell][h.PieceInformation.OffBoard] += 1
                        break
                
                if len(target_group) < magnitude:
                    starting_point = action["start"] if action['direction'] == direction else action["end"]
                    ending_point = action["end"] if action['direction'] == direction else action["start"]
                    starting_enemy_point = h.add_direction_vector(ending_point, action['direction'])
                    
                    self.state[tuple(starting_point)] = h.Cells.Empty
                    self.state[tuple(starting_enemy_point)] = target_cell
                    
                    if not is_push_off_board:
                        self.state[tuple(next_point)] = enemy_cell
                else:
                    self.invalid_move_reasons.append("Push move of magnitude " + str(magnitude) + " is insufficient due to more enemy marbles")
                    
                    return self.state, 0, False, False, self.get_info()
        # Side Step
        else:
            current_point = action["start"]
            # Think of better name
            target_group = []
            starting_group = []
            
            while True:
                if (self.state[tuple(current_point)] != target_cell):
                    self.invalid_move_reasons.append(
                        "Grid at position (" + h.convert_odd_row_to_cube(current_point, self.radius, to_string=True) + ") = " \
                        + str(self.state[tuple(current_point)]) + " "\
                        + "is not the target cell " + str(target_cell)
                    )
                    
                    return self.state, 0, False, False, self.get_info()

                next_point = h.add_direction_vector(current_point, action["direction"])
                
                '''
                    Invalid move if target cells are:
                    - Off the grid
                    - Not Empty
                    - In invalid grid position
                    - Handing the push logic in ---if (action["direction"] % 3 == direction % 3):---
                '''
                if (not h.is_point_in_grid(next_point, self.state) or self.state[tuple(next_point)] != h.Cells.Empty):
                    
                    if not h.is_point_in_grid(next_point, self.state):
                        self.invalid_move_reasons.append(
                            "Grid at position (" + h.convert_odd_row_to_cube(next_point, self.radius, to_string=True) + ") " \
                            + "is not a valid grid position / grid is marked invalid there."
                        )
                        
                    if self.state[tuple(next_point)] != h.Cells.Empty:
                        self.invalid_move_reasons.append(
                            "Action is a side step move, and grid at position (" + h.convert_odd_row_to_cube(next_point, self.radius, to_string=True) + ") " \
                            + "is not empty"
                        )
                    
                    return self.state, 0, False, False, self.get_info()
                
                target_group.append(tuple(next_point))
                starting_group.append(tuple(current_point))
                
                if (np.equal(current_point, action["end"]).all()):
                    break
                    
                current_point = h.add_direction_vector(current_point, direction)

            for starting_point, ending_point in zip(starting_group, target_group):
                self.state[starting_point] = h.Cells.Empty
                self.state[ending_point] = target_cell
        
        self.turn += 1

        # Todo, determine reward
        if self.piece_information[h.Cells.PlayerOne][h.PieceInformation.OffBoard] >= self.piece_information[h.Cells.PlayerOne][h.PieceInformation.Threshold]:
            terminated = True
            self.winner = h.Cells.PlayerTwo
        
        if self.piece_information[h.Cells.PlayerTwo][h.PieceInformation.OffBoard] >= self.piece_information[h.Cells.PlayerTwo][h.PieceInformation.Threshold]:
            terminated = True
            self.winner = h.Cells.PlayerOne

        # Return observation, reward, termination status, truncation, and info
        return self.state, reward, terminated, truncated, self.get_info()