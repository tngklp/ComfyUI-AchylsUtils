import torch
import numpy as np
from PIL import Image


class ImageGridComposer:
    """
    Image Grid Composer

    Takes a batch of images, a columns integer, and optional padding,
    and outputs a clean grid.
    """

    CATEGORY = "AchylsUtils/Image"

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("grid",)
    OUTPUT_TOOLTIPS = ("The composed grid image.",)
    FUNCTION = "compose"
    DESCRIPTION = (
        "Composes a batch of images into a grid layout with configurable "
        "columns and padding."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {
                    "tooltip": "Batch of images to arrange in a grid.",
                }),
                "columns": ("INT", {
                    "default": 4,
                    "min": 1,
                    "max": 64,
                    "tooltip": "Number of columns in the grid.",
                }),
                "padding": ("INT", {
                    "default": 2,
                    "min": 0,
                    "max": 100,
                    "tooltip": "Padding (in pixels) between grid cells.",
                }),
            },
        }

    def compose(self, images, columns=4, padding=2):
        batch_size = images.shape[0]
        if batch_size == 0:
            return (images,)

        img_h = images.shape[1]
        img_w = images.shape[2]

        rows = (batch_size + columns - 1) // columns

        cell_w = img_w + padding * 2
        cell_h = img_h + padding * 2

        grid_w = columns * cell_w + padding
        grid_h = rows * cell_h + padding

        grid_np = np.zeros((grid_h, grid_w, 3), dtype=np.float32)

        for i in range(batch_size):
            col = i % columns
            row = i // columns

            img_tensor = images[i].cpu().numpy()

            x = padding + col * cell_w
            y = padding + row * cell_h

            grid_np[y + padding:y + padding + img_h, x + padding:x + padding + img_w, :] = img_tensor

        grid_tensor = torch.from_numpy(grid_np).unsqueeze(0).to(dtype=images.dtype, device=images.device)
        return (grid_tensor,)
