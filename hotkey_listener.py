#!/usr/bin/env python3
"""Global hotkey listener to launch snapcitr app."""

import subprocess
import sys
from pathlib import Path

from pynput import keyboard

# Configuration
HOTKEY = {keyboard.Key.ctrl_l, keyboard.Key.print_screen}
APP_PATH = Path(__file__).parent / "main.py"

# Track currently pressed keys
current_keys = set()


def on_press(key: keyboard.Key | keyboard.KeyCode | None) -> None:
    """Called when a key is pressed."""
    if key is None:
        return

    current_keys.add(key)

    # Check if hotkey combination is pressed
    if current_keys >= HOTKEY:
        print("Hotkey detected! Launching snapcitr...")
        # Launch the app in a new process
        subprocess.Popen([sys.executable, str(APP_PATH)])
        # Clear keys to prevent repeated launches
        current_keys.clear()


def on_release(key: keyboard.Key | keyboard.KeyCode | None) -> None:
    """Called when a key is released."""
    if key is None:
        return

    try:
        current_keys.discard(key)
    except KeyError:
        pass


if __name__ == "__main__":
    print(
        "Snapcitr hotkey listener started.",
        "Press Ctrl+PrintScreen to launch the snapshot tool.",
        "Press Ctrl+C to exit.",
        sep="\n",
    )

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
