import tkinter as tk
from datetime import datetime
from backend import list_plug_and_play_devices, load_trusted_devices, check_device, log_event

seen_devices = set()
auto_scan_on = True
scheduled_job = None  # tracks the pending scan so we can cancel it cleanly

window = tk.Tk()
window.title("USB Guardian")
window.geometry("460x560")
window.configure(bg="#1e1e2e")
window.resizable(False, False)

title_label = tk.Label(window, text="🔐 USB GUARDIAN", font=("Segoe UI", 18, "bold"), bg="#1e1e2e", fg="#ffffff")
title_label.pack(pady=(20, 4))

subtitle_label = tk.Label(window, text="Real-time USB device monitor", font=("Segoe UI", 9), bg="#1e1e2e", fg="#888899")
subtitle_label.pack(pady=(0, 15))

status_frame = tk.Frame(window, bg="#1e1e2e")
status_frame.pack(pady=(0, 15))

status_dot = tk.Label(status_frame, text="●", font=("Arial", 12), bg="#1e1e2e", fg="#2ecc71")
status_dot.pack(side="left")

status_label = tk.Label(status_frame, text=" Monitoring — checking every 5s", font=("Segoe UI", 10), bg="#1e1e2e", fg="#cccccc")
status_label.pack(side="left")

card = tk.Frame(window, bg="#2a2a3d", padx=20, pady=16)
card.pack(padx=20, fill="x")

device_title = tk.Label(card, text="LAST DETECTED DEVICE", font=("Segoe UI", 9, "bold"), bg="#2a2a3d", fg="#7a7a90")
device_title.pack(anchor="w")

device_name = tk.Label(card, text="Waiting for first scan…", font=("Segoe UI", 14, "bold"), bg="#2a2a3d", fg="#ffffff", wraplength=380, justify="left")
device_name.pack(anchor="w", pady=(4, 8))

device_status = tk.Label(card, text="Status: —", font=("Segoe UI", 11), bg="#2a2a3d", fg="#f1c40f")
device_status.pack(anchor="w")

device_time = tk.Label(card, text="", font=("Segoe UI", 8), bg="#2a2a3d", fg="#666677")
device_time.pack(anchor="w", pady=(6, 0))

controls_frame = tk.Frame(window, bg="#1e1e2e")
controls_frame.pack(pady=16)


def manual_scan():
    global scheduled_job
    if scheduled_job is not None:
        window.after_cancel(scheduled_job)
        scheduled_job = None
    scan_status_label.config(text="Scanning now…")
    window.after(300, scan_devices)


refresh_btn = tk.Button(controls_frame, text="🔄  Scan Now", command=manual_scan, bg="#3b3b55", fg="white",
                         font=("Segoe UI", 10, "bold"), activebackground="#4a4a6a", activeforeground="white",
                         bd=0, padx=14, pady=6, cursor="hand2")
refresh_btn.grid(row=0, column=0, padx=6)


def toggle_auto_scan():
    global auto_scan_on, scheduled_job
    auto_scan_on = not auto_scan_on
    if auto_scan_on:
        auto_btn.config(text="⏸  Pause Auto-Scan", bg="#3b3b55")
        scan_status_label.config(text="Auto-scan resumed")
        scan_devices()
    else:
        auto_btn.config(text="▶  Resume Auto-Scan", bg="#55553b")
        scan_status_label.config(text="Auto-scan paused")
        if scheduled_job is not None:
            window.after_cancel(scheduled_job)
            scheduled_job = None


auto_btn = tk.Button(controls_frame, text="⏸  Pause Auto-Scan", command=toggle_auto_scan, bg="#3b3b55", fg="white",
                      font=("Segoe UI", 10, "bold"), activebackground="#4a4a6a", activeforeground="white",
                      bd=0, padx=14, pady=6, cursor="hand2")
auto_btn.grid(row=0, column=1, padx=6)

scan_status_label = tk.Label(window, text="", font=("Segoe UI", 8, "italic"), bg="#1e1e2e", fg="#888899")
scan_status_label.pack(pady=(0, 10))

activity_header = tk.Frame(window, bg="#1e1e2e")
activity_header.pack(fill="x", padx=20)

activity_label = tk.Label(activity_header, text="RECENT ACTIVITY", font=("Segoe UI", 9, "bold"), bg="#1e1e2e", fg="#7a7a90")
activity_label.pack(side="left")

count_label = tk.Label(activity_header, text="0 devices seen", font=("Segoe UI", 8), bg="#1e1e2e", fg="#666677")
count_label.pack(side="right")

list_frame = tk.Frame(window, bg="#1e1e2e")
list_frame.pack(padx=20, pady=(6, 20), fill="both", expand=True)

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

activity_box = tk.Listbox(list_frame, bg="#2a2a3d", fg="#dddddd", font=("Segoe UI", 9), height=10, bd=0,
                           highlightthickness=0, selectbackground="#3b3b55", yscrollcommand=scrollbar.set)
activity_box.pack(side="left", fill="both", expand=True)
scrollbar.config(command=activity_box.yview)

activity_box.insert(0, "No activity yet — waiting for first scan…")


def scan_devices():
    global scheduled_job
    trusted_list = load_trusted_devices()
    devices = list_plug_and_play_devices()
    new_found = False

    for d in devices:
        device_id = d["device_id"]
        name = d["name"]

        if device_id not in seen_devices:
            seen_devices.add(device_id)
            new_found = True

            is_trusted = check_device(device_id, trusted_list)
            status_text = "TRUSTED" if is_trusted else "UNKNOWN"
            icon = "✅" if is_trusted else "⚠️"
            now_str = datetime.now().strftime("%I:%M:%S %p")

            device_name.config(text=name)
            device_status.config(text=f"Status: {icon} {status_text}", fg="#2ecc71" if is_trusted else "#e74c3c")
            device_time.config(text=f"Detected at {now_str}")

            if activity_box.get(0) == "No activity yet — waiting for first scan…":
                activity_box.delete(0)

            activity_box.insert(0, f"{icon}  {now_str}   {name} — {status_text}")
            log_event(name, status_text)

    count_label.config(text=f"{len(seen_devices)} device(s) seen")
    scan_status_label.config(text="Up to date" if not new_found else "New device found!")

    if auto_scan_on:
        scheduled_job = window.after(5000, scan_devices)


def on_close():
    global scheduled_job
    if scheduled_job is not None:
        window.after_cancel(scheduled_job)
        scheduled_job = None
    window.destroy()


window.protocol("WM_DELETE_WINDOW", on_close)
scheduled_job = window.after(800, scan_devices)
window.mainloop()