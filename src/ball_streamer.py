# ==========================================
# BALL2HEAD — Trionda Smart Ball Bluetooth Streamer
# Purpose: Connect wirelessly to the real ball → get acceleration → calculate energy LIVE
# Key Rule: The PHYSICS formula stays in ONE place (compute_energy.py) — we just reuse it here
# ==========================================

import asyncio
import numpy as np
from bleak import BleakScanner, BleakClient

# ✅ REUSE OUR PROVEN PHYSICS — NO DUPLICATE CODE!
# This means: if we ever update the formula, it updates EVERYWHERE automatically
from compute_energy import calculate_impact_energy

# ==========================================
# BALL CONNECTION DETAILS
# These are standard codes that tell Bluetooth: "talk to THIS specific device"
# ==========================================

# What name to look for when scanning — ball should have "Trionda" in its name
TRIONDA_NAME_SUBSTRING = "Trionda"

# These UUID numbers are like Bluetooth "channel codes" given by the manufacturer
SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"  # Main ball service
CHAR_UUID = "0000ffe4-0000-1000-8000-00805f9b34fb"    # Where IMU acceleration data lives


class TriondaBallStreamer:
    """
    Handles everything related to the physical ball:
    - Scanning nearby
    - Connecting via Bluetooth
    - Receiving acceleration readings
    - Running them through our physics formula
    """

    def __init__(self):
        # When we create this tool → start with NO connection
        self.client = None       # Will hold our Bluetooth connection
        self.connected = False   # Are we connected? True = yes, False = no


    async def scan_and_connect(self):
        """Search Bluetooth area → find Trionda ball → connect to it"""
        print("🔍 Scanning for Trionda ball...")

        # Ask Bluetooth: "show me EVERYTHING nearby"
        devices = await BleakScanner.discover()

        # Check each found device → does it say "Trionda" in its name?
        for dev in devices:
            if dev.name and TRIONDA_NAME_SUBSTRING.lower() in dev.name.lower():
                print(f"✅ Found: {dev.name} ({dev.address})")

                # Create a Bluetooth connection to THIS specific ball
                self.client = BleakClient(dev.address)
                await self.client.connect()
                self.connected = True

                print("🔗 Connected to Trionda ball!")
                return True  # Success!

        # If we finish the loop and found nothing
        print("❌ Trionda ball not found.")
        return False


    def decode_imu_data(self, data: bytes):
        """
        THE BALL SENDS COMPRESSED DATA → WE UNPACK IT HERE
        Raw bytes → real acceleration numbers (m/s²)
        
        How it works:
        - Ball sends integers (whole numbers) to save space
        - We divide by 100 to get back to real m/s² values
        - Little-endian = how THIS ball orders its bytes (manufacturer choice)
        """
        ax = int.from_bytes(data[0:2], byteorder='little', signed=True) / 100.0
        ay = int.from_bytes(data[2:4], byteorder='little', signed=True) / 100.0
        az = int.from_bytes(data[4:6], byteorder='little', signed=True) / 100.0
        return ax, ay, az


    async def stream_live(self, callback):
        """
        START RECEIVING DATA FOREVER
        Every time the ball sends a reading:
            1. Unpack the 3 acceleration values
            2. Run through PHYSICS formula → get impact energy
            3. Pass EVERYTHING to whatever wants to use it (print, dashboard, save, etc.)
        """

        # If not connected yet → try to find and connect first
        if not self.connected:
            if not await self.scan_and_connect():
                return  # Failed → stop here

        # ==========================================
        # WHAT TO DO WHEN BALL SENDS NEW DATA
        # ==========================================
        def handle_data(_, data):
            # Step 1: Unpack raw bytes → real acceleration values
            ax, ay, az = self.decode_imu_data(data)

            # Step 2: Calculate IMPACT ENERGY using our PHYSICS FORMULA
            # NOTE: Same exact formula as API → NO DIFFERENCE
            energy = calculate_impact_energy(ax, ay, az)

            # Step 3: Hand results to whoever started this stream
            # (Could be: print to screen, send to dashboard, save to CSV...)
            callback(ax, ay, az, energy)

        # ==========================================
        # START LISTENING — ball will call handle_data() automatically
        # ==========================================
        await self.client.start_notify(CHAR_UUID, handle_data)

        # Keep program running while ball is connected
        while self.connected:
            # Small pause — gives Bluetooth time to breathe (adjust if needed)
            # Note: Ball runs at 500Hz → this just keeps our code happy
            await asyncio.sleep(0.01)


    async def disconnect(self):
        """Cleanly end Bluetooth connection"""
        if self.client:
            await self.client.disconnect()
            self.connected = False
            print("🔌 Disconnected")


# ==========================================
# TEST RUN — If you run THIS FILE directly, it shows results on screen
# ==========================================
if __name__ == "__main__":

    # This function gets called EVERY TIME the ball sends new data
    async def print_result(ax, ay, az, e):
        print(f"📡 Live: ax={ax:.2f} ay={ay:.2f} az={az:.2f} → Energy={e:.6f} J")

    # Create our ball connection tool
    streamer = TriondaBallStreamer()

    try:
        # Start streaming — will print every reading live
        asyncio.run(streamer.stream_live(print_result))

    # Press Ctrl+C to stop gracefully
    except KeyboardInterrupt:
        asyncio.run(streamer.disconnect())