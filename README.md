2026PJTL_VTI

Running the Simulation
Navigate to the PX4 directory:
cd ~/Desktop/2026VTI/PX4-Autopilot
Start the simulation:
make px4_sitl gz_x500_mono_cam_down_baylands

Camera Visualization
Open a new terminal in the same directory and run:
python3 camera.py
This will display the live camera feed from the simulated drone.

Running Control Scripts
Activate the virtual environment:
source venv/bin/activate
Run any script:
python3 script1.py


For simulation (SITL), ensure your code uses:
await drone.connect(system_address="udpin://0.0.0.0:14540")
For Free Fly Alta Testing, you must update the system_address in your script to match the telemetry connection.
