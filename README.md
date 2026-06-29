# ComfyUI AchylsUtils

A collection of utility nodes for ComfyUI that streamline common generation workflows.

---

## Installation

1. Clone this repository into your `ComfyUI/custom_nodes/` directory:
   ```bash
   cd ComfyUI/custom_nodes/
   git clone https://github.com/tngklp/ComfyUI-AchylsUtils.git
   ```
2. Restart ComfyUI (or reload custom nodes).

---

## Nodes

- [Generator](#generator)
  - [Achyls Generator](#achyls-generator)
- [Image](#image)
  - [Save Image (No Metadata)](#save-image-no-metadata)
  - [Smart Crop & Pad](#smart-crop--pad)
  - [Image Grid Composer](#image-grid-composer)
- [Latent](#latent)
  - [Latent Image Presets](#latent-image-presets)
  - [Latent Noise Injector](#latent-noise-injector)
  - [Empty Latent from Image](#empty-latent-from-image)
- [Text](#text)
  - [Randomizer](#randomizer)
  - [Dynamic Prompt Builder](#dynamic-prompt-builder)
  - [Weight Scheduler (Prompt)](#weight-scheduler-prompt)
  - [LoRA Tag Extractor](#lora-tag-extractor)
  - [Regex String Replacer](#regex-string-replacer)
- [Batch](#batch)
  - [Batch Interleaver](#batch-interleaver)
  - [Batch Slicer/Splitter](#batch-slicersplitter)
- [Logic](#logic)
  - [Multi-Switch (Any Type)](#multi-switch-any-type)
  - [Seed Generator & Display](#seed-generator--display)
  - [Seed Incrementer](#seed-incrementer)
- [Resolution](#resolution)
  - [Aspect Ratio to Resolution](#aspect-ratio-to-resolution)

---

## Generator

### Achyls Generator

An all-in-one generation node that consolidates prompting, CLIP layer control, dimension settings, batch size, KSampler, dual-KSampler upscaling, and VAE decoding into a single node.

**Inputs:** `MODEL`, `CLIP`, `VAE`, `LATENT (optional)`

**Outputs:** `MODEL`, `CLIP`, `VAE`, `LATENT`, `IMAGE`, `STRING (metadata)`

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `positive` | STRING | The positive prompt describing what to generate |
| `negative` | STRING | The negative prompt describing what to avoid |
| `enable_clip_layer` | BOOLEAN | Enable CLIP layer stopping |
| `stop_at_clip_layer` | INT | CLIP layer to stop at (-24 to -1) |
| `width` | INT | Image width in pixels (overridden if `latent` is connected) |
| `height` | INT | Image height in pixels (overridden if `latent` is connected) |
| `batch_size` | INT | Number of images per batch (overridden if `latent` is connected) |
| `seed` | INT | Random seed for noise generation |
| `steps` | INT | Number of sampling steps |
| `cfg` | FLOAT | Classifier-Free Guidance scale |
| `sampler_name` | COMBO | Sampling algorithm (all KSampler samplers) |
| `scheduler` | COMBO | Noise scheduler (all KSampler schedulers) |
| `denoise` | FLOAT | Amount of denoising (1.0 = full denoise) |
| `enable_upscale` | BOOLEAN | Enable second KSampler pass with upscaled latent |
| `upscale_multiplier` | COMBO | Upscale multiplier (1×, 1.25×, 1.5×, 1.75×, 2×) |
| `upscale_denoise` | FLOAT | Denoise value for the second KSampler upscale pass (default: 0.5) |

When upscaling is enabled, the node runs two KSampler passes:
1. First pass at the original resolution with ~60% of the total steps
2. Latent is upscaled using pixel-based math, then a second pass runs at ~40% steps with the configured `upscale_denoise`

---

## Image

### Save Image (No Metadata)

Saves images as PNG files with all generation metadata stripped. Takes an image input and a filename prefix, but saves without embedding any prompt, workflow, or generation info.

The prefix for the file can include formatting information such as `%date:yyyy-MM-dd%` or `%Empty Latent Image.width%` to include values from nodes.

### Smart Crop & Pad

Takes an image of any size and a target resolution. In "crop" mode it scales to cover the target and center-crops any overflow. In "fit" mode it letterboxes the image inside the target dimensions and fills the remaining borders with edge-stretched pixels, solid black, or solid white.

### Image Grid Composer

Composes a batch of images into a clean grid layout with configurable column count and padding between cells.

---

## Latent

### Latent Image Presets

Select a preset resolution and batch size to generate an empty latent tensor. Resolution presets are loaded from `presets.json` — edit this file to add, remove, or customize presets.

**Customizing Presets**

Open `presets.json` in the extension root folder. The format is:

```json
{
    "My Preset": [1280, 720],
    "Another Preset": [1920, 1080]
}
```

Each key is a display name shown in the dropdown. Each value is `[width, height]` in pixels. Add, remove, or edit entries freely, they'll update on the next ComfyUI node refresh.

### Latent Noise Injector

Sits between a KSampler and the VAE Decode. Adds a configurable amount of Gaussian noise to the latent tensor, useful for adding gritty texture or breaking up overly smooth AI generations.

### Empty Latent from Image

Takes an image as input and outputs an empty latent tensor matching that image's exact dimensions. Saves having to route through separate "Get Image Size" and "Empty Latent" nodes.

---

## Text

### Randomizer

A multiline textbox where each line is an entry. Every time the node runs, it picks one at random.

**Weighted entries:** Prefix a line with `n*` to adjust its selection probability:
- `3*sunset` — 3× more likely to be picked
- `0.5*portrait` — half as likely to be picked
- `landscape` — normal probability (1×)

### Dynamic Prompt Builder

A template-based prompt assembly node. Write a template using `{PlaceholderName}` syntax and connect string inputs for each placeholder (Subject, Medium, Style, Lighting, plus five extra slots). The node replaces placeholders with their values and outputs the assembled prompt.

### Weight Scheduler (Prompt)

Dynamically adjusts the weight of a specific word or phrase over a range of sampling steps using linear interpolation. Provide the target word, start/end weights, and start/end steps; the node outputs the prompt with the appropriately weighted term.

### LoRA Tag Extractor

Paste a block of text containing `<lora:name:weight>` tags. The node extracts the LoRA tags, cleans them from the main text, and outputs the clean prompt on one output and the formatted LoRA tags on another (ready to route to a LoRA loader or text encoder).

### Regex String Replacer

Applies a Python regex pattern and replacement to an input string. Supports capture groups (`\1`, `\2`, etc.) and returns both the modified string and a count of how many replacements were made. Useful for parsing filenames, modifying bulk prompts, or cleaning up metadata.

---

## Batch

### Batch Interleaver

Takes two image batches (A and B) and interleaves them into a single batch (A1, B1, A2, B2, ...). Useful for comparing base generations vs. upscaled generations side-by-side.

### Batch Slicer/Splitter

Splits an image batch at a given index. Outputs three tensors: images before the index, the single image at the index, and images after the index.

---

## Logic

### Multi-Switch (Any Type)

A universal switch that accepts 4 inputs of any type and a select integer. Only the selected input passes through to the output, reducing wire clutter when setting up dynamic routing.

### Seed Generator & Display

Generates a seed and outputs it both as an integer (for KSampler nodes) and as a string (for embedding in saved image filenames via the filename prefix).

### Seed Incrementer

Takes a base seed and an iteration number and outputs `base_seed + iteration`. Useful for deterministic sequential seeds in batch generation workflows.

---

## Resolution

### Aspect Ratio to Resolution

Select a standard aspect ratio (1:1, 16:9, 9:16, 4:3, 3:2, 21:9, etc.) and a target total pixel count (0.5 MP through 2.0 MP). Outputs exact width and height integers rounded to the nearest multiple of 8 for optimal model compatibility.