import json
import math
import os

import numpy as np
from scipy.integrate import quad
from sympy import lambdify, symbols


class BezierInterpolation:
    def __init__(self, json_file, keyframe_name):
        base_dir = os.path.dirname(__file__)
        json_file_path = os.path.join(base_dir, json_file)

        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        keyframe_data = data.get(keyframe_name)
        if not keyframe_data:
            raise ValueError(f"Keyframe {keyframe_name} not found in the JSON file.")
        
        self.location_eqs = {axis: self.parse_bezier_equation(eq_data["equation"]) for axis, eq_data in keyframe_data['Bezier equations']['Bezier equations for location'].items()}
        self.rotation_eqs = {axis: self.parse_bezier_equation(eq_data["equation"]) for axis, eq_data in keyframe_data['Bezier equations']['Bezier equations for rotation_euler'].items()}
        self.scale_eqs = {axis: self.parse_bezier_equation(eq_data["equation"]) for axis, eq_data in keyframe_data['Bezier equations']['Bezier equations for scale'].items()}

    def parse_bezier_equation(self, bezier_eq_str):
        t = symbols('t')
        expr = eval(bezier_eq_str, {"t": t, "np": np, "math": math})
        return expr

    def evaluate_bezier_curve(self, bezier_eq, frame):
        t = symbols('t')
        bezier_func = lambdify(t, bezier_eq, modules=["numpy"])
        return float(bezier_func(frame))

    def get_transformation_matrix(self, t):
        # Evaluate Bézier curves for translation, rotation, and scale
        location = {axis: self.evaluate_bezier_curve(self.location_eqs[axis], t) for axis in ['B_X', 'B_Y', 'B_Z']}
        rotation = {axis: self.evaluate_bezier_curve(self.rotation_eqs[axis], t) for axis in ['B_X', 'B_Y', 'B_Z']}
        scale = {axis: self.evaluate_bezier_curve(self.scale_eqs[axis], t) for axis in ['B_X', 'B_Y', 'B_Z']}

        # Construct the transformation matrix
        translation_matrix = np.array([
            [1, 0, 0, location['B_X']],
            [0, 1, 0, location['B_Y']],
            [0, 0, 1, location['B_Z']],
            [0, 0, 0, 1]
        ])

        rotation_matrix = np.eye(4)
        rotation_matrix[:3, :3] = self.euler_to_matrix([
            math.radians(rotation['B_X']),
            math.radians(rotation['B_Y']),
            math.radians(rotation['B_Z'])
        ])

        scale_matrix = np.array([
            [scale['B_X'], 0, 0, 0],
            [0, scale['B_Y'], 0, 0],
            [0, 0, scale['B_Z'], 0],
            [0, 0, 0, 1]
        ])

        # Combine the transformations
        transformation_matrix = translation_matrix @ rotation_matrix @ scale_matrix
        return transformation_matrix

    def euler_to_matrix(self, euler_angles):
        rx = np.array([
            [1, 0, 0],
            [0, np.cos(euler_angles[0]), -np.sin(euler_angles[0])],
            [0, np.sin(euler_angles[0]), np.cos(euler_angles[0])]
        ])

        ry = np.array([
            [np.cos(euler_angles[1]), 0, np.sin(euler_angles[1])],
            [0, 1, 0],
            [-np.sin(euler_angles[1]), 0, np.cos(euler_angles[1])]
        ])

        rz = np.array([
            [np.cos(euler_angles[2]), -np.sin(euler_angles[2]), 0],
            [np.sin(euler_angles[2]), np.cos(euler_angles[2]), 0],
            [0, 0, 1]
        ])

        return rz @ ry @ rx

    def curve_length(self, t1, t2, bezier_x, bezier_y, bezier_z):
        t = symbols('t')
        bezier_x_func = lambdify(t, bezier_x, modules=["numpy"])
        bezier_y_func = lambdify(t, bezier_y, modules=["numpy"])
        bezier_z_func = lambdify(t, bezier_z, modules=["numpy"])

        def curve_derivative(t):
            dx_dt = np.gradient([bezier_x_func(t - 0.01), bezier_x_func(t), bezier_x_func(t + 0.01)])[1]
            dy_dt = np.gradient([bezier_y_func(t - 0.01), bezier_y_func(t), bezier_y_func(t + 0.01)])[1]
            dz_dt = np.gradient([bezier_z_func(t - 0.01), bezier_z_func(t), bezier_z_func(t + 0.01)])[1]
            return np.sqrt(dx_dt**2 + dy_dt**2 + dz_dt**2)

        return quad(curve_derivative, t1, t2)[0]

