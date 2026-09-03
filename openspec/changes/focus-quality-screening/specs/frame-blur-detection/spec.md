## Purpose

Flags whole images that are motion-blurred or globally soft, using a cheap classical sharpness measure, so obviously unusable shots are caught without any model inference.

## ADDED Requirements

### Requirement: Frame sharpness scoring
The system SHALL compute a sharpness score for each processed image using Laplacian variance (edge-energy based, no ML model).

#### Scenario: Sharp image
- **WHEN** an image is in clear focus with well-defined edges
- **THEN** its sharpness score is computed and compared against the configured threshold

#### Scenario: Motion-blurred image
- **WHEN** an image has visible motion blur (soft edges throughout the frame)
- **THEN** its sharpness score is measurably lower than a sharp image of similar content

### Requirement: Configurable threshold, calibrated per user
The system SHALL compare the sharpness score against a configurable threshold rather than a fixed universal value, since Laplacian variance has no threshold that generalizes across cameras/subjects/lighting.

#### Scenario: Below-threshold image
- **WHEN** a sharpness score falls below the configured threshold
- **THEN** the image is flagged as blurry (see keyword behavior below)

### Requirement: Blur flag written as an additional keyword
The system SHALL write a `blurry` keyword (reusing v1's exiftool write path — XMP `dc:Subject` + IPTC `Keywords`, flat, no CSV/log file) when an image is flagged below threshold, independent of and in addition to any species keyword already written for that image.

#### Scenario: Blurry photo of a confidently-identified animal
- **WHEN** an image is tagged with a confident species keyword AND its sharpness score is below threshold
- **THEN** the image carries both the species keyword and the `blurry` keyword — a blurry photo of a known species is still filterable as "needs a sharper shot," not silently dropped
