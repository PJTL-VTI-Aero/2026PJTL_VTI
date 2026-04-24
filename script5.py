#!/usr/bin/env python3
import asyncio
import logging
from mavsdk import System, telemetry
from mavsdk.offboard import PositionNedYaw, OffboardError, VelocityNedYaw
from pynput import keyboard

logging.basicConfig(level=logging.INFO)

# Globals
drone = None

async def setup_drone():
    global drone, relAlt
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

    print("-- Arming")
    
    await drone.action.arm()



    # async for pos in drone.telemetry.position():
    #     relAlt = pos.relative_altitude_m

    #     # Get one flight mode sample
    #     async for m in drone.telemetry.flight_mode():
    #         mode = m
    #         break

    #     print(f"Rel Alt: {relAlt:.2f} | Mode: {mode}")

    #     if relAlt >= 15 * 0.95:
    #         print("-- Target altitude reached")
    #         break

    height_reached = False

    async for pos in drone.telemetry.position():
        relAlt = pos.relative_altitude_m
        print(f"Rel Alt: {relAlt}")

        if relAlt >= 5 * 0.95: 
            print("-- Target altitude reached")
            height_reached = True
            break
      


async def control_loop():

    while True:

        async for m in drone.telemetry.flight_mode():
            mode = m
            break

        print(f"Mode: {mode}")
    
        if mode == telemetry.FlightMode.HOLD and relAlt >= 4:
            print("Agree to take control?")
            await asyncio.to_thread(input)  
            
            await drone.offboard.set_velocity_ned(
               VelocityNedYaw(1, 0.0, 0.0, 0.0)  # 1 m/s forward
            )

            await drone.offboard.start()
            await asyncio.sleep(2)
            await drone.offboard.set_velocity_ned(
               VelocityNedYaw(0.0, 0.0, 0.0, 0.0)  # 1 m/s forward
            )








async def main():
    global loop

    await setup_drone()
    await control_loop()

if __name__ == "__main__":
    asyncio.run(main())
