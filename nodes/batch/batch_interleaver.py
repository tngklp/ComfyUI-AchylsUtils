import torch


class BatchInterleaver:
    """
    Batch Interleaver

    Takes two image batches (Batch A and Batch B) and interleaves them
    (A1, B1, A2, B2). Useful for comparing base generations vs.
    upscaled generations side-by-side in a single batch.
    """

    CATEGORY = "AchylsUtils/Batch"

    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("interleaved", "total_count")
    OUTPUT_TOOLTIPS = (
        "The interleaved image batch (A1, B1, A2, B2, ...).",
        "The total number of images in the interleaved batch.",
    )
    FUNCTION = "interleave"
    DESCRIPTION = (
        "Interleaves two image batches: A1, B1, A2, B2, etc. "
        "The output batch size is min(len(A), len(B)) * 2."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "batch_a": ("IMAGE", {
                    "tooltip": "First batch of images.",
                }),
                "batch_b": ("IMAGE", {
                    "tooltip": "Second batch of images.",
                }),
            },
        }

    def interleave(self, batch_a, batch_b):
        len_a = batch_a.shape[0]
        len_b = batch_b.shape[0]
        n = min(len_a, len_b)

        # Interleave: A1, B1, A2, B2, ...
        interleaved = []
        for i in range(n):
            interleaved.append(batch_a[i].unsqueeze(0))
            interleaved.append(batch_b[i].unsqueeze(0))

        result = torch.cat(interleaved, dim=0)
        return (result, result.shape[0])
