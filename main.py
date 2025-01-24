import json

import numpy as np

from bezier_interpolation import BezierInterpolation
from fls import FLS


def main():
    bezier_interpolation = BezierInterpolation(
        'bezier_equations_location.json',
        'bezier_equations_degrees.json',
        'bezier_equations_scale.json'
    )
    
    all_coords_file = 'all_FLS_Coords.json'
    
    fls_instances = [
        FLS(fls_id, bezier_interpolation, all_coords_file)
        for fls_id in range(3)
    ]

    max_velocity = 0
    max_velocity_fls_id = None
    max_velocity_frame = None
    furthest_distance = 0
    furthest_distance_fls_id = None
    longest_frame_distance = 0
    longest_frame_distance_fls_id = None
    longest_frame_distance_frame = None

    for frame in range(1, 43):  # Simulate frames 1 to 42
        for fls in fls_instances:
            fls.update_position(frame)
            # Calculate velocity for the current frame
            velocity = fls.velocity_magnitude(frame) * 24  # Convert to per second
            if velocity > max_velocity:
                max_velocity = velocity
                max_velocity_fls_id = fls.fls_id
                max_velocity_frame = frame

    for fls in fls_instances:
        total_length = fls.calculate_path_length(1, 42)
        print(f"Total Path Length for FLS {fls.fls_id}: {total_length}")
        if total_length > furthest_distance:
            furthest_distance = total_length
            furthest_distance_fls_id = fls.fls_id

    # Find the longest frame distance
    for fls in fls_instances:
        for frame in range(1, 42):
            frame_length = fls.calculate_frame_length(frame, frame + 1)
            if frame_length > longest_frame_distance:
                longest_frame_distance = frame_length
                longest_frame_distance_fls_id = fls.fls_id
                longest_frame_distance_frame = frame

    # Output results to JSON
    results = {
        "max_velocity": max_velocity,
        "max_velocity_fls_id": max_velocity_fls_id,
        "max_velocity_frame": max_velocity_frame,
        "furthest_distance": furthest_distance,
        "furthest_distance_fls_id": furthest_distance_fls_id,
        "longest_frame_distance": longest_frame_distance,
        "longest_frame_distance_fls_id": longest_frame_distance_fls_id,
        "longest_frame_distance_frame": longest_frame_distance_frame
    }

    with open("fls_results.json", "w") as outfile:
        json.dump(results, outfile, indent=4)

    print("Results written to fls_results.json")

if __name__ == "__main__":
    main()