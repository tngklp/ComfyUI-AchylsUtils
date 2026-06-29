import os
import torch
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import folder_paths


class SaveImageNoMetadata:
    """
    Save Image (No Metadata)

    Strips all generation metadata (prompts, workflow, etc.) from images
    by detaching and cloning the tensor, then saves them as PNG files
    with no embedded metadata.
    """

    CATEGORY = "AchylsUtils/Image"

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "save"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {
                    "tooltip": "The images to save with no metadata.",
                }),
                "filename_prefix": ("STRING", {
                    "default": "Achyls",
                    "tooltip": "The prefix for the saved file. May include formatting like %date:yyyy-MM-dd%.",
                }),
            },
        }

    def save(self, images, filename_prefix="Achyls"):
        # Strip any metadata by detaching and cloning
        cleaned_images = images.detach().clone()

        # Build output path
        output_dir = folder_paths.get_output_directory()
        subfolder = ""
        full_output_folder = os.path.join(output_dir, subfolder)

        os.makedirs(full_output_folder, exist_ok=True)

        # Counter to avoid overwriting files
        counter = 1
        while True:
            file = f"{filename_prefix}_{counter:05d}_.png"
            file_path = os.path.join(full_output_folder, file)
            if not os.path.exists(file_path):
                break
            counter += 1

        # Convert tensor to PIL images, saving each frame
        results = list()
        for image_tensor in cleaned_images:
            # Tensor is (H, W, C) in float 0..1, convert to uint8 0..255
            img_np = image_tensor.cpu().numpy()
            img_np = np.clip(img_np * 255.0, 0, 255).astype(np.uint8)
            pil_image = Image.fromarray(img_np, mode="RGB")

            # Save with NO metadata (empty PngInfo)
            metadata = PngInfo()
            pil_image.save(file_path, pnginfo=metadata, optimize=True)

            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": "output",
            })

        return {"ui": {"images": results}}
