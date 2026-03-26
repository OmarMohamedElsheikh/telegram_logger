import os
import subprocess


def notify(name, text, sound_path):
    try:
        subprocess.Popen(["paplay", sound_path])

        env = os.environ.copy()
        env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path=/run/user/{os.getuid()}/bus"

        subprocess.Popen(["notify-send", name, text or ""], env=env)

    except Exception as e:
        print(f"[WARN] notification failed: {e}")
