import time
from dataclasses import dataclass
from typing import List, Tuple

import pyautogui
import pygetwindow as gw
from PIL import Image

from config import CaptureSettings


@dataclass
class TileCapture:
    col: int
    row: int
    image: Image.Image


def find_unreal_window(window_keyword: str):
    """Find the Unreal Editor window whose title contains the keyword."""
    titles = gw.getAllTitles()
    for title in titles:
        if window_keyword.lower() in title.lower():
            windows = gw.getWindowsWithTitle(title)
            if windows:
                return windows[0]
    raise RuntimeError(
        f"Could not find Unreal window with keyword '{window_keyword}'. "
        f"Open the Blueprint editor and check the window title."
    )


def bring_to_front(unreal_window):
    """Activate the Unreal window."""
    unreal_window.activate()
    time.sleep(1)
    if not unreal_window.isActive:
        print("Warning: Unreal window may not be active. Click it manually quickly before capture.")


def capture_grid(settings: CaptureSettings) -> Tuple[List[TileCapture], int, int]:
    """
    Capture a grid of screenshots from the Unreal Blueprint window.

    Returns:
        (tiles, tile_width, tile_height)
    """
    print(f"Searching for Unreal window with keyword: {settings.window_keyword!r}")
    win = find_unreal_window(settings.window_keyword)
    bring_to_front(win)

    left, top, width, height = win.left, win.top, win.width, win.height
    print(f"Using window region: left={left}, top={top}, width={width}, height={height}")

    print(
        f"Place your mouse over the Blueprint graph area.\n"
        f"Capture will start in {settings.countdown} seconds..."
    )
    time.sleep(settings.countdown)

    tiles: List[TileCapture] = []

    for row in range(settings.grid_rows):
        for col in range(settings.grid_cols):
            # Take screenshot of current view
            bbox = (left, top, left + width, top + height)
            img = pyautogui.screenshot(region=bbox)
            tiles.append(TileCapture(col=col, row=row, image=img))
            print(f"Captured tile ({col}, {row})")
            time.sleep(settings.delay)

            # Pan to the right unless we're at end of row
            if col < settings.grid_cols - 1:
                distance = settings.pan_x - settings.overlap
                # NOTE: dragging mouse LEFT moves the view RIGHT in many apps.
                # If direction feels inverted, flip the sign.
                pyautogui.dragRel(-distance, 0, duration=0.5, button='middle')
                time.sleep(settings.delay)

        # Move back to left and down for next row
        if row < settings.grid_rows - 1:
            # Pan back left to starting column
            back_distance = (settings.grid_cols - 1) * (settings.pan_x - settings.overlap)
            pyautogui.dragRel(back_distance, 0, duration=1.0, button='middle')
            time.sleep(settings.delay)

            # Pan down (again, sign might need flipping depending on Unreal behavior)
            distance = settings.pan_y - settings.overlap
            pyautogui.dragRel(0, -distance, duration=0.5, button='middle')
            time.sleep(settings.delay)

    # All tiles should be same size (window size)
    tile_w, tile_h = width, height
    return tiles, tile_w, tile_h
