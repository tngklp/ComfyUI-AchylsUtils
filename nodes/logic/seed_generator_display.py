class SeedGeneratorDisplay:
    """
    Seed Generator & Display

    Generates a random seed, outputs it as an INT for the KSampler,
    but ALSO outputs it as a STRING. This allows routing the seed
    directly into a "Save Image" node's filename prefix.
    """

    CATEGORY = "AchylsUtils/Logic"

    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("seed_int", "seed_str")
    OUTPUT_TOOLTIPS = (
        "The generated seed as an integer, for KSampler use.",
        "The generated seed as a string, for filename prefixes.",
    )
    FUNCTION = "generate"
    DESCRIPTION = (
        "Generates a random seed and outputs it both as INT (for KSampler) "
        "and STRING (for filename prefixes like 'output_{seed}')."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff,
                    "control_after_generate": True,
                    "tooltip": "The seed value. Enable 'control_after_generate' to auto-randomize.",
                }),
            },
        }

    def generate(self, seed=0):
        return (seed, str(seed))
