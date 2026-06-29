import torch
import comfy.model_management


class EmptyLatentFromImage:
    """
    Empty Latent from Image

    Takes an image input and outputs an Empty Latent with the exact dimensions
    of that image. Saves routing through "Get Image Size" + "Empty Latent" nodes.
    """

    CATEGORY = "AchylsUtils/Latent"

    RETURN_TYPES = ("LATENT", "INT", "INT")
    RETURN_NAMES = ("latent", "width", "height")
    OUTPUT_TOOLTIPS = (
        "An empty latent matching the input image's dimensions.",
        "The image width in pixels.",
        "The image height in pixels.",
    )
    FUNCTION = "generate"
    DESCRIPTION = (
        "Creates an empty latent tensor with the exact dimensions of a given image. "
        "Saves you from having to use Get Image Size + Empty Latent nodes separately."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "The reference image whose dimensions will be used.",
                }),
                "batch_size": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 64,
                    "tooltip": "Number of latents to generate.",
                }),
            },
        }

    def generate(self, image, batch_size=1):
        # ComfyUI IMAGE tensor is (B, H, W, C)
        img_h = image.shape[1]
        img_w = image.shape[2]

        # Latent is 1/8th resolution
        latent_h = img_h // 8
        latent_w = img_w // 8

        latent = torch.zeros(
            [batch_size, 4, latent_h, latent_w],
            device=comfy.model_management.intermediate_device(),
        )

        return ({"samples": latent}, img_w, img_h)
