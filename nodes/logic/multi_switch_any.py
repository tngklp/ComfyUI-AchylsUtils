class MultiSwitchAny:
    """
    Multi-Switch (Any Type)

    A universal switch that takes 4 inputs of ANY type, a select integer,
    and passes through only the selected input. Drastically reduces wire clutter.
    """

    CATEGORY = "AchylsUtils/Logic"

    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("output",)
    OUTPUT_TOOLTIPS = ("The selected input, passed through unchanged.",)
    FUNCTION = "route"
    DESCRIPTION = (
        "Universal switch: accepts 4 inputs of any type and a select integer. "
        "Passes through only the selected input. Reduces wire clutter for dynamic routing."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "select": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 3,
                    "step": 1,
                    "tooltip": "Which input to pass through (0, 1, 2, or 3).",
                }),
            },
            "optional": {
                "input_0": ("*", {"tooltip": "Input 0 (selected when select=0)."}),
                "input_1": ("*", {"tooltip": "Input 1 (selected when select=1)."}),
                "input_2": ("*", {"tooltip": "Input 2 (selected when select=2)."}),
                "input_3": ("*", {"tooltip": "Input 3 (selected when select=3)."}),
            },
        }

    def route(self, select=0, input_0=None, input_1=None, input_2=None, input_3=None):
        inputs = [input_0, input_1, input_2, input_3]
        idx = max(0, min(select, 3))
        return (inputs[idx],)
