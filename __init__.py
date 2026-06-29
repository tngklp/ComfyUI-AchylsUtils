# Import node classes
from .nodes.generator.generator import AchylsGenerator

from .nodes.image.save_image_no_metadata import SaveImageNoMetadata
from .nodes.image.smart_crop_and_pad import SmartCropAndPad
from .nodes.image.image_grid_composer import ImageGridComposer
from .nodes.latent.latent_presets import LatentImagePresets
from .nodes.latent.latent_noise_injector import LatentNoiseInjector
from .nodes.latent.empty_latent_from_image import EmptyLatentFromImage
from .nodes.text.randomizer import Randomizer
from .nodes.text.dynamic_prompt_builder import DynamicPromptBuilder
from .nodes.text.weight_scheduler import WeightScheduler
from .nodes.text.lora_tag_extractor import LoRATagExtractor
from .nodes.text.regex_string_replacer import RegexStringReplacer
from .nodes.batch.batch_interleaver import BatchInterleaver
from .nodes.batch.batch_slicer import BatchSlicer
from .nodes.logic.multi_switch_any import MultiSwitchAny
from .nodes.logic.seed_generator_display import SeedGeneratorDisplay
from .nodes.logic.seed_incrementer import SeedIncrementer
from .nodes.resolution.aspect_ratio_to_resolution import AspectRatioToResolution

# Node class mappings
NODE_CLASS_MAPPINGS = {
    "AchylsUtilsGenerator": AchylsGenerator,
    "SaveImageNoMetadata": SaveImageNoMetadata,
    "SmartCropAndPad": SmartCropAndPad,
    "ImageGridComposer": ImageGridComposer,
    "LatentImagePresets": LatentImagePresets,
    "LatentNoiseInjector": LatentNoiseInjector,
    "EmptyLatentFromImage": EmptyLatentFromImage,
    "Randomizer": Randomizer,
    "DynamicPromptBuilder": DynamicPromptBuilder,
    "WeightScheduler": WeightScheduler,
    "LoRATagExtractor": LoRATagExtractor,
    "RegexStringReplacer": RegexStringReplacer,
    "BatchInterleaver": BatchInterleaver,
    "BatchSlicer": BatchSlicer,
    "MultiSwitchAny": MultiSwitchAny,
    "SeedGeneratorDisplay": SeedGeneratorDisplay,
    "SeedIncrementer": SeedIncrementer,
    "AspectRatioToResolution": AspectRatioToResolution,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AchylsUtilsGenerator": "Achyls Generator",
    "SaveImageNoMetadata": "Save Image (No Metadata)",
    "SmartCropAndPad": "Smart Crop & Pad",
    "ImageGridComposer": "Image Grid Composer",
    "LatentImagePresets": "Latent Image Presets",
    "LatentNoiseInjector": "Latent Noise Injector",
    "EmptyLatentFromImage": "Empty Latent from Image",
    "Randomizer": "Randomizer",
    "DynamicPromptBuilder": "Dynamic Prompt Builder",
    "WeightScheduler": "Weight Scheduler (Prompt)",
    "LoRATagExtractor": "LoRA Tag Extractor",
    "RegexStringReplacer": "Regex String Replacer",
    "BatchInterleaver": "Batch Interleaver",
    "BatchSlicer": "Batch Slicer/Splitter",
    "MultiSwitchAny": "Multi-Switch (Any Type)",
    "SeedGeneratorDisplay": "Seed Generator & Display",
    "SeedIncrementer": "Seed Incrementer",
    "AspectRatioToResolution": "Aspect Ratio to Resolution",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
