import asyncio
from mavsdk import System

async def run():
    drone = System()
    # Connect to the SITL drone
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connected!")
            break

    # Subscribe to distance sensor telemetry (LIDAR altitude)
    async for distance in drone.telemetry.distance_sensor():
        # current_distance_m is the Lidar reading in meters
        print(f"LIDAR Altitude: {distance.current_distance_m} m")

if __name__ == "__main__":
    asyncio.run(run())
