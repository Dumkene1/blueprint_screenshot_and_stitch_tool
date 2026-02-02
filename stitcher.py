from pathlib import Path
from typing import List
from PIL import Image


def load_images_from_folder(folder: Path) -> List[Image.Image]:
    """
    Load images from a folder, sorted by filename.
    Supports PNG/JPG/JPEG.
    """
    image_paths = sorted(
        [p for p in folder.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"}]
    )
    if not image_paths:
        raise ValueError(f"No PNG/JPG images found in {folder}")

    images = [Image.open(p) for p in image_paths]
    return images


def stitch_grid(
    images: List[Image.Image],
    cols: int,
    rows: int,
    overlap_x: int = 0,
    overlap_y: int = 0,
) -> Image.Image:
    """
    Stitch a list of images arranged in a grid (left->right, top->bottom).

    images: list of PIL Images (length must be cols * rows)
    cols, rows: grid dimensions
    overlap_x, overlap_y: how many pixels each image overlaps its neighbor
    """
    if len(images) != cols * rows:
        raise ValueError(
            f"Number of images ({len(images)}) does not match cols*rows ({cols*rows})"
        )

    tile_w, tile_h = images[0].size

    # Make sure all images are same size
    for img in images:
        if img.size != (tile_w, tile_h):
            raise ValueError("All images must have the same resolution.")

    step_x = tile_w - overlap_x
    step_y = tile_h - overlap_y

    total_w = cols * step_x
    total_h = rows * step_y

    result = Image.new("RGB", (total_w, total_h))

    index = 0
    for row in range(rows):
        for col in range(cols):
            img = images[index]
            index += 1

            x = col * step_x
            y = row * step_y
            result.paste(img, (x, y))

    return result
