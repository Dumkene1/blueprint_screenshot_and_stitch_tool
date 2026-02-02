from pathlib import Path

from config import CaptureSettings
from capture import capture_grid
from stitcher import stitch_tiles


def run_capture_pipeline(settings: CaptureSettings) -> Path:
    """
    Run the full pipeline:
    1. Capture grid of screenshots.
    2. Stitch into one big image.
    3. Save to disk.
    """
    print("Starting capture pipeline with settings:")
    print(settings)

    tiles, tile_w, tile_h = capture_grid(settings)
    print(f"Captured {len(tiles)} tiles of size {tile_w}x{tile_h}")

    stitched = stitch_tiles(tiles, settings)

    output_path = Path(settings.output_name).resolve()
    stitched.save(output_path)
    print(f"Saved stitched blueprint image to: {output_path}")

    return output_path
