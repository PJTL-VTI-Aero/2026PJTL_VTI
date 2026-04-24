# 2026PJTL_VTI

## 1. Clone PX4 Autopilot

Clone the PX4 Autopilot repository:
```bash
git clone https://github.com/PX4/PX4-Autopilot.git
```

---

## 2. Modifying the Baylands World (baylands.sdf)
You can modify the simulation environment to include the Post Office and the multicolored balls by editing the `baylands.sdf` world file.

### File location:
```bash
PX4-Autopilot/Tools/simulation/gz/worlds/baylands.sdf
```

---

## 3. Running the Simulation

Navigate to the PX4 directory:
```bash
cd ~/Desktop/2026VTI/PX4-Autopilot
```

Start the simulation:
```bash
make px4_sitl gz_x500_mono_cam_down_baylands
```

---

## 4. Camera Visualization

Open a new terminal in the same directory and run:
```bash
python3 camera.py
```

This will display the live camera feed from the simulated drone.

---

## 5. Running Control Scripts

Activate the virtual environment:
```bash
source venv/bin/activate
```

Run any script:
```bash
python3 script1.py
```

---

## 6. Connection Settings

### Simulation (SITL)
Ensure your code uses:
```python
await drone.connect(system_address="udpin://0.0.0.0:14540")
```

### Real Drone (Freefly Alta X)
When connecting to a real vehicle, update the `system_address` to match the telemetry connection instead of the SITL UDP endpoint.
