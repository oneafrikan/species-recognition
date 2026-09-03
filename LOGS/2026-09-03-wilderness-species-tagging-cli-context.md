---
date: 2026-09-03
machine: wilderness
type: context
session: species-recognition repo — spec, build, test, public release
---

# Session Context: 2026-09-03 — wilderness

## What Was Investigated

Built a Python CLI that batch-tags wildlife photos with species keywords using a local Ollama vision model, writing results into EXIF/XMP/IPTC metadata for Lightroom filtering. Went full-cycle in one session: requirements interview → OpenSpec proposal/design/tasks → implementation via a specialist agent → real-world manual testing against 26 actual wildlife photos → a real bug found and fixed through that testing → two follow-on features (MegaDetector/SpeciesNet backend, focus-quality screening) specced but deliberately not built → repo made public. The user's stated goal throughout: "get it right," not "ship fast and iterate blind" — hence the emphasis on real testing over assumed correctness at every stage.

## Every Decision and Reasoning

1. **Tool workflow chosen up front:** `/grill-me` to resolve requirements, then the OpenSpec approach via the `grid-tech-lead`/`grid-product-manager` skills to formally spec, then build. User was explicit: "do not over-engineer, do not overthink, do not over-spec."

2. **RAW handling = embedded-preview extraction, not full decode.** Reasoning: rawpy/libraw is a fragile cross-platform dependency (native builds vary by camera format), full RAW decode is much slower for no accuracy benefit on a species-ID task that doesn't need color-accurate pixels — exiftool can pull the embedded JPEG preview trivially on all three target OSes.

3. **Metadata convention: flat keywords (`"African Elephant"`, `"review_needed"`, `"no_detection"`) in XMP `dc:Subject` + IPTC `Keywords`, not hierarchical.** User picked flat over Lightroom's hierarchical-keyword feature for simplicity — filterable independently, no nested-tree setup needed.

4. **No CSV/log files — explicit user correction mid-interview.** First draft proposed a CSV "review_needed" list; user rejected it: "i don't want csv files - everything should be tagged in the exif data using tagging conventions." All state (including empty-frame results) lives in the image's own metadata plus console output.

5. **Always reprocess every image, no idempotency/skip-if-tagged logic.** User explicitly chose the simpler option over a skip-if-already-tagged design — deliberate simplicity trade, not an oversight. Consequence discovered later: since `exif.py`'s `write_keywords` uses exiftool's `+=` append syntax, re-running a different model on already-tagged images *appends* rather than replaces — had to restore from `_original` backups between each model in the multi-model comparison testing to get clean per-model results.

6. **Region is a free-text `region_context` config value templated into the prompt, no hardcoded species checklist.** User corrected an initial proposal to hardcode a Southern African species list: "this isn't only going to be African wildlife... I think it's better to say let's bake that into the prompt so that it narrows it down at the point the script is running."

