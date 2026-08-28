# src/ball_streamer.py
import asyncio
import numpy as np
from bleak import BleakScanner, BleakClient
from compute_energy import calculate_impact_energy  # Reuse your proven physics

# === TRIONDA BALL SPECS — ADJUST UUIDS PER YOUR DEVICE DOC ===
TRIONDA_NAME_SUBSTRING = "Trionda"
SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"  # Example BLE service
CHAR_UUID = "0000ffe4-0000-1000-8000-00805f9b34fb"    # Characteristic for IMU data

class TriondaBallStreamer:
    def __init__(self):
        self.client = None
        self.connected = False

    async def scan_and_connect(self):
        print("🔍 Scanning for Trionda ball...")
        devices = await BleakScanner.discover()
        for dev in devices:
            if dev.name and TRIONDA_NAME_SUBSTRING.lower() in dev.name.lower():
                print(f"✅ Found: {dev.name} ({dev.address})")
                self.client = BleakClient(dev.address)
                await self.client.connect()
                self.connected = True
                print("🔗 Connected to Trionda ball!")
                return True
        print("❌ Trionda ball not found.")
        return False

    def decode_imu_data(self, data: bytes):
        """Convert raw BLE bytes → ax, ay, az (m/s²) — adjust endianness/scaling per Trionda spec"""
        # EXAMPLE DECODING — UPDATE WITH YOUR BALL'S FORMAT!
        ax = int.from_bytes(data[0:2], byteorder='little', signed=True) / 100.0
        ay = int.from_bytes(data[2:4], byteorder='little', signed=True) / 100.0
        az = int.from_bytes(data[4:6], byteorder='little', signed=True) / 100.0
        return ax, ay, az

    async def stream_live(self, callback):
        """Stream forever — pass energy results to callback"""
        if not self.connected:
            if not await self.scan_and_connect():
                return

        def handle_data(_, data):
            ax, ay, az = self.decode_imu_data(data)
            energy = calculate_impact_energy(ax, ay, az)
            callback(ax, ay, az, energy)

        await self.client.start_notify(CHAR_UUID, handle_data)
        while self.connected:
            await asyncio.sleep(0.01)  # Match 500Hz → 0.002s, but yield to event loop

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()
            self.connected = False
            print("🔌 Disconnected")

# Example test run
if __name__ == "__main__":
    async def print_result(ax, ay, az, e):
        print(f"📡 Live: ax={ax:.2f} ay={ay:.2f} az={az:.2f} → Energy={e:.6f} J")
    streamer = TriondaBallStreamer()
    try:
        asyncio.run(streamer.stream_live(print_result))
    except KeyboardInterrupt:
        asyncio.run(streamer.disconnect())