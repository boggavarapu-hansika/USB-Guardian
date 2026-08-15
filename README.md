# 🔐 USB Guardian

USB Guardian is a Python project I made to monitor USB devices connected to a Windows computer.

The main idea is to check whether a connected USB device is trusted or not. If an unknown device is connected, the application gives an alert.

## What it does

- Detects USB devices
- Checks devices with a trusted device list
- Alerts when an unknown device is connected
- Records USB activity
- Has a simple GUI

## Technologies I Used

- Python
- Tkinter
- WMI
- Windows

## How it works

1. The program monitors USB devices.
2. When a USB device is connected, it detects it.
3. It checks the device with the trusted device list.
4. If it is trusted, it is recognized.
5. If it is not trusted, an alert is shown.

## Project Files

```text
USB-Guardian/
│
├── README.md
├── .gitignore
│
└── project.py/
    ├── backend.py
    ├── frontend.py
    └── trusted_devices.txt
