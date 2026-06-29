import torch


class BatchSlicer:
    """
    Batch Slicer/Splitter

    Takes a batch of images and an index, and splits the batch into
    "Before Index" and "After Index" (or extracts just the image at the index).
    """

    CATEGORY = "AchylsUtils/Batch"

    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = ("before_index", "at_index", "after_index")
    OUTPUT_TOOLTIPS = (
        "Images before the selected index (may be empty batch).",
        "The single image at the selected index.",
        "Images after the selected index (may be empty batch).",
    )
    FUNCTION = "slice"
    DESCRIPTION = (
        "Splits a batch of images at a given index. Outputs three tensors: "
        "images before the index, the single image at the index, "
        "and images after the index."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {
                    "tooltip": "The batch of images to slice.",
                }),
                "index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffff,
                    "tooltip": "Index at which to split the batch.",
                }),
            },
        }

    def slice(self, images, index=0):
        total = images.shape[0]
        # Clamp index
        idx = max(0, min(index, total - 1)) if total > 0 else 0

        before = images[:idx] if idx > 0 else torch.empty((0, *images.shape[1:]), dtype=images.dtype, device=images.device)
        at_img = images[idx:idx + 1] if total > 0 else torch.empty((0, *images.shape[1:]), dtype=images.dtype, device=images.device)
        after = images[idx + 1:] if idx + 1 < total else torch.empty((0, *images.shape[1:]), dtype=images.dtype, device=images.device)

        return (before, at_img, after)
