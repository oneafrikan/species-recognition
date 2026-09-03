## Routing

Same convention as the other changes in this repo: no specialist pre-assigned.
The Tech Lead decides routing when this actually starts building —
`grid-backend-dev` for the settled `frame-blur-detection` work,
`grid-data-scientist` is worth considering for the `subject-focus-detection`
pilot specifically (task 3.1 below) given it's an evaluation/experiment
task, not straightforward implementation. `grid-ponytail` before calling
either half done. This change is **not build-ready today** — pick it up
whenever the user asks for it.

## 1. Frame-level blur detection (settled — build this first)

- [ ] 1.1 Add `opencv-python` to `requirements.txt`
- [ ] 1.2 Sharpness-scoring function (`cv2.Laplacian(...).var()`) — pure function, image bytes in, score out
- [ ] 1.3 Config: `blur_threshold` (or similar) added to `config.yaml` schema, validated like other numeric config fields
- [ ] 1.4 Wire into the existing pipeline: score every image, write `blurry` keyword when below threshold, alongside whatever species keywords already got written
- [ ] 1.5 Unit tests: known-sharp vs. known-blurred test images score as expected on either side of a threshold

## 2. Calibration

- [ ] 2.1 Score a real sample of the user's own sharp and soft photos, pick a sensible default threshold (per design.md — no universal constant works)
- [ ] 2.2 Document the calibration process in README, since a different camera/subject mix may need a different threshold

## 3. Subject-focus-detection pilot (do NOT build the full feature before this)

- [ ] 3.1 Pilot: run both candidate bounding-region sources (Ollama VLM grounding prompt, and `megadetector-speciesnet-backend`'s MegaDetector stage if that change is available) against ~20 real images with animals in them. Judge reliability by eye — does the returned box actually contain the animal/eye.
- [ ] 3.2 Decision point: pick a candidate, or conclude neither is reliable enough and stop here (a legitimate outcome — see design.md)
- [ ] 3.3 If proceeding: implement the localized-vs-background sharpness comparison, write the front/back-focus flag as a keyword
- [ ] 3.4 If proceeding: unit tests for the comparison logic against known focus/misfocus crops
