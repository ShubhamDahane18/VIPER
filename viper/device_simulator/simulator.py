import time
import hashlib
import requests
import argparse
import os

API_URL = "http://localhost:8000/api"

def generate_checksum(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def simulate_transfer(audio_file: str, title: str, device_serial: str, roles: str):
    print(f"--- H-R191 SIMULATOR ---")
    print(f"[Device {device_serial}] Pairing initiated over BLE 5.4...")
    time.sleep(1.5)
    print(f"[Device {device_serial}] Paired successfully.")
    
    print(f"[Device {device_serial}] Calculating SHA256 checksum for {audio_file}...")
    checksum = generate_checksum(audio_file)
    print(f"[Device {device_serial}] Checksum: {checksum}")
    
    print(f"[Device {device_serial}] Initiating OPUS transfer (rate limited ~50KB/s)...")
    file_size = os.path.getsize(audio_file)
    time_to_transfer = min(5, file_size / 50000) # Mock time but capped so we don't wait forever
    # simulate some loading
    for i in range(1, 6):
        time.sleep(time_to_transfer / 5)
        print(f"Transferring... {i * 20}%")
        
    print(f"[Device {device_serial}] Transfer complete. Sending to Ingestion API...")
    
    with open(audio_file, "rb") as f:
        files = {"file": (os.path.basename(audio_file), f, "audio/wav")} # Using wav/opus mime
        data = {
            "title": title,
            "device_serial": device_serial,
            "allowed_roles": roles
        }
        headers = {"x-username": "eng_user"} # auth context
        
        try:
            response = requests.post(f"{API_URL}/meetings/ingest", files=files, data=data, headers=headers)
            if response.status_code == 200:
                print(f"[Device {device_serial}] Backend verification successful.")
                print(f"[Device {device_serial}] CLEARING ON-DEVICE FLASH...")
                time.sleep(1)
                print(f"[Device {device_serial}] Storage cleared. Ready for new audio.")
                print("Backend Response:")
                print(response.json())
            else:
                print(f"[Device {device_serial}] Backend error: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            print("ERROR: Could not connect to API on http://localhost:8000. Is the server running?")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-R191 Device Simulator")
    parser.add_argument("--file", type=str, required=True, help="Path to audio file (WAV/OPUS)")
    parser.add_argument("--title", type=str, default="Engineering Sync", help="Meeting Title")
    parser.add_argument("--serial", type=str, default="HR191-1055A", help="Device Serial Number")
    parser.add_argument("--roles", type=str, default="admin,engineering", help="ACL Roles allowed")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: Audio file {args.file} not found.")
    else:
        simulate_transfer(args.file, args.title, args.serial, args.roles)
