## Purpose

Drives a batch run end-to-end from a config file and a target folder, and tells the user what's happening — since the tool keeps no log files, the console is the only window into a run.

## ADDED Requirements

### Requirement: YAML config drives every run
The system SHALL load run configuration (backend, Ollama host/model, `models_to_test`, `region_context`, `min_confidence`) from a YAML file, invoked as `python -m species_tag <folder> --config config.yaml`.

#### Scenario: Valid config
- **WHEN** a valid `config.yaml` is supplied with all required fields
- **THEN** the run uses those values for backend, model, region hint, and confidence threshold

#### Scenario: Missing required field
- **WHEN** `config.yaml` is missing a required field (e.g. `ollama.host`)
- **THEN** the system reports a clear config error and exits before processing any images

### Requirement: Live per-image progress
The system SHALL print one progress line per image as it is processed, showing the filename, the outcome, and the model used.

#### Scenario: Batch run in progress
- **WHEN** the tool is processing a folder of images
- **THEN** each image's result (species tagged / review_needed / no_detection / error) is printed as it completes, before the next image starts

### Requirement: End-of-run summary
The system SHALL print a summary tally at the end of a run, counting images tagged, flagged review_needed, marked no_detection, and errored.

#### Scenario: Run completes
- **WHEN** a batch run finishes processing all discovered images
- **THEN** a summary line reports the count in each of the four outcome categories

### Requirement: Per-image failures do not halt the batch
The system SHALL continue processing remaining images when a single image fails (extraction, identification, or write error), and SHALL include it in the error count.

#### Scenario: One file fails mid-batch
- **WHEN** one image in a folder of many fails during processing
- **THEN** that image is counted as an error in the summary
- **AND** every other image in the folder is still processed
