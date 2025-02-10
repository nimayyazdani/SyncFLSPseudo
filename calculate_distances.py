import numpy as np
import pandas as pd


def calculate_euclidean_distances(file1, file2, output_file):
    # Load the coordinates from the CSV files
    waypoints = np.loadtxt(file1, delimiter=",")
    fls_coordinates = np.loadtxt(file2, delimiter=",")

    # Ensure both files have the same number of coordinates
    if waypoints.shape != fls_coordinates.shape:
        raise ValueError("The number of coordinates in both files must be the same.")

    # Calculate the Euclidean distances
    distances = np.linalg.norm(waypoints - fls_coordinates, axis=1)

    # Save the distances to a new CSV file
    np.savetxt(output_file, distances, delimiter=",", fmt="%.5f")

    print(f"Euclidean distances have been saved to {output_file}")

if __name__ == "__main__":
    calculate_euclidean_distances("spheres_waypoints.csv", "fls_coordinates.csv", "waypoint_checker.csv") 