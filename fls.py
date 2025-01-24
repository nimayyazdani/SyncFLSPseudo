import json

import numpy as np
from scipy.integrate import quad


class FLS:
    def __init__(self, fls_id, bezier_interpolation, all_coords_file):
        self.fls_id = fls_id
        self.bezier_interpolation = bezier_interpolation
        self.center_point = self.load_center_point(all_coords_file)
        self.current_position = None
        self.total_distance = 0.0

    def load_center_point(self, file_path):
        with open(file_path, 'r') as file:
            all_coords = json.load(file)
        # Access the center point for the specific FLS ID
        return np.array(all_coords[self.fls_id])

    def update_position(self, t):
        """Update the FLS's position based on the time t."""
        transformation_matrix = self.bezier_interpolation.get_transformation_matrix(t)
        initial_position_homogeneous = np.append(self.center_point, 1)
        new_position_homogeneous = transformation_matrix @ initial_position_homogeneous
        new_position = new_position_homogeneous[:3]
        
        if self.current_position is not None:
            # Calculate the path length from the previous frame to the current frame
            frame_length = self.calculate_frame_length(t - 1, t)
            self.total_distance += frame_length
            print(f"Time {t}: FLS ID {self.fls_id} Position: {self.current_position}, Frame Length: {frame_length}")
        else:
            print(f"Time {t}: FLS ID {self.fls_id} Position: {self.current_position}")

        self.current_position = new_position

    def velocity_magnitude(self, t):
        delta_t = 0.01  # Small time step for finite difference
        pos_t1 = self.bezier_interpolation.get_transformation_matrix(t) @ np.append(self.center_point, 1)
        pos_t2 = self.bezier_interpolation.get_transformation_matrix(t + delta_t) @ np.append(self.center_point, 1)
        velocity = (pos_t2[:3] - pos_t1[:3]) / delta_t
        return np.linalg.norm(velocity)

    def calculate_frame_length(self, t1, t2):
        # Integrate the velocity magnitude over the interval [t1, t2]
        # Adjust the absolute and relative error tolerances for faster computation
        length, _ = quad(self.velocity_magnitude, t1, t2)
        return length

    def calculate_path_length(self, t1, t2):
        # Integrate the velocity magnitude over the interval [t1, t2]
        length, _ = quad(self.velocity_magnitude, t1, t2)
        self.total_distance = length
        return self.total_distance