import re


class DynamicPromptBuilder:
    """
    Dynamic Prompt Builder (Template Node)

    Takes multiple string inputs (Subject, Medium, Style, Lighting, etc.)
    and a template text box where you write {Subject}, {Medium}, etc.
    Outputs a single concatenated string with placeholders replaced.
    """

    CATEGORY = "AchylsUtils/Text"

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    OUTPUT_TOOLTIPS = ("The assembled prompt string with all placeholders replaced.",)
    FUNCTION = "build"
    DESCRIPTION = (
        "Insert any number of placeholder inputs and write a template using {placeholder_name}. "
        "Each placeholder will be replaced with its corresponding input value. "
        "Great for swapping out prompt parts without chaining multiple Text Concatenate nodes."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "template": ("STRING", {
                    "multiline": True,
                    "default": "{Subject}, {Medium}, {Style}, {Lighting}",
                    "tooltip": "Template text. Use {PlaceholderName} to reference dynamic inputs.",
                }),
            },
            "optional": {
                "Subject": ("STRING", {"default": "", "tooltip": "Value to replace {Subject} in the template."}),
                "Medium": ("STRING", {"default": "", "tooltip": "Value to replace {Medium} in the template."}),
                "Style": ("STRING", {"default": "", "tooltip": "Value to replace {Style} in the template."}),
                "Lighting": ("STRING", {"default": "", "tooltip": "Value to replace {Lighting} in the template."}),
                "extra_1": ("STRING", {"default": "", "tooltip": "Extra placeholder. Use {extra_1} in the template."}),
                "extra_2": ("STRING", {"default": "", "tooltip": "Extra placeholder. Use {extra_2} in the template."}),
                "extra_3": ("STRING", {"default": "", "tooltip": "Extra placeholder. Use {extra_3} in the template."}),
                "extra_4": ("STRING", {"default": "", "tooltip": "Extra placeholder. Use {extra_4} in the template."}),
                "extra_5": ("STRING", {"default": "", "tooltip": "Extra placeholder. Use {extra_5} in the template."}),
            },
        }

    def build(self, template, **kwargs):
        result = template
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            if value and placeholder in result:
                result = result.replace(placeholder, value)
        # Clean up any remaining unfilled placeholders
        result = re.sub(r"\{[^}]+\}", "", result)
        # Clean up extra whitespace
        result = re.sub(r"\s+", " ", result).strip()
        return (result,)
