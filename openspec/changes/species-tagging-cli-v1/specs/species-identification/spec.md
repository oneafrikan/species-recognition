## Purpose

Sends a normalized image to a configured Ollama vision model with a geographic hint, and returns the species it sees plus how confident it is, so downstream tagging logic never has to talk to the model directly.

## ADDED Requirements

### Requirement: Configurable Ollama backend
The system SHALL send each image to an Ollama vision model at a configurable host URL, using a configurable active model name.

#### Scenario: Remote Ollama host
- **WHEN** config specifies `ollama.host: http://192.168.1.50:11434` and `ollama.model: llama3.2-vision`
- **THEN** identification requests are sent to that host and model, not to a hardcoded localhost address

### Requirement: Multiple candidate models
The system SHALL allow more than one Ollama model to be listed in config for comparison, with one designated as the active model for a given run.

#### Scenario: Switching the active model
- **WHEN** `models_to_test` lists `llama3.2-vision`, `llava`, and `minicpm-v`, and `active_model` is set to `llava`
- **THEN** the run uses `llava` for every image in that run

### Requirement: Region-hint prompting
The system SHALL inject a free-text `region_context` config value into the prompt sent to the vision model as a geographic hint, with no species checklist hardcoded in the tool.

#### Scenario: Region context changes the prompt
- **WHEN** `region_context` is set to "Southeast Asian rainforest wildlife"
- **THEN** that text appears in the prompt sent to the model for every image in the run
- **AND** the model is not restricted to a fixed list of species names

### Requirement: Species and confidence in every response
For each image, the system SHALL obtain zero or more identified species names, each with a confidence level, from the model's response.

#### Scenario: Single species, high confidence
- **WHEN** the model identifies one animal it is confident about
- **THEN** identification returns exactly one species name with a high-confidence indicator

#### Scenario: Multiple species in one frame
- **WHEN** the model identifies two distinct animals in the same image
- **THEN** identification returns both species names, each with its own confidence indicator

#### Scenario: No animal present
- **WHEN** the model determines no animal is present in the image
- **THEN** identification returns zero species

### Requirement: Backend failure is per-image, not fatal
If the Ollama backend cannot be reached or returns an error for a given image, the system SHALL record that image as an error and continue processing the rest of the batch.

#### Scenario: Ollama host unreachable
- **WHEN** the configured Ollama host does not respond
- **THEN** the current image is reported as an error
- **AND** the batch run continues to the next image rather than terminating
