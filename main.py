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
        kf1_start, kf1_end = extract_keyframe_info(bezier_file, 'Keyframe 1 to Keyframe 2')
        kf2_start, kf2_end = extract_keyframe_info(bezier_file, 'Keyframe 2 to Keyframe 3')
        kf3_start, kf3_end = extract_keyframe_info(bezier_file, 'Keyframe 3 to Keyframe 4')
        kf4_start, kf4_end = extract_keyframe_info(bezier_file, 'Keyframe 4 to Keyframe 5')

        # Initialize FLS instances for the first keyframe segment
        bezier_interpolation_kf1 = BezierInterpolation(bezier_file, 'Keyframe 1 to Keyframe 2')
        
        fls_instances_kf1 = [
            FLS(fls_id, bezier_interpolation_kf1, all_coords_file)
            for fls_id in fls_ids
        ]

        # Dictionary to store max velocity information
        max_velocity_info = {f'FLS{fls_id}': {'frame': None, 'velocity': 0} for fls_id in fls_ids}
        overall_max_velocity = {'frame': None, 'velocity': 0, 'fls_id': None}

        # Process frames for KF1
        for frame in range(kf1_start, kf1_end + 1):
            waypoints_row = [frame]
            frame_lengths_row = [frame]

            for fls in fls_instances_kf1:
                fls.update_position(frame, kf1_start)
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

        # Update total distance traveled for KF1
        for fls in fls_instances_kf1:
            fls.update_total_distance_traveled(kf1_start, kf1_end)

        # Initialize FLS instances for the second keyframe segment
        fls_instances_kf2 = [
            FLS(fls_id, BezierInterpolation(bezier_file, 'Keyframe 2 to Keyframe 3'), all_coords_file)
            for fls_id in fls_ids
        ]

        # Process frames for KF2
        for frame in range(kf2_start, kf2_end + 1):
            waypoints_row = [frame]
            frame_lengths_row = [frame]

            for fls in fls_instances_kf2:
                fls.update_position(frame, kf2_start)
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

        # Initialize FLS instances for the third keyframe segment
        fls_instances_kf3 = [
            FLS(fls_id, BezierInterpolation(bezier_file, 'Keyframe 3 to Keyframe 4'), all_coords_file)
            for fls_id in fls_ids
        ]

        # Process frames for KF3
        for frame in range(kf3_start, kf3_end + 1):
            waypoints_row = [frame]
            frame_lengths_row = [frame]

            for fls in fls_instances_kf3:
                fls.update_position(frame, kf3_start)
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

        # Initialize FLS instances for the fourth keyframe segment
        fls_instances_kf4 = [
            FLS(fls_id, BezierInterpolation(bezier_file, 'Keyframe 4 to Keyframe 5'), all_coords_file)
            for fls_id in fls_ids
        ]

        # Process frames for KF4
        for frame in range(kf4_start, kf4_end + 1):
            waypoints_row = [frame]
            frame_lengths_row = [frame]

            for fls in fls_instances_kf4:
                fls.update_position(frame, kf4_start)
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

    # Write max velocity information to JSON in the results directory
    for fls in fls_instances_kf1:
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