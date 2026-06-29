import re


class RegexStringReplacer:
    """
    Regex String Replacer

    Takes an input string, a Regex pattern, and a replacement string.
    Extremely useful for parsing filenames, modifying bulk prompts,
    or cleaning up metadata.
    """

    CATEGORY = "AchylsUtils/Text"

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("output", "replacements")
    OUTPUT_TOOLTIPS = (
        "The string after applying the regex replacement.",
        "The number of replacements made.",
    )
    FUNCTION = "replace"
    DESCRIPTION = (
        "Applies a regex pattern and replacement to an input string. "
        "Supports all standard Python regex syntax including capture groups "
        "(use \\1, \\2, etc. in the replacement)."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "The input string to process.",
                }),
                "pattern": ("STRING", {
                    "default": "",
                    "tooltip": "The regex pattern to search for. Uses Python re syntax.",
                }),
                "replacement": ("STRING", {
                    "default": "",
                    "tooltip": "The replacement string. Use \\1, \\2 for capture groups.",
                }),
            },
        }

    def replace(self, text, pattern, replacement):
        if not pattern:
            return (text, 0)
        try:
            result, count = re.subn(pattern, replacement, text)
            return (result, count)
        except re.error as e:
            return (f"[Regex Error: {e}]", 0)
