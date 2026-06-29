import re


class LoRATagExtractor:
    """
    LoRA Tag Extractor

    Pastes a block of text containing <lora:name:weight> tags.
    Extracts the lora tags, cleans the main prompt text, and outputs the
    clean text on one string, and the formatted LoRA tags on another.
    """

    CATEGORY = "AchylsUtils/Text"

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("clean_text", "lora_tags")
    OUTPUT_TOOLTIPS = (
        "The original text with all <lora:...> tags removed.",
        "Formatted LoRA tag string, e.g. '<lora:name1:0.8> <lora:name2:1.0>'",
    )
    FUNCTION = "extract"
    DESCRIPTION = (
        "Extracts <lora:name:weight> tags from a block of text. "
        "Outputs the cleaned text (tags removed) and the extracted LoRA tags formatted."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Input text containing <lora:name:weight> tags.",
                }),
            },
        }

    def extract(self, text):
        # Find all <lora:...> tags
        lora_pattern = re.compile(r"<lora:([^:>]+):([^>]+)>", re.IGNORECASE)
        matches = lora_pattern.findall(text)

        # Build formatted LoRA tags string
        lora_tags = " ".join(f"<lora:{name}:{weight}>" for name, weight in matches)

        # Remove all <lora:...> tags from the text
        clean_text = lora_pattern.sub("", text)
        # Clean up extra whitespace
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        return (clean_text, lora_tags)
