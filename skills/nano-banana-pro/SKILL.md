---
name: nano-banana-pro
description: "Generate/edit images with Nano Banana Pro (Gemini 3 Pro Image). Use for image create/modify requests incl. edits. Supports text-to-image + image-to-image; 1K/2K/4K; use --input-image."
description_zh: "AI 图片生成与编辑（支持 4K）"
description_en: "AI image generation & editing (up to 4K)"
version: 1.0.1
display_name: "nano-banana-pro"
display_name_en: "nano-banana-pro"
visibility: "public"
---

# Nano Banana Pro Image Generation & Editing

Generate new images or edit existing ones using Google's Nano Banana Pro API (Gemini 3 Pro Image).

## Usage

Run the script using absolute path (do NOT cd to skill directory first):

**Generate new image:**
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "your image description" --filename "output-name.png" [--resolution 1K|2K|4K] [--api-key KEY]
```

**Edit existing image:**
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "editing instructions" --filename "output-name.png" --input-image "path/to/input.png" [--resolution 1K|2K|4K] [--api-key KEY]
```

**Important:** Always run from the user's current working directory so images are saved where the user is working.

## Default Workflow (draft > iterate > final)

- Draft (1K): quick feedback loop
- Iterate: adjust prompt in small diffs; keep filename new per run
- Final (4K): only when prompt is locked

## Resolution Options

- **1K** (default) - ~1024px resolution
- **2K** - ~2048px resolution
- **4K** - ~4096px resolution

## API Key

1. `--api-key` argument
2. `GEMINI_API_KEY` environment variable

## Image Editing

Use `--input-image` parameter with the path to the image. The prompt should contain editing instructions.

## Prompt Handling

**For generation:** Pass user's image description as-is to `--prompt`.
**For editing:** Pass editing instructions in `--prompt`.

## Character and avatar consistency

When generating the same character or a family of avatars across runs, keep a
short visual anchor beside the prompt:

- subject and silhouette;
- expression and pose;
- framing and camera angle;
- lighting and palette;
- material and rendering style;
- background treatment;
- one signature prop or identifying detail.

Change only the variables the user asked to vary; repeat every other anchor
verbatim. Use a new filename for each variant so comparisons stay possible.
Start at 1K, iterate on the prompt, and reserve 4K for the locked direction.

Use an original character or a clearly authorized reference. Do not invent a
real person's likeness or imply that a real person endorses the result. Avoid
reproducing a protected character design merely because it is recognizable.

## Output

- Saves PNG to current directory
- Script outputs the full path to the generated image
- **Do not read the image back** - just inform the user of the saved path
