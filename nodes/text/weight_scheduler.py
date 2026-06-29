import re


class WeightScheduler:
    """
    Weight Scheduler (Prompt)

    Takes a text prompt and dynamically adjusts the weight of a specific word or phrase
    over a set number of steps. E.g., (masterpiece:1.2) from steps 0-10,
    scaling down to (masterpiece:0.8) from steps 10-20.
    """

    CATEGORY = "AchylsUtils/Text"

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    OUTPUT_TOOLTIPS = ("The prompt with the scheduled weight applied.",)
    FUNCTION = "schedule"
    DESCRIPTION = (
        "Dynamically adjusts the weight of a word/phrase over sampling steps. "
        "Provide the target word, start/end weights, and start/end steps. "
        "Outputs the prompt with the weight applied for the current step."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "The base prompt containing the word to weight-schedule.",
                }),
                "target_word": ("STRING", {
                    "default": "masterpiece",
                    "tooltip": "The word or phrase to apply dynamic weighting to.",
                }),
                "start_weight": ("FLOAT", {
                    "default": 1.2,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.05,
                    "tooltip": "Starting weight at step_start.",
                }),
                "end_weight": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.05,
                    "tooltip": "Ending weight at step_end.",
                }),
                "step_start": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 10000,
                    "tooltip": "Step number where the scheduled weight begins.",
                }),
                "step_end": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 10000,
                    "tooltip": "Step number where the scheduled weight ends.",
                }),
                "current_step": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 10000,
                    "tooltip": "The current sampling step to compute the interpolated weight.",
                }),
            },
        }

    def schedule(self, prompt, target_word, start_weight, end_weight, step_start, step_end, current_step):
        if not prompt or not target_word:
            return (prompt,)

        # Clamp current_step to [step_start, step_end]
        effective_step = max(step_start, min(step_end, current_step))
        step_range = max(1, step_end - step_start)
        # Linear interpolation
        t = (effective_step - step_start) / step_range
        weight = start_weight + (end_weight - start_weight) * t
        weight = round(weight, 4)

        # Replace the target word with weighted version
        # Avoid double-wrapping if already weighted
        pattern = re.compile(
            r"\b" + re.escape(target_word) + r"\b"
            r"(?!\s*:\s*[\d.]+\s*\))",
            re.IGNORECASE,
        )
        replacement = f"({target_word}:{weight})"
        result = pattern.sub(replacement, prompt)

        return (result,)
