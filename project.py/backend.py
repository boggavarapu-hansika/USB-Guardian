import wmi
from datetime import datetime


def list_plug_and_play_devices():
    c = wmi.WMI()
    devices = []
    for device in c.Win32_PnPEntity():
        if device.PNPClass == "USB" or (device.DeviceID and "USB" in str(device.DeviceID)):
            devices.append({
                "name": device.Name,
                "device_id": device.DeviceID
            })
    return devices


def load_trusted_devices(filepath="trusted_devices.txt"):
    try:
        with open(filepath, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def check_device(device_id, trusted_list):
    return device_id in trusted_list


def log_event(device_name, status, filepath="activity_log.txt"):
    timestamp = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    with open(filepath, "a") as f:
        f.write(f"{timestamp} | Device: {device_name} | Status: {status}\n")


if __name__ == "__main__":
    print("Scanning for USB devices...\n")
    usb_devices = list_plug_and_play_devices()
    trusted_list = load_trusted_devices()

    for d in usb_devices:
        is_trusted = check_device(d["device_id"], trusted_list)
        status = "TRUSTED" if is_trusted else "UNKNOWN"
        icon = "✅" if is_trusted else "⚠️"

        print(f"Name: {d['name']}")
        print(f"Device ID: {d['device_id']}")
        print(f"Status: {icon} {status}")
        print("-" * 40)

        log_event(d['name'], status)

    print("\n✅ Log saved to activity_log.txt")