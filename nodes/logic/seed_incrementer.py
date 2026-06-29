class SeedIncrementer:
    """
    Seed Incrementer

    Takes a base seed and an iteration integer.
    Outputs base_seed + iteration.
    Great for "For-Loop" or batch generation workflows
    where you want deterministic but sequential seeds.
    """

    CATEGORY = "AchylsUtils/Logic"

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("seed",)
    OUTPUT_TOOLTIPS = ("The computed seed = base_seed + iteration.",)
    FUNCTION = "increment"
    DESCRIPTION = (
        "Computes base_seed + iteration. Useful for batch generation workflows "
        "where you want deterministic but sequential seeds."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff,
                    "tooltip": "The base seed to start from.",
                }),
                "iteration": ("INT", {
                    "default": 1,
                    "min": 0,
                    "max": 0xffffffff,
                    "tooltip": "The iteration number to add to the base seed.",
                }),
            },
        }

    def increment(self, base_seed=0, iteration=0):
        result = (base_seed + iteration) & 0xffffffffffffffff
        return (result,)
