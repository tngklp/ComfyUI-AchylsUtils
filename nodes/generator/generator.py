import math
import torch
import comfy.sd
import comfy.utils
import comfy.samplers
import comfy.model_management
from nodes import common_ksampler


class AchylsGenerator:
    """
    Achyls Generator

    A single-node powerhouse that consolidates positive/negative prompting, CLIP layer control,
    dimension presets + custom sizes, batch size, KSampler, dual-KSampler upscaler,
    and VAE decode into one node.
    """

    CATEGORY = "AchylsUtils/Generator"

    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "LATENT", "IMAGE", "STRING")
    RETURN_NAMES = ("model", "clip", "vae", "latent", "image", "metadata")
    OUTPUT_TOOLTIPS = (
        "The diffusion model (passed through).",
        "The CLIP model (with clip layer set).",
        "The VAE model (passed through).",
        "The final latent before VAE decode.",
        "The decoded image output.",
        "Full metadata showing all params used for this generation.",
    )
    FUNCTION = "generate"
    DESCRIPTION = (
        "Achyls Generator: Encodes prompts, sets CLIP layer, "
        "selects dimensions (presets or custom), sets batch size, runs KSampler, optionally "
        "upscales via a second KSampler pass, and VAE decodes to image."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Model inputs
                "model": ("MODEL", {"tooltip": "The diffusion model from a checkpoint loader."}),
                "clip": ("CLIP", {"tooltip": "The CLIP model from a checkpoint loader."}),
                "vae": ("VAE", {"tooltip": "The VAE model from a checkpoint loader."}),

                # Prompts
                "positive": ("STRING", {
                    "multiline": True,
                    "dynamicPrompts": True,
                    "default": "",
                    "tooltip": "The positive prompt describing what to generate.",
                }),
                "negative": ("STRING", {
                    "multiline": True,
                    "dynamicPrompts": True,
                    "default": "",
                    "tooltip": "The negative prompt describing what to avoid.",
                }),

                # CLIP settings
                "enable_clip_layer": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Enable CLIP layer stopping. Disabled = use all CLIP layers (default ComfyUI behavior).",
                }),
                "stop_at_clip_layer": ("INT", {
                    "default": -1,
                    "min": -24,
                    "max": -1,
                    "step": 1,
                    "display": "slider",
                }),

                # Dimensions
                "width": ("INT", {
                    "default": 1024,
                    "min": 64,
                    "max": 16384,
                    "step": 8,
                    "tooltip": "Image width in pixels. Overridden if a latent is connected.",
                }),
                "height": ("INT", {
                    "default": 1024,
                    "min": 64,
                    "max": 16384,
                    "step": 8,
                    "tooltip": "Image height in pixels. Overridden if a latent is connected.",
                }),
                "batch_size": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 64,
                    "tooltip": "Number of images to generate in a batch. Overridden if a latent is connected.",
                }),

                # KSampler settings
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff,
                    "control_after_generate": True,
                    "tooltip": "Random seed for noise generation.",
                }),
                "steps": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 10000,
                    "tooltip": "Number of sampling steps.",
                }),
                "cfg": ("FLOAT", {
                    "default": 8.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.1,
                    "round": 0.01,
                    "tooltip": "Classifier-Free Guidance scale.",
                }),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS, {
                    "tooltip": "Sampling algorithm.",
                }),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS, {
                    "tooltip": "Noise scheduler.",
                }),
                "denoise": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Amount of denoising (1.0 = full denoise).",
                }),

                # Upscaler settings
                "enable_upscale": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Enable second KSampler pass with upscaled latent.",
                }),
                "upscale_multiplier": ([
                    "1",
                    "1.25",
                    "1.5",
                    "1.75",
                    "2",
                ], {
                    "default": "1.5",
                    "tooltip": "Upscale multiplier for the second KSampler pass.",
                }),
                "upscale_denoise": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Denoise value for the second KSampler upscale pass.",
                }),
            },
            "optional": {
                "latent": ("LATENT", {
                    "tooltip": "Optional input latent. If connected, overrides width, height, and batch_size with the latent's dimensions.",
                }),
            },
        }

    def generate(
        self,
        model,
        clip,
        vae,
        positive="",
        negative="",
        enable_clip_layer=False,
        stop_at_clip_layer=-1,
        width=1024,
        height=1024,
        batch_size=1,
        seed=0,
        steps=20,
        cfg=8.0,
        sampler_name="euler",
        scheduler="normal",
        denoise=1.0,
        enable_upscale=False,
        upscale_multiplier="1.5",
        upscale_denoise=0.5,
        latent=None,
    ):
        # ---- 1. Set CLIP layer ----
        if enable_clip_layer:
            clip = clip.clone()
            clip.clip_layer(stop_at_clip_layer)

        # ---- 2. Encode prompts ----
        pos_tokens = clip.tokenize(positive)
        pos_cond = clip.encode_from_tokens_scheduled(pos_tokens)

        neg_tokens = clip.tokenize(negative)
        neg_cond = clip.encode_from_tokens_scheduled(neg_tokens)

        # ---- 3. Set dimensions (from inputs or latent override) ----
        latent_connected = latent is not None
        if latent_connected:
            samples = latent["samples"]
            batch_size = samples.shape[0]
            latent_h = samples.shape[2]
            latent_w = samples.shape[3]
            used_width = latent_w * 8
            used_height = latent_h * 8
            latent_dict = latent
        else:
            used_width = width
            used_height = height
            # ---- 4. Create empty latent ----
            # Latent is 1/8th the size of the target image
            latent_tensor = torch.zeros(
                [batch_size, 4, used_height // 8, used_width // 8],
                device=comfy.model_management.intermediate_device(),
                dtype=comfy.model_management.intermediate_dtype(),
            )
            latent_dict = {"samples": latent_tensor}

        # ---- 5. Upscaler setup ----
        multiplier = float(upscale_multiplier) if enable_upscale else 1.0
        # Only split steps when there's actual upscaling (multiplier > 1.0)
        if enable_upscale and multiplier > 1.0:
            first_steps = max(1, math.ceil(steps * 0.6))
            second_steps = max(1, steps - first_steps)
            first_denoise = denoise
            second_denoise = upscale_denoise
        else:
            first_steps = steps
            second_steps = 0
            first_denoise = denoise
            second_denoise = 0.0

        # ---- 6. First KSampler ----
        (first_latent,) = common_ksampler(
            model,
            seed,
            first_steps,
            cfg,
            sampler_name,
            scheduler,
            pos_cond,
            neg_cond,
            latent_dict,
            denoise=first_denoise,
        )

        # ---- 7. Second KSampler (upscaler pass) ----
        if multiplier > 1.0:
            samples = first_latent["samples"]
            # Calculate target pixel dimensions, then convert to latent dimensions
            new_pixel_w = max(64, round(used_width * multiplier))
            new_pixel_h = max(64, round(used_height * multiplier))
            new_latent_w = new_pixel_w // 8
            new_latent_h = new_pixel_h // 8

            upscaled_samples = comfy.utils.common_upscale(
                samples, new_latent_w, new_latent_h, "nearest-exact", "disabled"
            )
            # Preserve all metadata from the source latent
            upscaled_latent = first_latent.copy()
            upscaled_latent["samples"] = upscaled_samples

            seed_2 = seed + 1

            (final_latent,) = common_ksampler(
                model,
                seed_2,
                second_steps,
                cfg,
                sampler_name,
                scheduler,
                pos_cond,
                neg_cond,
                upscaled_latent,
                denoise=second_denoise,
            )
        else:
            final_latent = first_latent

        # ---- 8. VAE Decode ----
        decoded_latent = final_latent["samples"]
        images = vae.decode(decoded_latent)
        if len(images.shape) == 5:
            images = images.reshape(-1, images.shape[-3], images.shape[-2], images.shape[-1])

        # ---- 9. Build metadata ----
        latent_shape = list(latent_dict["samples"].shape)
        total_steps = (f"{first_steps + second_steps} ({first_steps} first + {second_steps} second)"
                       if multiplier > 1.0 else str(steps))
        metadata_parts = [
            "=== Achyls Generator Metadata ===",
            f"Positive: {positive}",
            f"Negative: {negative}",
            f"CLIP layer stop: {'enabled (stop_at=' + str(stop_at_clip_layer) + ')' if enable_clip_layer else 'disabled'}",
            f"Width: {used_width} px",
            f"Height: {used_height} px",
            f"Latent shape: {latent_shape}",
            f"Batch size: {batch_size}",
            f"Seed: {seed}",
            f"Steps: {total_steps}",
            f"CFG: {cfg}",
            f"Sampler: {sampler_name}",
            f"Scheduler: {scheduler}",
            f"Denoise: {denoise}",
            f"Upscale enabled: {enable_upscale}",
            f"Upscale multiplier: {upscale_multiplier}",
            f"Upscale denoise: {upscale_denoise}",
            f"Latent input connected: {latent_connected}",
        ]
        if multiplier > 1.0:
            metadata_parts.append(f"Upscaled resolution: {used_width}x{used_height} -> {new_pixel_w}x{new_pixel_h}")
            metadata_parts.append(f"Upscaled latent: {new_latent_w}x{new_latent_h}")
            metadata_parts.append(f"Second pass seed: {seed_2}, steps: {second_steps}, denoise: {second_denoise}")
        metadata_parts.append(f"Output image shape: {list(images.shape)}")
        metadata = "\n".join(metadata_parts)

        print(f"[AchylsUtils Generator]\n{metadata}\n")

        return (model, clip, vae, final_latent, images, metadata)
