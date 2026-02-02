from dataclasses import dataclass

@dataclass
class CaptureSettings:
    # Part of the Unreal window title to search for.
    window_keyword: str = "Unreal Editor"

    # Grid of tiles to capture (columns x rows).
    grid_cols: int = 3
    grid_rows: int = 3

    # How far to pan between tiles (in pixels of graph movement).
    pan_x: int = 800
    pan_y: int = 600

    # Overlap between tiles (helps avoid gaps).
    overlap: int = 100

    # Delay between actions so Unreal has time to redraw.
    delay: float = 0.8

    # Countdown before capture starts so you can get ready.
    countdown: int = 5

    # Output file name for the stitched image.
    output_name: str = "blueprint_full_graph.png"
