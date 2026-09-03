## Purpose

Catches the failure mode frame-level blur detection can't: a technically "sharp enough" frame where the *animal* is soft because the camera focused on the background instead — the difference between a globally blurry photo and a front/back-focus miss.

## ADDED Requirements

### Requirement: Localized sharpness comparison
The system SHALL compare a sharpness measure computed inside a detected-animal region against a sharpness measure computed over the rest of the frame (or the whole frame as a baseline).

#### Scenario: Subject sharper than background
- **WHEN** the detected-animal region has a higher local sharpness score than the surrounding frame
- **THEN** the image is treated as correctly focused on the subject

#### Scenario: Subject softer than background
- **WHEN** the detected-animal region has a lower local sharpness score than the surrounding frame
- **THEN** the image is flagged as front/back-focused — the camera focused on the wrong thing

### Requirement: Depends on a subject-region source, not built standalone
The system SHALL obtain the animal bounding region from an existing detection source (either the Ollama backend via a grounding-capable prompt, or the `megadetector-speciesnet-backend` change's detection stage) rather than implementing its own detector.

#### Scenario: No bounding region available
- **WHEN** the active pipeline configuration provides no animal bounding region for an image (e.g. a plain Ollama species-ID call with no grounding support)
- **THEN** subject-focus-detection is skipped for that image — it degrades gracefully to frame-blur-detection's whole-frame result rather than failing

### Requirement: Pilot validation gates full build-out
The system's detection-method choice (VLM grounding-prompt vs. reusing MegaDetector) SHALL be validated against a real sample of animal-eye/subject crops before being adopted as the shipped approach — this is not yet a settled design decision (see design.md's Decisions and Open Questions).

#### Scenario: Pilot shows a method is unreliable
- **WHEN** a candidate bounding-region source (e.g. VLM grounding prompts) is piloted against ~20 real images and found unreliable for animal subjects specifically
- **THEN** that method is not adopted, and the other candidate (or a decision to drop this capability) is used instead — the pilot result is what decides the approach, not an assumption made now