7. **Cloud vision backend is an architected extension point (the `VisionBackend` ABC) but not implemented in v1.** Ollama only for v1 — local and remote (host is a config value, since the user's Ollama instance may run on a different machine than the one running the script, e.g. the eventual Ubuntu 3060 box vs. a Mac Mini running the actual Lightroom library).

8. **`icewall905/image-tagger` (a close architectural-match prior-art repo) was evaluated but not vendored.** Reasoning documented in `design.md`: 3-star project, no independent code-quality signal, the actual logic needed (HTTP call + prompt template + exiftool write) was small enough that vendoring added more indirection (submodule pin/update overhead, extra license to track) than it saved.

9. **Repo target: personal `oneafrikan` GitHub account, private initially.** Discovered via `gh auth status` + the machine's private `claude-private/machines/wilderness.md` file (which itself was missing/unfilled at session start — flagged to the user as a real gap, then found already fixed mid-session by an external process). SSH: `github-personal` alias (`~/.ssh/id_ed25519`), distinct from the machine's default `github-wilderness` alias.

10. **Build was explicitly deferred from spec, and specialist routing was explicitly NOT pre-decided in the spec.** User: "I don't think we need to assign that now. I think we need the tech lead to decide once we get into build stage." A `## Routing` section was added to `tasks.md` codifying this as a repo-wide convention (also applied to the two later changes).

11. **Real testing revealed `llava` (the first model tried) missed 11/26 obvious animals** (elephants, lions, buffalo, giraffes, a stork, hornbills, a snake — all directly eyeballed via the `Read` tool, not assumed from the tags alone). This was the trigger for the whole "which model, and why is it failing" investigation that dominated the middle of the session.

12. **Root cause found was NOT model weakness — it was Ollama's default `num_ctx` (2048 tokens) silently truncating prompt+image context.** Discovered via: qwen2.5vl threw a hard, informative 400 error (`exceeds the available context size`) where llava's older engine silently degraded instead. The user's own hypothesis ("is context window length the issue for the other models too?") was confirmed directly: raising `num_ctx` to 8192 took `llava` from 11 misses to 5. This is the single most important finding of the session — worth remembering the *shape* of the bug (silent truncation with no error, not a crash) if similar accuracy issues come up again with other Ollama models.

13. **`num_ctx` made configurable (`ollama.num_ctx` in `config.yaml`, default 8192) rather than left hardcoded, specifically because safe headroom differs by machine** — this Mac has 24GB unified memory and no memory pressure; the eventual Ubuntu 3060 box has fixed, much smaller VRAM. Verified via `ollama show`'s architecture-max context values (misleading — that's the model's *capability* ceiling, not Ollama's actual runtime default) vs. the real observed runtime default (4096 for qwen2.5vl, confirmed via its actual 400 error; almost certainly Ollama's global 2048 default for models like llava whose Modelfile doesn't override it).

14. **`bakllava` testing revealed a second, distinct bug: the response parser was too strict.** It failed the *entire image* on one unparseable line even when other lines correctly named the right species — the model clearly saw rhinos/lions/elephants/giraffes correctly but wouldn't reliably stick to the requested `name: confidence` line format. Fixed by making the parser skip bad lines and keep good ones (only error if *nothing* parseable came back), plus adding a one-shot example to the prompt. This is a permanent code improvement, not a bakllava-specific workaround — it also slightly helped context around parsing noise for other models.

15. **Full 5-model comparison, `num_ctx=8192`:**
    - `qwen2.5vl`: 25/26 tagged, 0 false negatives, 1 timeout (not a detection miss) — best by a wide margin.
    - `llava`: 17 tagged / 4 review_needed / 5 no_detection / 0 errors (after the `num_ctx` fix).
    - `llama3.2-vision`: 0/0/0/26 — completely broken on this Mac's Ollama install (`unknown model architecture: 'mllama'`), even after a full app update (0.30.10 → 0.33.2) and a fresh model re-pull. Root cause not resolved — plausibly the app's bundled inference engine didn't actually get replaced by the in-app updater. Untested whether a full from-scratch reinstall would fix it.
    - `bakllava`: format-compliance issues dominate; sees the right animals, ~62-69% of images still end up "error" due to non-conforming output even after the parser fix.
    - `moondream`: 11/0/15/0 — too small (1.8B params), and its **architectural max context is only 2048 tokens** — genuinely cannot benefit from raising `num_ctx` past that, unlike the other models.

16. **Raised `num_ctx` further to 16384 to test whether more headroom helps further.** Result: only `llava` improved meaningfully (17→20 tagged); `qwen2.5vl` was already at its practical ceiling at 8192; `moondream` is capped by its own 2048 architectural max regardless of what's requested; `bakllava`'s slight regression (8→6 tagged) is almost certainly sampling-run variance given its core issue is format-compliance, not context. **Conclusion: 8192 is the right shipped default, not 16384** — diminishing/no returns beyond it for the best model.

17. **Given `qwen2.5vl`'s near-perfect result, the user chose to still spec (not build) the MegaDetector/SpeciesNet path**, explicitly deferring the actual build to when the Ubuntu 3060 box exists — "we will build it once the 3060 is installed and i can test it there on 100's of images." Reasoning offered by the user for going this route despite qwen2.5vl already working well: wants to validate the purpose-built ecology pipeline (the standard tool ecologists actually use, confirmed via prior-art research) at real volume before deciding it's unnecessary.

