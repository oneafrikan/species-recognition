# TODO

## Current phase: spec complete, build not started

Full build checklist lives in `openspec/changes/species-tagging-cli-v1/tasks.md` — that's the source of truth, tracked as checkboxes there. Summary of the sections, in build order:

- [ ] 1. Project scaffold (package structure, requirements.txt, config.example.yaml, README setup section)
- [ ] 2. Config loading (`config.py`)
- [ ] 3. Image discovery (`discovery.py`, RAW preview extraction)
- [ ] 4. Species identification (`backends/base.py`, `backends/ollama.py`)
- [ ] 5. Metadata tagging (`tagging.py`, `exif.py` write path)
- [ ] 6. CLI + reporting (`__main__.py`, `reporting.py`)
- [ ] 7. Verify (unit tests + manual end-to-end run on Ubuntu)

## After v1 ships

- Add `gkwilderness` as a GitHub collaborator on this repo.
- Consider making the repo public (currently private) once it's proven out.
- v2 candidates (not started, see `openspec/changes/species-tagging-cli-v1/proposal.md` for the full deferred list): cloud API backend, GUI, blank-frame pre-filtering, scientific names, hierarchical keywords, results database, pip packaging.
