import time
from pathlib import Path

import pyautogui
import pygetwindow as gw
from PIL import Image


def find_unreal_window(window_keyword: str = "Unreal Editor"):
    """
    Find the first window whose title contains window_keyword.
    """
    titles = gw.getAllTitles()
    for title in titles:
        if window_keyword.lower() in title.lower():
            windows = gw.getWindowsWithTitle(title)
            if windows:
                return windows[0]

    raise RuntimeError(
        f"Could not find a window with keyword '{window_keyword}'. "
        f"Make sure Unreal is running and the editor window is visible."
    )


def capture_unreal_window_screenshot(
    window_keyword: str,
    save_path: Path,
    delay: float = 1.5,
) -> Path:
    """
    Capture the region of the Unreal window and save it to save_path.
    delay: seconds to wait before actually taking the screenshot
           (gives time for our app to minimize and for Unreal to redraw).
    """
    win = find_unreal_window(window_keyword)

    # Get window bounds (including title bar).
    left, top, width, height = win.left, win.top, win.width, win.height

    # Optional: you could adjust these to only capture the client area.
    bbox = (left, top, left + width, top + height)

    # Wait a bit so the user sees Unreal after our app minimizes.
    time.sleep(delay)

    img = pyautogui.screenshot(region=bbox)
    img.save(save_path)
    return save_path
