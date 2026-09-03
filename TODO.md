# TODO

## v1 (Ollama-based CLI): implemented and tested

`species_tag/` is built (sections 1–6 + unit tests 7.1/7.2 of `openspec/changes/species-tagging-cli-v1/tasks.md`, all checked off). Manually tested end-to-end against 26 real photos, across all five practical Ollama vision models. Key findings:

- **`qwen2.5vl` is the best model**: 25/26 correct, 0 false negatives, 1 slow-timeout (not a detection failure). Set as the working default.
- **Real bug found and fixed:** Ollama's default `num_ctx` (2048) was silently truncating prompt+image context, causing false `no_detection` results. Now configurable via `config.yaml`'s `ollama.num_ctx` (default 8192) instead of hardcoded — see commit history.
- `llava`, `bakllava`, `moondream`, `llama3.2-vision` all have real limitations (miss rate, format non-compliance, too-small context ceiling, and an Ollama-install-specific `mllama` architecture bug respectively) — see conversation/commit history for the full comparison data if revisiting model choice.
- `species-tagging-cli-v1` change is not yet archived (`openspec archive species-tagging-cli-v1`) — the remaining manual verification tasks (7.3 wider real-photo run, 7.4 Ubuntu pass) are still open.

## v2 (MegaDetector + SpeciesNet backend): specced, not built

`openspec/changes/megadetector-speciesnet-backend/` — full proposal/specs/design/tasks written and validated. **Deliberately not implemented yet** — build is deferred until the Ubuntu 3060 box is available, so it can be built and tested against real hardware and hundreds of images from day one instead of guessing on this Mac. See that change's `tasks.md` for the full checklist (starts with a Task 0 prerequisites section: GPU drivers, CUDA, confirming current package sources).

## Repo

- [ ] Made public (was private under `oneafrikan`).
- [ ] Add `gkwilderness` as a GitHub collaborator, so it's usable from both accounts.

## Other ideas raised, not committed to

- Focus/blur-quality screening (eye-in-focus detection) — researched (Laplacian variance for frame-level blur is cheap and solid; subject/eye-region focus is a genuinely harder unsolved problem, no good lightweight existing solution found). Not scoped as a change yet.
- v1's own deferred list (cloud API backend, GUI, scientific names, hierarchical keywords, results database, pip packaging) — see `openspec/changes/species-tagging-cli-v1/proposal.md`.