18. **A file (`wildlife_vision_models_registry.md`) appeared in `openspec/specs/` mid-session, self-described as "structured for direct parsing by an AI coding or automation agent."** Flagged directly to the user rather than silently acted on — both because of its unusual instruction-like framing and because it was sitting in the wrong location (`openspec/specs/` is meant to be populated only by `openspec archive`, never by hand). Confirmed as the user's own reference material (created moments before their message, alongside pasted research with the same content), not a malicious injection. Moved to `reference/wildlife_vision_models_registry.md` per the user's instruction — treated throughout as informational input, never as executable instructions.

19. **Focus-quality-screening research (via a `core-researcher` agent) concluded: classical Laplacian-variance blur detection is cheap and solid; asking a VLM directly "is this in focus?" is a bad idea** (benchmarks near-random on blur judgment — VLMs read semantic content, not pixel-level sharpness); **no lightweight animal-eye-landmark detector exists**, so subject/eye-region focus detection has two unvalidated candidate approaches (VLM grounding prompt, or reusing MegaDetector's bounding boxes) rather than a settled implementation.

20. **Repo made public only after v1 was proven out through real testing, and only after an explicit tracked-file audit for secrets/private hosts/real photos** — `config.yaml` (real host) and `test-photos/` (real photos) confirmed correctly gitignored and never tracked.

## Key Findings

- **Ollama's default `num_ctx` (2048) is a silent accuracy killer for vision models with any nontrivial prompt** — this is the single highest-leverage finding of the session and likely generalizes well beyond this project. No error, no warning — just quietly worse results that look like "the model isn't very good" when the model may be fine.
- **A model can be highly accurate at *seeing* the right thing while being commercially useless for a tool that needs structured output** — `bakllava`'s failure mode (correct content, wrong format) is qualitatively different from `moondream`'s failure mode (genuinely too weak) or `llama3.2-vision`'s (broken install), and needed different diagnosis for each.
- **`ollama show`'s "context length" is the model's architectural maximum, not Ollama's actual runtime default** — don't confuse the two when debugging context-related issues.
- **The WhatsApp test-photo set (26 real images) turned out to be a genuinely good, hard test set** — mostly close-up, unambiguous wildlife shots that a weak model still managed to miss, making model-quality differences very legible.

## Known Bugs / Limitations

- `llama3.2-vision` is non-functional on this Mac's current Ollama install (`Ollama.app`, reports v0.33.2) — `unknown model architecture: 'mllama'` on every attempt, including a fresh model pull post-update. Not resolved. `qwen2.5vl` is used as the shipped default instead, so this isn't currently blocking, but flag it if `llama3.2-vision` specifically is ever needed.
- `species_tag/backends/ollama.py`'s `_REQUEST_TIMEOUT_SECONDS` (120s) is too short for at least one specific test image against `qwen2.5vl` — consistently times out, not flaky. Likely just needs raising, not a deeper fix.
- `bakllava` remains impractical for this tool even after the parser fix — documented as a known limitation, not something to keep tuning further (diminishing returns already observed).
- `species-tagging-cli-v1`'s `tasks.md` items 7.3/7.4 are technically still unchecked, even though the change has been tested far more thoroughly than those two line items describe — a future session should decide whether to formally check them off / archive the change, or leave it open pending an actual Ubuntu run.

## Open Questions

- Does a full from-scratch Ollama.app reinstall (not the in-app updater) fix the `mllama` architecture error? Untested.
- Which of the two `subject-focus-detection` candidate approaches (VLM grounding prompt vs. MegaDetector reuse) actually works, if either — genuinely unresolved, gated behind `focus-quality-screening/tasks.md` task 3.1's pilot.
- Should `species-tagging-cli-v1` be formally archived now, or left open until a literal Ubuntu run happens? Not decided this session.
- Has `gkwilderness` been added as a collaborator on the now-public repo yet? Last known state: not done, user said they'd handle it themselves.

## Immediate Next Actions

1. Confirm with the user whether `species-tagging-cli-v1` should be archived (`openspec archive species-tagging-cli-v1`) given the extensive manual testing already done, or left open for a literal Ubuntu-machine run.
2. When the Ubuntu 3060 box exists: start `openspec/changes/megadetector-speciesnet-backend/tasks.md` at Task 0.
3. If focus-quality screening becomes a priority: `openspec/changes/focus-quality-screening/tasks.md` section 1 (`frame-blur-detection`) can be built immediately, independent of the 3060 timeline.
