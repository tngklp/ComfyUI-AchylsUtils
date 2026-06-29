import torch
import comfy.model_management


class LatentNoiseInjector:
    """
    Latent Noise Injector

    Sits between the KSampler and the VAE Decode. Takes the latent and adds
    a user-defined amount of Gaussian noise (scaled by a float input).
    Useful for adding gritty texture or breaking up overly smooth AI generations.
    """

    CATEGORY = "AchylsUtils/Latent"

    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent",)
    OUTPUT_TOOLTIPS = ("The latent with noise added.",)
    FUNCTION = "inject"
    DESCRIPTION = (
        "Adds Gaussian noise to a latent tensor. Sits between KSampler and VAE Decode. "
        "Noise scale controls intensity. Useful for adding texture or breaking up "
        "overly smooth AI generations."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "latent": ("LATENT", {
                    "tooltip": "The latent from a KSampler or similar node.",
                }),
                "noise_scale": ("FLOAT", {
                    "default": 0.1,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "Standard deviation of the Gaussian noise to add.",
                }),
                "noise_seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff,
                    "control_after_generate": True,
                    "tooltip": "Seed for reproducible noise.",
                }),
            },
        }

    def inject(self, latent, noise_scale=0.1, noise_seed=0):
        samples = latent["samples"]

        if noise_scale > 0:
            device = samples.device
            dtype = samples.dtype

            # Generate reproducible Gaussian noise
            generator = torch.Generator(device="cpu")
            generator.manual_seed(noise_seed)
            noise = torch.randn(samples.shape, dtype=dtype, generator=generator, device="cpu")
            noise = noise.to(device=device, dtype=dtype)

            # Scale and add
            samples = samples + noise * noise_scale

        result = latent.copy()
        result["samples"] = samples
        return (result,)
