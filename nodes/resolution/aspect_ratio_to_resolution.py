import math


# Standard aspect ratios as (width_ratio, height_ratio) tuples
ASPECT_RATIOS = {
    "1:1 (Square)": (1, 1),
    "16:9 (Landscape)": (16, 9),
    "9:16 (Portrait)": (9, 16),
    "4:3 (Landscape)": (4, 3),
    "3:4 (Portrait)": (3, 4),
    "3:2 (Landscape)": (3, 2),
    "2:3 (Portrait)": (2, 3),
    "21:9 (Ultrawide)": (21, 9),
    "9:21 (Tall)": (9, 21),
}

# Optimal pixel counts (target total pixels) for different models
OPTIMAL_PIXEL_COUNTS = {
    "0.5 MP (SD1.5 ~704x704)": 512 * 512,
    "0.75 MP (~864x864)": 768 * 768,
    "1.0 MP (SDXL ~1024x1024)": 1024 * 1024,
    "1.5 MP (~1224x1224)": 1224 * 1224,
    "2.0 MP (~1408x1408)": 1408 * 1408,
}


class AspectRatioToResolution:
    """
    Aspect Ratio to Resolution

    Has a dropdown of standard ratios (1:1, 16:9, 9:16, 4:3, 3:2, 21:9)
    and a target total pixel count (e.g., 1024x1024 = 1 Megapixel).
    Outputs exact Width and Height integers that match SDXL/SD1.5 optimal pixel counts.
    """

    CATEGORY = "AchylsUtils/Resolution"

    RETURN_TYPES = ("INT", "INT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("width", "height", "aspect_w", "aspect_h")
    OUTPUT_TOOLTIPS = (
        "Calculated width in pixels (multiple of 8).",
        "Calculated height in pixels (multiple of 8).",
        "Width ratio component (e.g., 16 for 16:9).",
        "Height ratio component (e.g., 9 for 16:9).",
    )
    FUNCTION = "calculate"
    DESCRIPTION = (
        "Select an aspect ratio and target megapixel count. "
        "Outputs exact width and height (rounded to nearest multiple of 8) "
        "that best match the ratio at the target resolution."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "aspect_ratio": (list(ASPECT_RATIOS.keys()), {
                    "default": "1:1 (Square)",
                    "tooltip": "The desired aspect ratio.",
                }),
                "target_pixels": (list(OPTIMAL_PIXEL_COUNTS.keys()), {
                    "default": "1.0 MP (SDXL ~1024x1024)",
                    "tooltip": "Target total pixel count (megapixel equivalent).",
                }),
            },
        }

    @classmethod
    def IS_CHANGED(cls, aspect_ratio, target_pixels):
        return float(ASPECT_RATIOS[aspect_ratio][0]) + float(ASPECT_RATIOS[aspect_ratio][1]) + float(OPTIMAL_PIXEL_COUNTS[target_pixels])

    def calculate(self, aspect_ratio, target_pixels):
        w_ratio, h_ratio = ASPECT_RATIOS[aspect_ratio]
        total_pixels = OPTIMAL_PIXEL_COUNTS[target_pixels]

        # Calculate dimensions to match aspect ratio and total pixels
        # w * h = total_pixels, w/h = w_ratio/h_ratio
        # w = sqrt(total_pixels * w_ratio / h_ratio)
        # h = sqrt(total_pixels * h_ratio / w_ratio)
        width = math.sqrt(total_pixels * w_ratio / h_ratio)
        height = math.sqrt(total_pixels * h_ratio / w_ratio)

        # Round to nearest multiple of 8
        width = round(width / 8) * 8
        height = round(height / 8) * 8

        # Ensure minimum dimensions
        width = max(64, width)
        height = max(64, height)

        return (width, height, float(w_ratio), float(h_ratio))
