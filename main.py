import json
import time  # Import the time module

import numpy as np

from bezier_interpolation import BezierInterpolation
from fls import FLS


def main():
    start_time = time.time()  # Start the timer

    bezier_interpolation = BezierInterpolation(
        'bezier_equations_location.json',
        'bezier_equations_degrees.json',
        'bezier_equations_scale.json'
    )
    
    all_coords_file = 'all_FLS_Coords.json'
    
    fls_instances = [
        FLS(fls_id, bezier_interpolation, all_coords_file)
        for fls_id in range(2009)
    ]

    # Store results for each FLS
    fls_results = []

    max_velocity = [0, 0]
    max_velocity_frame = [None, None]

    for frame in range(1, 43):  # Simulate frames 1 to 42
        for fls in fls_instances:
            fls.update_position(frame)
            # Calculate velocity for the current frame
            velocity = fls.velocity_magnitude(frame) * 24  # Convert to per second
            if velocity > max_velocity[fls.fls_id]:
                max_velocity[fls.fls_id] = velocity
                max_velocity_frame[fls.fls_id] = frame

    for fls in fls_instances:
        total_length = fls.total_distance
        print(f"Total Path Length for FLS {fls.fls_id}: {total_length}")

        # Store results for this FLS
        fls_results.append({
            "fls_id": fls.fls_id,
            "total_length": total_length,
            "max_velocity": max_velocity[fls.fls_id],
            "max_velocity_frame": max_velocity_frame[fls.fls_id]
        })

    # Write results to JSON
    with open('fls_results.json', 'w') as outfile:
        json.dump(fls_results, outfile, indent=4)

    end_time = time.time()  # End the timer
    print(f"Execution time: {end_time - start_time:.2f} seconds")  # Print the execution time

if __name__ == "__main__":
    main()