## Why

Real testing (26-image batch, direct human inspection of every miss) showed general-purpose Ollama vision models have a real accuracy ceiling: `llava` missed 11/26 obvious animals outright at default settings, and even after fixing a genuine context-window bug (`num_ctx` truncation — see `species-tagging-cli-v1`), the best Ollama model (`qwen2.5vl`) still tops out around 25/26 on an easy 26-image set. The user wants to validate whether a purpose-built detect-then-classify pipeline (MegaDetector + SpeciesNet — the standard tool ecologists actually use, per prior-art research already done for v1) does meaningfully better once real GPU hardware (an Ubuntu 3060 box) is available to test it at volume (hundreds of images).

## What Changes

- New alternate backend: MegaDetector (object detection: Animal/Human/Vehicle/Empty + bounding box) feeding SpeciesNet (species classification on the cropped detection, ~2,000+ species).
- Kept as a **separate, standalone entry point** from the existing Ollama-based `species_tag` package — different runtime (PyTorch, not an HTTP call to Ollama), different setup burden (GPU/CUDA, downloaded model weights), different failure modes. Per the user's explicit direction: two implementations, not one config flag forcing both into the same runtime footprint.
- Reuses, unchanged, the parts of v1 that aren't backend-specific: recursive folder scan + RAW preview extraction (`discovery.py`, `exif.py`'s `extract_preview`), the confidence-bucket keyword-writing behavior (`tagging.py`, `exif.py`'s `write_keywords`), and the flat-keyword EXIF/XMP convention.
- **Spec only in this change — not implemented.** Actual build is deferred until the Ubuntu 3060 box is available for real testing at volume; building it blind on a MacBook would mean re-doing GPU/CUDA-specific validation anyway once the real target hardware exists.

## Capabilities

### New Capabilities
- `blank-frame-filtering`: runs MegaDetector on an image, classifies it Animal/Human/Vehicle/Empty, and returns cropped bounding-box regions for Animal detections — the "is there something here at all" stage, done once, cheaply, before any species classification runs.
- `species-classification-local`: runs SpeciesNet on a cropped animal region (from `blank-frame-filtering`) and returns a species name + confidence from its fixed taxonomy — the "what is it" stage.

### Modified Capabilities
(none — `image-discovery`, `metadata-tagging`, and `cli-reporting` from `species-tagging-cli-v1` are reused as-is; this backend produces the same `SpeciesResult` shape those capabilities already consume)

## Impact

- New, heavier runtime dependency tree: PyTorch, MegaDetector's package (or its YOLO-based successor), a SpeciesNet package/weights — multi-GB downloads, GPU strongly recommended.
- Targets the Ubuntu 3060 box specifically (per the user) — not validated on this Mac; CUDA/driver setup is out of scope for this spec and belongs to whoever sets up that machine.
- No change to the existing Ollama-based `species_tag` tool — it keeps working exactly as it does today, unaffected by this addition.
