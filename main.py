import csv
import json
import os
import re
import time  # Import the time module

import numpy as np
import pandas as pd  # Import pandas for Excel output
from bezier_interpolation import BezierInterpolation
from fls import FLS


def extract_keyframe_info(json_file, keyframe_name):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    keyframe_data = data.get(keyframe_name)
    if not keyframe_data:
        raise ValueError(f"Keyframe {keyframe_name} not found in the JSON file.")
    
    start_frame = keyframe_data['start_time']
    end_frame = keyframe_data['end_time']
    return start_frame, end_frame

def main():
    start_time = time.time()  # Record the start time

    # Update the file paths to the new directory
    all_coords_file = '/Users/nimayazdani/Desktop/testFolder/SyncFLSPseudo/Blender-Outputs/all_FLS_Coords.json'
    bezier_file = '/Users/nimayazdani/Desktop/testFolder/SyncFLSPseudo/Blender-Outputs/all_beziers.json'
    
    fls_ids = range(1)  # ***Assuming 1 FLS for this example, CHANGE THIS TO 2008 in order to animate all FLS in the Rose Animation***

    # Define the results directory
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)

    # Define file paths for CSV outputs
    waypoints_file = os.path.join(results_dir, "calculated_waypoints.csv")
    frame_lengths_file = os.path.join(results_dir, "calculated_frame_lengths.csv")

    # Open CSV files with line buffering and write headers
    with open(waypoints_file, mode='w', newline='', buffering=1) as wp_file, \
         open(frame_lengths_file, mode='w', newline='', buffering=1) as fl_file:

        wp_writer = csv.writer(wp_file)
        fl_writer = csv.writer(fl_file)

        # Write headers
        headers = ['Frame'] + [f'FLS{fls_id}' for fls_id in fls_ids]
        wp_writer.writerow(headers)
        fl_writer.writerow(headers)

        # Extract keyframe information
        keyframes = [
            ('Keyframe 1 to Keyframe 2', extract_keyframe_info(bezier_file, 'Keyframe 1 to Keyframe 2')),
            ('Keyframe 2 to Keyframe 3', extract_keyframe_info(bezier_file, 'Keyframe 2 to Keyframe 3')),
            ('Keyframe 3 to Keyframe 4', extract_keyframe_info(bezier_file, 'Keyframe 3 to Keyframe 4')),
            ('Keyframe 4 to Keyframe 5', extract_keyframe_info(bezier_file, 'Keyframe 4 to Keyframe 5'))
        ]

        # Initialize FLS instances for each keyframe segment
        fls_instances = {
            name: [
                FLS(fls_id, BezierInterpolation(bezier_file, name), all_coords_file)
                for fls_id in fls_ids
            ]
            for name, _ in keyframes
        }

        # Dictionary to store max velocity information
        max_velocity_info = {f'FLS{fls_id}': {'frame': None, 'velocity': 0} for fls_id in fls_ids}
        overall_max_velocity = {'frame': None, 'velocity': 0, 'fls_id': None}

        # Process frames for all keyframes
        for frame in range(keyframes[0][1][0], keyframes[-1][1][1] + 1):
            waypoints_row = [frame]
            frame_lengths_row = [frame]

            # Determine the current keyframe segment
            for name, (kf_start, kf_end) in keyframes:
                if kf_start <= frame <= kf_end:
                    current_fls_instances = fls_instances[name]
                    break

            for fls in current_fls_instances:
                fls.update_position(frame, kf_start)
                waypoints_row.append(np.round(fls.current_position, 5).tolist())
                frame_length = fls.calculate_frame_length(frame - 1, frame)
                frame_lengths_row.append(frame_length)

                # Calculate velocity
                velocity = frame_length * 24
                if velocity > max_velocity_info[f'FLS{fls.fls_id}']['velocity']:
                    max_velocity_info[f'FLS{fls.fls_id}']['velocity'] = velocity
                    max_velocity_info[f'FLS{fls.fls_id}']['frame'] = frame
                # Check for overall max velocity
                if velocity > overall_max_velocity['velocity']:
                    overall_max_velocity['velocity'] = velocity
                    overall_max_velocity['frame'] = frame
                    overall_max_velocity['fls_id'] = fls.fls_id

            # Write the current frame's data to CSV
            wp_writer.writerow(waypoints_row)
            fl_writer.writerow(frame_lengths_row)

        # Update total distance traveled for each keyframe segment
        for name, (kf_start, kf_end) in keyframes:
            for fls in fls_instances[name]:
                fls.update_total_distance_traveled(kf_start, kf_end)

    # Write max velocity information to JSON in the results directory
    for fls in fls_instances[keyframes[0][0]]:
        max_velocity_info[f'FLS{fls.fls_id}']['total_distance_traveled'] = fls.total_distance_traveled

    velocity_data = {
        "overall_max_velocity": overall_max_velocity,
        "fls_max_velocities": max_velocity_info
    }
    with open(os.path.join(results_dir, "calculated_velocities.json"), "w") as json_file:
        json.dump(velocity_data, json_file, indent=4)

    end_time = time.time()  # Record the end time
    print(f"Total execution time: {end_time - start_time:.2f} seconds")  # Print the total execution time

if __name__ == "__main__":
    main()