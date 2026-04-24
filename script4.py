#!/usr/bin/env python3
import asyncio
import logging
from mavsdk import System
from mavsdk.offboard import PositionNedYaw, OffboardError
from pynput import keyboard

logging.basicConfig(level=logging.INFO)

# Globals
drone = None
loop = None
override_active = False
current_mode = "OFFBOARD"
current_input = [0, 0, 0.5, 0]  # roll, pitch, throttle, yaw

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

# ---------------- DRONE SETUP ----------------
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

    #RC > Mavlink
    await drone.param.set_param_int("COM_RC_IN_MODE", 5) 
    #Enable override during offboard 
    await drone.param.set_param_int("COM_RC_OVERRIDE", 1)

    # Arm
    print("-- Arming")
    
    #prevents disarm timeout
    await drone.param.set_param_float("COM_DISARM_PRFLT", -1.0)
    await drone.action.arm()

    # Start Offboard
    print("-- Starting offboard")
    await drone.offboard.set_position_ned(PositionNedYaw(0, 0, -5, 0))
    try:
        await drone.offboard.start()
    except OffboardError as e:
        print(f"Offboard failed: {e}")
        await drone.action.disarm()
        return


async def control_loop():
    global current_mode

    while True:
        if override_active:
            if current_mode != "MANUAL":
                print("-- Switching to MANUAL")
                await drone.offboard.stop()
                await drone.manual_control.set_manual_control_input(*current_input)
                current_mode = "MANUAL"

            # Continuously send manual input
            await drone.manual_control.set_manual_control_input(*current_input)
            print("MANUAL:", current_input)

        else:
            if current_mode != "OFFBOARD":
                print("-- Switching to OFFBOARD")
                await drone.offboard.set_position_ned(PositionNedYaw(-28.26, -27.91, -13, 0))
                try:
                    await drone.offboard.start()
                    current_mode = "OFFBOARD"
                except OffboardError as e:
                    print(f"Offboard failed: {e}")

            await drone.offboard.set_position_ned(PositionNedYaw(-28.26, -27.91, -13, 0))
            print("OFFBOARD: going to waypoint")

        await asyncio.sleep(0.05)  # 20 Hz

# ---------------- TELEMETRY ----------------
async def monitor_flight_mode():
    async for mode in drone.telemetry.flight_mode():
        print(f"Mode: {mode}")

# ---------------- MAIN ----------------
async def main():
    global loop
    loop = asyncio.get_running_loop()

    # Keyboard listener (runs in separate thread)
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    await setup_drone()

    await asyncio.gather(
        control_loop(),
        monitor_flight_mode(),
    )

if __name__ == "__main__":
    asyncio.run(main())