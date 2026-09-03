# species-recognition — context for future sessions

Personal project (Gareth), not part of the `guide-engine` meta-repo (it's gitignored there — this repo lives at `guide-engine/species-recognition/` on this laptop purely as a matter of where it happened to be created, not a dependency relationship). Will be used within a Wilderness context later (stakeholder demo of local vision models) but is not Wilderness client work.

## Repo / GitHub

- Private repo under the personal `oneafrikan` GitHub account (not `gkwilderness`, the Wilderness work account).
- Remote: `git@github-personal:oneafrikan/species-recognition.git` — note the `github-personal` SSH host alias, not the default `github.com` alias (which authenticates as `gkwilderness` on this machine). Machine-specific SSH/account details: `~/.dev-env/claude-private/machines/wilderness.md`.
- Will later add `gkwilderness` as a collaborator so it's usable from both accounts. Not done yet.

## Where the spec lives

This repo uses [OpenSpec](https://github.com/Fission-AI/OpenSpec) (`openspec init` already run, config at `openspec/config.yaml`, with a project `context` block). Two changes exist under `openspec/changes/`:

- **`species-tagging-cli-v1`** — the Ollama-based CLI (`species_tag/`). Proposal, 4 capability specs (`image-discovery`, `species-identification`, `metadata-tagging`, `cli-reporting`), design, tasks. **Implemented and manually tested** (see Status below) — not yet archived, since 7.3/7.4 (wider real-photo run, Ubuntu pass) are still open.
- **`megadetector-speciesnet-backend`** — an alternate detect-then-classify backend (MegaDetector + SpeciesNet), targeting the Ubuntu 3060 box. Proposal, 2 capability specs (`blank-frame-filtering`, `species-classification-local`), design, tasks. **Spec only, deliberately not implemented** — build is deferred until that hardware exists.

Read the relevant change's `design.md` before writing any code — module layout and key decisions are already made there. Don't re-derive them. `openspec init` also installed `.claude/skills/openspec-*` and `.claude/commands/opsx/*` (`/opsx:propose`, `/opsx:apply`, `/opsx:archive`, etc.) — use those for any future change instead of the raw `openspec` CLI where convenient.

## Status as of 2026-09-03

**v1 (`species_tag/`, Ollama-based) is built and manually tested against 26 real photos.** Key findings, in case model choice or config defaults ever come into question:

- **`qwen2.5vl` is the best of the five practical Ollama vision models tested** — 25/26 correct, 0 false negatives. Not yet set as the shipped default in `config.example.yaml` (still `llama3.2-vision`, which has an install-specific bug on this Mac — see below); worth revisiting.
- **Real bug found via testing, not theory:** Ollama's own default context window (2048 tokens) was silently truncating prompt+image context on most models, causing false `no_detection` results — this was the majority root cause of early poor accuracy, not model weakness. Fixed by making `num_ctx` configurable (`config.yaml`'s `ollama.num_ctx`, default 8192) instead of relying on Ollama's default. Raising further to 16384 only helped the weaker models marginally; 8192 is the right default.
- `llama3.2-vision` fails entirely on this Mac's Ollama install (`unknown model architecture: 'mllama'`) even after a full app update and fresh model re-pull — a real, unresolved install issue, not a code bug. Works fine architecturally (11B model, well-supported elsewhere); don't assume it's broken everywhere.
- `bakllava` sees animals correctly but won't reliably follow the requested output format — a model instruction-following limitation, not fixable by prompt/parser tuning alone (the parser was made more tolerant of partial-format responses as a result, which is a real, permanent improvement — see `ollama.py`'s `_parse_response`).
- `moondream` is too small (1.8B, hard 2048-token context ceiling) for reliable results.

**v2 (`megadetector-speciesnet-backend`) exists only as a spec.** Next step there is Task 0 (confirm 3060 box has GPU drivers/CUDA working) once that hardware exists — see that change's `tasks.md`.

## Key decisions not to relitigate

These came out of a full requirements interview with the user — see `proposal.md`/`design.md` for the reasoning, but the short version:

- RAW handling is embedded-preview extraction only, never a full RAW decode (rawpy/libraw deliberately avoided — fragile cross-platform dependency, no accuracy benefit for species ID).
- No CSV/log files anywhere. All state lives in the image's own EXIF/XMP/IPTC metadata plus console output.
- Flat keywords only (`"African Elephant"`, `"review_needed"`, `"no_detection"`) — no hierarchical Lightroom keywords.
- No idempotency/skip-if-tagged logic — every run reprocesses every image. This was a deliberate simplicity choice, not an oversight.
- No hardcoded species checklist — geography is a free-text `region_context` config value templated into the model prompt, because this tool is used across multiple continents, not just Africa.
- Cloud vision backend is an architected extension point only — do not implement an actual cloud provider without the user asking for it.

## Deferred (do not build without being asked)

Cloud API backend implementation, GUI, scientific-name field, hierarchical keywords, results database, parallelized/multi-GPU processing, pip-installable packaging. (Blank-frame pre-filtering / MegaDetector is no longer just deferred — it has a real spec now, see `megadetector-speciesnet-backend` above; it's just not built yet.)
