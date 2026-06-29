import torch
import numpy as np
from PIL import Image


class SmartCropAndPad:
    """
    Smart Crop & Pad

    Takes an image of any size and a target resolution.
    Instead of just stretching, it intelligently centers, crops the overflow,
    and pads the remainder (with edge-color stretching or solid black)
    to hit exact target dimensions without distortion.
    """

    CATEGORY = "AchylsUtils/Image"

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    OUTPUT_TOOLTIPS = ("The resized image at exact target dimensions without distortion.",)
    FUNCTION = "process"
    DESCRIPTION = (
        "Takes an image of any size and fits it into a target resolution "
        "without distortion. In 'crop' mode it scale-crops to cover (no padding needed). "
        "In 'fit' mode it letterboxes with padding controlled by pad_mode "
        "(edge_stretch extends border pixels, solid_black/solid_white fill with color)."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "The input image to crop and pad.",
                }),
                "target_width": ("INT", {
                    "default": 1024,
                    "min": 64,
                    "max": 16384,
                    "step": 8,
                    "tooltip": "Target width in pixels.",
                }),
                "target_height": ("INT", {
                    "default": 1024,
                    "min": 64,
                    "max": 16384,
                    "step": 8,
                    "tooltip": "Target height in pixels.",
                }),
                "mode": (["crop", "fit"], {
                    "default": "crop",
                    "tooltip": "'crop' scale-crops to fill target (no padding). 'fit' letterboxes to fit inside target with padding.",
                }),
                "pad_mode": (["edge_stretch", "solid_black", "solid_white"], {
                    "default": "edge_stretch",
                    "tooltip": "Padding method (used in 'fit' mode): edge_stretch extends border pixels, solid_black/solid_white fill with color.",
                }),
            },
        }

    def process(self, image, target_width, target_height, mode="crop", pad_mode="edge_stretch"):
        # Input image is (B, H, W, C) float 0..1
        batch = image.shape[0]
        channels = image.shape[3]

        # Determine padding color for solid modes
        if pad_mode == "solid_black":
            fill_color = (0.0,) * channels
        elif pad_mode == "solid_white":
            fill_color = (1.0,) * channels
        else:
            fill_color = None  # edge_stretch

        output_list = []
        for b in range(batch):
            img_np = image[b].cpu().numpy()  # (H, W, C) float 0..1
            h, w = img_np.shape[:2]

            if mode == "crop":
                # Scale to COVER the target area (scale up until both dimensions >= target)
                scale = max(target_width / w, target_height / h)
            else:
                # Scale to FIT inside the target area (scale up until one dimension hits target)
                scale = min(target_width / w, target_height / h)

            new_w = int(round(w * scale))
            new_h = int(round(h * scale))

            # Resize
            pil_img = Image.fromarray((np.clip(img_np * 255.0, 0, 255).astype(np.uint8)))
            pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)

            if mode == "crop":
                # Center crop to exact target dimensions
                left = (new_w - target_width) // 2
                top = (new_h - target_height) // 2
                right = left + target_width
                bottom = top + target_height
                result_img = pil_img.crop((left, top, right, bottom))
                arr = np.array(result_img).astype(np.float32) / 255.0
            else:
                # "fit" mode: place on a canvas, then pad
                canvas = Image.new("RGB", (target_width, target_height), (0, 0, 0))
                paste_x = (target_width - new_w) // 2
                paste_y = (target_height - new_h) // 2

                if fill_color is not None:
                    # Fill canvas with solid color first
                    rgb_fill = tuple(int(c * 255) for c in fill_color[:3])
                    canvas = Image.new("RGB", (target_width, target_height), rgb_fill)

                canvas.paste(pil_img, (paste_x, paste_y))

                # If edge_stretch, stretch the border pixels to fill remaining space
                if fill_color is None:
                    arr = np.array(canvas).astype(np.float32) / 255.0
                    # Edge-stretch left border
                    if paste_x > 0:
                        left_strip = arr[:, paste_x:paste_x + 1, :]
                        arr[:, :paste_x, :] = left_strip
                    # Edge-stretch right border
                    right_end = paste_x + new_w
                    if right_end < target_width:
                        right_strip = arr[:, right_end - 1:right_end, :]
                        arr[:, right_end:, :] = right_strip
                    # Edge-stretch top border
                    if paste_y > 0:
                        top_strip = arr[paste_y:paste_y + 1, :, :]
                        arr[:paste_y, :, :] = top_strip
                    # Edge-stretch bottom border
                    bottom_end = paste_y + new_h
                    if bottom_end < target_height:
                        bottom_strip = arr[bottom_end - 1:bottom_end, :, :]
                        arr[bottom_end:, :, :] = bottom_strip
                else:
                    arr = np.array(canvas).astype(np.float32) / 255.0

            output_list.append(arr)

        result = np.stack(output_list, axis=0)
        result = torch.from_numpy(result).to(dtype=image.dtype, device=image.device)
        return (result,)
