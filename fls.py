import json
import os

import numpy as np
import pandas as pd  # Import pandas for DataFrame operations
from scipy.integrate import quad


class FLS:
    def __init__(self, fls_id, bezier_interpolation, all_coords_file):
        base_dir = os.path.dirname(__file__)
        all_coords_file_path = os.path.join(base_dir, all_coords_file)
        self.fls_id = fls_id
        self.bezier_interpolation = bezier_interpolation
        self.center_points = self.load_center_points(all_coords_file_path, fls_id)
        self.current_position = None
        self.total_distance = 0.0
        self.total_distance_traveled = 0.0
        # New attributes for the local clock mechanism
        self.local_clock = 0.0      # FLS's own internal time
        self.prev_local_clock = 0.0 # To store the previous clock value used for integrations
        self.advance_count = 0      # Counter for even FLS to control clock advancement

    def load_center_points(self, file_path, fls_id):
        with open(file_path, 'r') as file:
            all_coords = json.load(file)
        # Extract center points using start frame numbers as keys
        center_points = {}
        for start_frame, coords in all_coords.items():
            # Assuming coords is a list where the index corresponds to the FLS ID
            center_points[int(start_frame)] = np.array(coords[fls_id], dtype=np.float64)
        return center_points

    def update_position(self, start_frame):
        """Update the FLS's position using its local clock and the given keyframe start frame."""
        # Use the correct center point for the current keyframe interval
        self.center_point = self.center_points[start_frame]
        current_time = self.local_clock
        transformation_matrix = self.bezier_interpolation.get_transformation_matrix(current_time)
        initial_position_homogeneous = np.append(self.center_point, 1)
        new_position_homogeneous = transformation_matrix @ initial_position_homogeneous
        new_position = new_position_homogeneous[:3]

        # Calculate frame length based on the difference between the previous and current local clock values
        if self.local_clock == start_frame:
            frame_length = 0.0  # At the very start, no movement has occurred
        else:
            frame_length = self.calculate_frame_length(self.prev_local_clock, self.local_clock)
        self.total_distance += frame_length
        self.current_position = new_position
        print(f"Local Clock {self.local_clock}: FLS ID {self.fls_id} Position: {self.current_position}, Frame Length: {frame_length}")

    def velocity_magnitude(self, t):
        delta_t = 0.001  # Smaller time step for finite difference
        pos_t1 = self.bezier_interpolation.get_transformation_matrix(t) @ np.append(self.center_point, 1)
        pos_t2 = self.bezier_interpolation.get_transformation_matrix(t + delta_t) @ np.append(self.center_point, 1)
        velocity = (pos_t2[:3] - pos_t1[:3]) / delta_t
        return np.linalg.norm(velocity)

    def calculate_frame_length(self, t1, t2):
        # Integrate the velocity magnitude over the interval [t1, t2]
        length, _ = quad(self.velocity_magnitude, t1, t2, epsabs=1e-9, epsrel=1e-9)
        return length

    def calculate_path_length(self, segments):
        total_length = 0.0
        for (t1, t2) in segments:
            length, _ = quad(self.velocity_magnitude, t1, t2, epsabs=1e-9, epsrel=1e-9)
            total_length += length
        return total_length

    def update_total_distance_traveled(self, t1, t2):
        # Calculate the path length for the interval and update the total distance traveled
        length = self.calculate_frame_length(t1, t2)
        self.total_distance_traveled += length

    def advance_clock(self, error_model=1):
        """
        Advance the FLS's local clock according to error-model 1:
          - For odd-numbered FLS (fast): Increment the clock by 2 every call.
          - For even-numbered FLS (slow): Increment by 1 only every other call.
        """
        if error_model == 1:
            if self.fls_id % 2 == 1:  # odd FLS: advance by 2 every time
                self.prev_local_clock = self.local_clock
                self.local_clock += 2
            else:  # even FLS: update only every other time
                self.advance_count += 1
                if self.advance_count % 2 == 0:
                    self.prev_local_clock = self.local_clock
                    self.local_clock += 1
                else:
                    # Do not update the clock on the first call (simulate delay)
                    self.prev_local_clock = self.local_clock
        else:
            # Default behavior if no error model is specified: increment by 1
            self.prev_local_clock = self.local_clock
            self.local_clock += 1

