#!/usr/bin/env python3

"""
Caveat when attempting to run the examples in non-gps environments:

`drone.offboard.stop()` will return a `COMMAND_DENIED` result because it
requires a mode switch to HOLD, something that is currently not supported in a
non-gps environment.
"""

import asyncio
import logging

from mavsdk import System
from mavsdk.offboard import OffboardError, PositionNedYaw

# Enable INFO level logging by default so that INFO messages are shown
logging.basicConfig(level=logging.INFO)


async def run():
    """Does Offboard control using position NED coordinates."""

    drone = System()
    # await drone.connect(system_address="udpin://0.0.0.0:14540")
    await drone.connect(system_address="serial:///dev/ttyACM0:57600")


    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to drone!")
            break
    
    print("FINISHED")


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())