def follow_flight_path(fls_id):
    # Define file paths relative to the current directory
    base_dir = os.path.dirname(__file__)
    all_coords_file = os.path.join(base_dir, "all_FLS_Coords.json")
    location_curves_path = os.path.join(base_dir, "bezier_equations_location_KF1.json")
    rotation_curves_path = os.path.join(base_dir, "bezier_equations_degrees_KF1.json")
    scale_curves_path = os.path.join(base_dir, "bezier_equations_scale_KF1.json")

    # Load the center point from all_FLS_Coords.json
    with open(all_coords_file, 'r') as file:
        all_coords = json.load(file)
        local_center = np.array(all_coords[fls_id])

    # Load the Bézier curve equations
    def load_bezier_equations(file_path):
        with open(file_path, 'r') as file:
            bezier_data = json.load(file)
        return {axis: data["equation"] for axis, data in bezier_data.items()}

    location_curves = load_bezier_equations(location_curves_path)
    rotation_curves = load_bezier_equations(rotation_curves_path)
    scale_curves = load_bezier_equations(scale_curves_path)

    # Function to parse and lambdify Bézier equation string
    def parse_and_lambdify(bezier_eq_str):
        t = symbols('t')
        expr = eval(bezier_eq_str)
        return lambdify(t, expr)

    # Parse and lambdify the Bézier equations
    location_eqs = {axis: parse_and_lambdify(eq) for axis, eq in location_curves.items()}
    rotation_eqs = {axis: parse_and_lambdify(eq) for axis, eq in rotation_curves.items()}
    scale_eqs = {axis: parse_and_lambdify(eq) for axis, eq in scale_curves.items()}

    # Function to calculate the derivative of the Bézier curve
    def curve_derivative(t, bezier_x, bezier_y, bezier_z):
        dx_dt = np.gradient([bezier_x(t - 0.01), bezier_x(t), bezier_x(t + 0.01)])[1]
        dy_dt = np.gradient([bezier_y(t - 0.01), bezier_y(t), bezier_y(t + 0.01)])[1]
        dz_dt = np.gradient([bezier_z(t - 0.01), bezier_z(t), bezier_z(t + 0.01)])[1]
        return np.sqrt(dx_dt**2 + dy_dt**2 + dz_dt**2)

    # Function to calculate the curve length using numerical integration
    def curve_length(t1, t2, bezier_x, bezier_y, bezier_z):
        return quad(curve_derivative, t1, t2, args=(bezier_x, bezier_y, bezier_z))[0]

    # Calculate the total length of the curve
    total_distance = curve_length(1, 42, location_eqs['B_X'], location_eqs['B_Y'], location_eqs['B_Z'])

    # Calculate velocity at each frame
    max_velocity = 0.0
    max_velocity_frame = 1
    for frame in range(1, 42):
        # Calculate the velocity between this frame and the next
        velocity = curve_length(frame, frame + 1, location_eqs['B_X'], location_eqs['B_Y'], location_eqs['B_Z']) * 24
        if velocity > max_velocity:
            max_velocity = velocity
            max_velocity_frame = frame

    # # Output results to JSON
    # results = {
    #     "total_distance": total_distance,
    #     "max_velocity": max_velocity,
    #     "max_velocity_frame": max_velocity_frame,
    #     "fls_id": fls_id
    # }

    # with open(f"fls_results_{fls_id}.json", "w") as outfile:
    #     json.dump(results, outfile, indent=4)

    # print(f"Results for FLS {fls_id} written to fls_results_{fls_id}.json")