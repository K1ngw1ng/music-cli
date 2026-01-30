#!/usr/bin/env python3

import curses
import time
from pathlib import Path
from mpv import MPV

AUDIO_EXTS = (".mp3", ".flac", ".wav", ".ogg", ".m4a")

def load_tracks(directory):
    return sorted(
        [p for p in Path(directory).expanduser().iterdir()
         if p.suffix.lower() in AUDIO_EXTS]
    )

def format_meta(meta, fallback):
    return meta if meta else fallback

def draw_ui(stdscr, player, track, idx, total, volume):
    try:
        pos = player.time_pos or 0
        dur = player.duration or 0
    except Exception:
        pos, dur = 0, 0
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    def center(y, text, bold=False):
        x = max(0, (w - len(text)) // 2)
        if bold:
            stdscr.attron(curses.A_BOLD)
        stdscr.addstr(y, x, text)
        if bold:
            stdscr.attroff(curses.A_BOLD)

    meta = player.metadata or {}
    title = format_meta(meta.get("title"), track.stem)
    artist = format_meta(meta.get("artist"), "Unknown Artist")
    album = format_meta(meta.get("album"), "Unknown Album")

    center(2, "♪ - Music Player - ♪", True)
    center(4, title, True)
    center(6, f"{artist} — {album}")
    center(8, f"Track {idx + 1}/{total}")
        # progress bar
    bar_width = max(10, w - 20)
    progress = 0 if dur == 0 else min(1.0, pos / dur)
    filled = int(bar_width * progress)
    bar = "█" * filled + "─" * (bar_width - filled)

    def fmt(t):
        m, s = divmod(int(t), 60)
        return f"{m}:{s:02d}"

    center(10, f"[{bar}]")
    center(11, f"{fmt(pos)} / {fmt(dur)}")
    center(13, f"Volume: {volume}%")

    center(h - 5, "Space: Play/Pause   ←/→: Prev/Next")
    center(h - 4, "a / d: Seek −5s / +5s")
    center(h - 3, "+ / -: Volume   q: Quit")

    stdscr.refresh()

def main(stdscr, music_dir):
    curses.curs_set(0)
    stdscr.nodelay(True)

    tracks = load_tracks(music_dir)
    if not tracks:
        raise SystemExit("No audio files found.")

    # libmpv-safe options (DO NOT use no_video=True)
    player = MPV(
        vo="null",      # disable video output correctly
        vid="no",
        volume=70,
        input_default_bindings=False,
        input_vo_keyboard=False
    )

    index = 0
    volume = 70
    paused = False

    def play():
        player.play(str(tracks[index]))

    play()

    while True:
        draw_ui(stdscr, player, tracks[index], index, len(tracks), volume)

        key = stdscr.getch()

        if key == ord("q"):
            break

        elif key == ord(" "):
            paused = not paused
            player.pause = paused

        elif key in (curses.KEY_RIGHT, ord("n")):
            index = (index + 1) % len(tracks)
            play()

        elif key in (curses.KEY_LEFT, ord("p")):
            index = (index - 1) % len(tracks)
            play()

        elif key == ord("+"):
            volume = min(100, volume + 5)
            player.volume = volume

        elif key == ord("-"):
            volume = max(0, volume - 5)
            player.volume = volume

        elif key == ord("a"):
            if player.time_pos is not None:
                player.time_pos = max(0, player.time_pos - 5)

        elif key == ord("d"):
            if player.time_pos is not None and player.duration:
                player.time_pos = min(player.duration, player.time_pos + 5)
            volume = max(0, volume - 5)
            player.volume = volume

        time.sleep(0.05)

    player.terminate()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: tui_music.py <music-directory>")
        sys.exit(1)
    curses.wrapper(main, sys.argv[1])
