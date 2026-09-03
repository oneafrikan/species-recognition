# species-recognition — context for future sessions

Personal project (Gareth), not part of the `guide-engine` meta-repo (it's gitignored there — this repo lives at `guide-engine/species-recognition/` on this laptop purely as a matter of where it happened to be created, not a dependency relationship). Will be used within a Wilderness context later (stakeholder demo of local vision models) but is not Wilderness client work.

## Repo / GitHub

- Private repo under the personal `oneafrikan` GitHub account (not `gkwilderness`, the Wilderness work account).
- Remote: `git@github-personal:oneafrikan/species-recognition.git` — note the `github-personal` SSH host alias, not the default `github.com` alias (which authenticates as `gkwilderness` on this machine). Machine-specific SSH/account details: `~/.dev-env/claude-private/machines/wilderness.md`.
- Will later add `gkwilderness` as a collaborator so it's usable from both accounts. Not done yet.

## Where the spec lives

This repo uses [OpenSpec](https://github.com/Fission-AI/OpenSpec) (`openspec init` already run, config at `openspec/config.yaml`). The full v1 spec is in `openspec/changes/species-tagging-cli-v1/`:

- `proposal.md` — why, what's changing, capability list
- `specs/<capability>/spec.md` — behavior contracts for `image-discovery`, `species-identification`, `metadata-tagging`, `cli-reporting`
- `design.md` — architecture: module layout, `VisionBackend` abstraction, exiftool wrapper choice, config schema, and why `icewall905/image-tagger` was evaluated but not vendored
- `tasks.md` — the build checklist, grouped by module, in dependency order

Read `design.md` before writing any code here — it has the module layout and the key decisions (why pyexiftool, why plain-text model output instead of JSON mode, why no RAW-decode library) already made. Don't re-derive them.

**When implementation is complete:** run `openspec archive species-tagging-cli-v1` to move the change into `openspec/specs/` as the source of truth. `openspec init` also installed `.claude/skills/openspec-*` and `.claude/commands/opsx/*` (`/opsx:propose`, `/opsx:apply`, `/opsx:archive`, etc.) — use those for any future change instead of the raw `openspec` CLI where convenient.

## Status as of 2026-09-03

Spec complete (proposal, 4 capability specs, design, tasks all written and `openspec validate --strict` passing). **No implementation yet.** Next step is working through `tasks.md` section by section — scaffold first, then discovery → identification → tagging → CLI wiring → tests, in that order (each section depends on the last).

## Key decisions not to relitigate

These came out of a full requirements interview with the user — see `proposal.md`/`design.md` for the reasoning, but the short version:

- RAW handling is embedded-preview extraction only, never a full RAW decode (rawpy/libraw deliberately avoided — fragile cross-platform dependency, no accuracy benefit for species ID).
- No CSV/log files anywhere. All state lives in the image's own EXIF/XMP/IPTC metadata plus console output.
- Flat keywords only (`"African Elephant"`, `"review_needed"`, `"no_detection"`) — no hierarchical Lightroom keywords.
- No idempotency/skip-if-tagged logic — every run reprocesses every image. This was a deliberate simplicity choice, not an oversight.
- No hardcoded species checklist — geography is a free-text `region_context` config value templated into the model prompt, because this tool is used across multiple continents, not just Africa.
- Cloud vision backend is an architected extension point only — do not implement an actual cloud provider without the user asking for it.

## Deferred to v2+ (do not build without being asked)

Cloud API backend implementation, GUI, blank-frame pre-filtering (MegaDetector-style), scientific-name field, hierarchical keywords, results database, parallelized/multi-GPU processing, pip-installable packaging.
