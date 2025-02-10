# SyncFLSPseudo

1. Open the Blender folder.
2. Navigate to Blender_Scripts_to_Extract_Animation_Data.blend.
3. In the script "Introduce and Animate FLSs, extract Coords and Beziers" make sure to adjust the directory to your specs.
4. Run the script called "Introduce and Animate FLSs, extract Coords and Beziers".
   This will output the following files:
   - "all_beziers.json" : A JSON file containg all of the bezier equations as a function of time for each keyframe interval.
   - "all_FLS_Coords.json" : A JSON file containing all of the starting coordinates for all FLSs at the begining of each keyframe of the animation.
   - "keyframes_Rose_All_VERTICES.json" : A intermediary JSON file that stores the keyframes to be applied to the generated FLSs (represetned as spheres) in the depicted animation.
   - "Sphere_0_global_coordinates.txt" : A text file that contains the coordinates of FLS ID 0 (represented as a sphere object in Blender) during the entire animation as a sanity check.
5. Next, navigate to the "main.py" file. Before running, specify how many FLSs are in the animation. 
6. Run "main.py".
   This should output three files into the results folder:
   - "calculated_frame_lengths.csv" : A CSV file that contains the travel length that each FLS traveled from one frame to the next during the animation.
   - "calculated_velocities.json" : A JSON file that stores the calculated minimum velocity that an FLS should be able to achieve in order to execute this animation. It also stores the maximum velocity that each FLS reached during the animation and the time at which that max was achieved.
   - "calculated_waypoints.csv" : a CSV file that contains the interpolated 3D coordiantes of all FLSs for each frame of the animation.



