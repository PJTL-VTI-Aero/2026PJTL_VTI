#!/usr/bin/env python3
import asyncio
import logging

from mavsdk import System
from mavsdk.offboard import OffboardError, PositionNedYaw
from pynput import keyboard

logging.basicConfig(level=logging.INFO)

# Globals to bridge threads → asyncio
loop = None
drone = None


def on_press(key):
    """Runs in pynput thread → must NOT use await"""
    global loop, drone

    try:
        if key == keyboard.Key.space:
            print("RC Control override (space pressed)")

            # Schedule async MAVSDK call safely
            asyncio.run_coroutine_threadsafe(
                drone.manual_control.set_manual_control_input(0, 1, 0.5, 0),
                loop
            )

    except Exception as e:
        print(f"Error in key handler: {e}")


async def setup_drone():
    global drone

    drone = System()
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected")
            break

    print("Waiting for GPS...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- GPS OK")
            break
        
    # # Override RC
    # await drone.param.set_param_int("COM_RC_IN_MODE", 5)
    # await drone.param.set_param_int("COM_RC_OVERRIDE", 1)

    print("-- Arming")
    # await drone.param.set_param_float("COM_DISARM_PRFLT", -1.0)
    await drone.action.arm()

    print("-- Initial setpoint")
    await drone.offboard.set_position_ned(PositionNedYaw(0, 0, 0, 0))

    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as e:
        print(f"Offboard failed: {e}")
        await drone.action.disarm()
        return

    print("-- Flying to waypoint")


async def monitor_flight_mode():
    print("Monitoring")
    async for mode in drone.telemetry.flight_mode():
        print(f"Mode: {mode}")

    async for pos in drone.telemetry.position():
        relAlt = pos.relative_altitude_m
        print(f"Rel Alt: {relAlt}")

            

async def flying_post_office():
    print("going to post office")
    await drone.offboard.set_position_ned(PositionNedYaw(-28.26, -27.91, -13, 0))




async def main():
    global loop
    loop = asyncio.get_running_loop()

    # Start keyboard listener (separate thread)
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # Run drone setup + telemetry concurrently
    await setup_drone()

    print("monitoring")

    await asyncio.gather(
        monitor_flight_mode(),
        flying_post_office(),
    )

if __name__ == "__main__":
    asyncio.run(main())