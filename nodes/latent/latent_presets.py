import json
import os
import torch
import comfy.model_management


# Determine the path to presets.json relative to this file
_PRESETS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "presets.json")


def _load_presets():
    """Load the presets dictionary from presets.json."""
    if not os.path.exists(_PRESETS_PATH):
        # Return an empty dict if the file doesn't exist yet
        return {}
    with open(_PRESETS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_preset_list():
    """Return a sorted list of preset names for the dropdown widget."""
    presets = _load_presets()
    return list(presets.keys())


class LatentImagePresets:
    """
    Latent Image Presets

    Select a preset resolution from a JSON file, or use custom width/height.
    Outputs an empty latent with the chosen dimensions and batch size.
    """

    CATEGORY = "AchylsUtils/Latent"

    RETURN_TYPES = ("LATENT", "INT", "INT")
    RETURN_NAMES = ("latent", "width", "height")
    OUTPUT_TOOLTIPS = (
        "The empty latent with the chosen resolution.",
        "The selected/input width in pixels.",
        "The selected/input height in pixels.",
    )
    FUNCTION = "generate"
    DESCRIPTION = (
        "Select a preset resolution from a JSON file, or use custom width/height. "
        "Outputs an empty latent with the chosen dimensions and batch size."
    )

    @classmethod
    def INPUT_TYPES(cls):
        presets = _get_preset_list()
        return {
            "required": {
                "preset": (presets, {
                    "tooltip": "Select a preset resolution. The JSON file (presets.json) can be edited to add/remove presets.",
                }),
                "batch_size": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 64,
                    "tooltip": "Number of images to generate in a batch.",
                }),
            },
        }

    def generate(self, preset, batch_size=1):
        presets = _load_presets()
        if preset in presets:
            w, h = presets[preset]
        else:
            # Fallback if the preset name is somehow invalid
            w, h = 1024, 1024

        # Create empty latent (1/8th resolution)
        latent = torch.zeros(
            [batch_size, 4, h // 8, w // 8],
            device=comfy.model_management.intermediate_device(),
        )
        return ({"samples": latent}, w, h)
