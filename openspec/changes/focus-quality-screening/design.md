## Context

See `proposal.md` for motivation. This sits alongside `species-tagging-cli-v1`'s existing pipeline — it adds a keyword outcome, it doesn't touch species identification or the confidence-bucket logic. Research (not guesswork) already ruled out two tempting-but-wrong approaches: asking a VLM directly whether an image is in focus (benchmarks near-random for blur judgments — VLMs read semantic content, not pixel-level sharpness), and general no-reference image-quality models like BRISQUE/NIQE (heavy PyTorch dependency, restrictively licensed, no real advantage over Laplacian variance for this specific task).

## Goals / Non-Goals

**Goals:**
- `frame-blur-detection`: a settled, buildable-as-is capability using classical CV, no new heavy dependency.
- `subject-focus-detection`: a clearly-scoped experiment with an explicit pilot gate, not a premature architecture commitment.

**Non-Goals:**
- No ML-based image-quality model (BRISQUE/NIQE/pyiqa) — researched and rejected, see Context.
- No custom-trained eye-landmark model — no permissively-licensed lightweight option exists for animals (as distinct from human-face landmark models, which don't generalize).
- Not implemented in this change at all — build deferred, per the user.

## Decisions

### Frame-level: Laplacian variance

`cv2.Laplacian(gray, cv2.CV_64F).var()` — measures edge energy as a sharpness proxy. Well-understood, trivial to implement, the only new dependency is `opencv-python`. Known limitation, stated plainly: it's an outlier detector calibrated per-dataset, not an absolute measure — a sharp low-texture frame (sky, water) scores low, and a noisy-but-blurred frame can score deceptively high. The threshold is a config value the user calibrates against their own photos (score a few dozen known-sharp/known-soft shots, pick a cutoff), not a hardcoded universal constant.

### Subject-level: two candidates, pilot required before choosing

1. **Reuse the existing Ollama VLM with a grounding prompt** (ask it to return a bounding box for the animal/eye). Cheapest — no new dependency, the HTTP call infrastructure already exists in `species_tag/backends/ollama.py`. Risk: no evidence found in research that this is reliable for animal eyes specifically (as opposed to human faces or general objects, where grounding is better-studied). Must pilot on ~20 real images before trusting it.
2. **Reuse `megadetector-speciesnet-backend`'s MegaDetector stage** for the bounding region. More reliable for "where's the animal" (that's literally what it's built for), but only gives a whole-animal box, not an eye-specific one, and pulls in that change's heavy PyTorch dependency — only makes sense if `megadetector-speciesnet-backend` is already being used, not worth adopting standalone just for this.

Neither is adopted here. Both are named so the eventual build starts from "pilot these two and pick," not from zero.

### Where this slots into the existing pipeline

`frame-blur-detection` runs independently of species identification — every image gets a sharpness score regardless of what the species backend returns, and `blurry` is written as an additional keyword alongside whatever species-related keywords `metadata-tagging` already produced. `subject-focus-detection` only runs when a bounding region is available, so it's inherently conditional on which backend/config produced one.

## Risks / Trade-offs

- **No universal blur threshold.** Accepted — this is inherent to Laplacian variance, not a design flaw to engineer around. The spec requires it be configurable and calibrated, not that it magically generalize.
- **Subject-focus-detection may simply not pan out.** The pilot-first framing exists exactly because this might not be worth building at all if neither candidate proves reliable — that's a legitimate outcome, not a failure of this spec.

## Open Questions

- Exact blur-score threshold default — genuinely per-camera/per-dataset, resolve by calibrating against the user's own real photos when this is built, not now.
- Which subject-focus-detection candidate (VLM grounding vs. MegaDetector reuse) wins the pilot — resolved by the pilot itself, per the spec's "Pilot validation gates full build-out" requirement. Doesn't change the capability's contract either way.
