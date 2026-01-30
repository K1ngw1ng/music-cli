#!/usr/bin/env python3

import sys
import subprocess
import threading
from pathlib import Path
from pynput import keyboard

if len(sys.argv) < 2:
    print("Usage: music.py <music-directory>")
    sys.exit(1)

MUSIC_DIR = Path(sys.argv[1]).expanduser()
FILES = sorted([f for f in MUSIC_DIR.iterdir() if f.suffix.lower() in (".mp3", ".wav", ".flac", ".ogg")])

if not FILES:
    print("No audio files found.")
    sys.exit(1)

index = 0
player = None
paused = False

def play():
    global player, paused
    if player:
        player.terminate()
    print(f"\n▶ Playing: {FILES[index].name}")
    player = subprocess.Popen(
        ["mpv", "--no-video", "--quiet", FILES[index]],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    paused = False

def next_track():
    global index
    index = (index + 1) % len(FILES)
    play()

def prev_track():
    global index
    index = (index - 1) % len(FILES)
    play()

def toggle_pause():
    global paused
    if player and player.stdin:
        player.stdin.write(b"cycle pause\n")
        player.stdin.flush()
        paused = not paused
        print("⏸ Paused" if paused else "▶ Resumed")

def on_press(key):
    try:
        if key.char == "n":
            next_track()
        elif key.char == "p":
            prev_track()
        elif key.char == " ":
            toggle_pause()
        elif key.char == "q":
            print("\nExiting...")
            if player:
                player.terminate()
            return False
    except AttributeError:
        pass

print("""
Controls:
 space  → play / pause
 n      → next track
 p      → previous track
 q      → quit
""")

play()

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()