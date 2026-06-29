import random
import re


class Randomizer:
    """
    Randomizer

    Takes a textbox with one entry per line and outputs a randomly selected line each run.
    Lines can be prefixed with n* to modify selection weights (e.g. 3* triples the chance,
    0.5* halves it).
    """

    CATEGORY = "AchylsUtils/Text"

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("value",)
    OUTPUT_TOOLTIPS = (
        "A randomly selected line from the textbox.",
    )
    FUNCTION = "pick"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "entries": ("STRING", {
                    "multiline": True,
                    "default": "option 1\noption 2\noption 3",
                    "tooltip": "One entry per line. Prefix with n* to adjust weight (e.g. 3* triples the chance, 0.5* halves it).",
                }),
            },
        }

    def pick(self, entries):
        lines = entries.strip().split("\n")
        # Parse lines into (text, weight) pairs
        weighted = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            m = re.match(r"^([\d.]+)\*(.*)", line)
            if m:
                weight = float(m.group(1))
                text = m.group(2).strip()
                if not text:
                    continue
                weighted.append((text, max(weight, 0.0)))
            else:
                weighted.append((line, 1.0))

        if not weighted:
            return ("",)

        texts, weights = zip(*weighted)
        chosen = random.choices(texts, weights=weights, k=1)[0]
        return (chosen,)
