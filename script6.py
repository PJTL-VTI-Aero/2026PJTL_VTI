#!/usr/bin/env python3
import asyncio
import logging
from mavsdk import System, telemetry
from mavsdk.offboard import PositionNedYaw, OffboardError
from pynput import keyboard

logging.basicConfig(level=logging.INFO)

# Globals
drone = None
loop = None
override_active = False
current_mode = "TAKEOFF"
finished_takeoff = False
current_input = [0, 0, 0.5, 0]  # roll, pitch, throttle, yaw
altitude = 0.0

# ---------------- KEYBOARD HANDLERS ----------------
def on_press(key):
    global override_active, current_input, loop, drone

    try:
        override_active = True
        if key.char == "w":
            current_input[1] = 1
        elif key.char == "s":
            current_input[1] = -1
        elif key.char == "a":
            current_input[0] = -1
        elif key.char == "d":
            current_input[0] = 1
        elif key.char == "q":
            current_input[2] = 1
        elif key.char == "e":
            current_input[2] = 0

        # Thread-safe scheduling of manual input
        if drone and loop:
            asyncio.run_coroutine_threadsafe(
                drone.manual_control.set_manual_control_input(*current_input),
                loop
            )

    except AttributeError:
        pass


def on_release(key):
    global current_input, loop, drone
    try:
        if key.char in ["w", "s"]:
            current_input[1] = 0
        elif key.char in ["a", "d"]:
            current_input[0] = 0
        elif key.char in ["q", "e"]:
            current_input[2] = 0.5

        if drone and loop and override_active:
            asyncio.run_coroutine_threadsafe(
                drone.manual_control.set_manual_control_input(*current_input),
                loop
            )

    except AttributeError:
        pass

async def setup_drone():
    global drone
    drone = System()
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    print("Waiting for connection...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected")
            break

    print("Waiting for GPS...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- GPS OK")
            break

   
    # Arm
    print("-- Arming")
    
    #prevents disarm timeout
    await drone.param.set_param_float("COM_DISARM_PRFLT", -1.0)
    await drone.action.arm()

    # Start Offboard
    # print("-- Starting offboard")
    # await drone.offboard.set_position_ned(PositionNedYaw(0, 0, 0, 0))
    # try:
    #     await drone.offboard.start()
    # except OffboardError as e:
    #     print(f"Offboard failed: {e}")
    #     await drone.action.disarm()
    #     return


async def control_loop():
    global current_mode, altitude, finished_takeoff

    while True:
        async for mode in drone.telemetry.flight_mode():
            print(f"Mode: {mode}")
            print(altitude)

            if (mode in [telemetry.FlightMode.POSCTL, telemetry.FlightMode.HOLD] and altitude >= 10 and finished_takeoff == False):
                print("Agree to take control?")
                input()
                finished_takeoff = True
                await drone.offboard.set_position_ned(PositionNedYaw(-28.26, -27.91, -13, 0))
  

            # if (mode == "POSCTL" and finished_takeoff is True):
            #     print("Operator has taken control") 
            #     await drone.offboard.stop()

async def altitude_loop():
    global altitude
    async for distance in drone.telemetry.distance_sensor():
        # current_distance_m is the Lidar reading in meters
        altitude = distance.current_distance_m

# ---------------- MAIN ----------------
async def main():
    global loop, drone
    loop = asyncio.get_running_loop()

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    try:
        await setup_drone()

        await asyncio.gather(
            control_loop(),
            altitude_loop(),
        )
    
    except KeyboardInterrupt:
        await drone.action.disarm()

if __name__ == "__main__":
    asyncio.run(main())
