## Purpose

Turns a species-identification result into the correct keyword(s) for an image and writes them into that image's own metadata via exiftool, so results are filterable in Lightroom with no separate log files.

## ADDED Requirements

### Requirement: Confident results are written as species keywords
When one or more species are identified at or above the configured confidence threshold, the system SHALL write each species' common name as its own keyword to the image's XMP `dc:Subject` and IPTC `Keywords` fields.

#### Scenario: Single confident species
- **WHEN** identification returns "African Elephant" at high confidence and the threshold is `medium`
- **THEN** the image's XMP Subject and IPTC Keywords each gain the keyword "African Elephant"

#### Scenario: Multiple confident species
- **WHEN** identification returns "Zebra" and "Wildebeest", both at or above threshold
- **THEN** the image gains both "Zebra" and "Wildebeest" as separate keywords

### Requirement: Low-confidence results are flagged for review
When a species is identified below the configured confidence threshold, the system SHALL write both the species guess and a `review_needed` keyword to the image.

#### Scenario: Guess below threshold
- **WHEN** identification returns "Impala" at low confidence and the threshold is `medium`
- **THEN** the image gains the keywords "Impala" and "review_needed"

### Requirement: No detection is tagged distinctly
When identification returns no species for an image, the system SHALL write only a `no_detection` keyword, with no species keyword.

#### Scenario: Empty camera-trap frame
- **WHEN** identification returns zero species for an image
- **THEN** the image gains the single keyword "no_detection"
- **AND** no species keyword is written

### Requirement: Configurable confidence threshold
The system SHALL allow the confidence threshold (`low`, `medium`, `high`) to be set in config, determining the cutoff between the confident and review_needed outcomes above.

#### Scenario: Threshold raised to high
- **WHEN** `min_confidence` is set to `high` and a species is identified at medium confidence
- **THEN** that result is treated as below-threshold and tagged with `review_needed`, not as a confident result

### Requirement: Original file is preserved on every write
The system SHALL keep exiftool's default automatic backup (`<filename>_original`) whenever it writes metadata, and SHALL NOT pass a flag that disables it.

#### Scenario: Successful keyword write
- **WHEN** the system writes a keyword to an image file
- **THEN** an untouched `_original` copy of that file exists alongside it afterward

### Requirement: Every run reprocesses every image
The system SHALL NOT check for or skip images that already carry keywords from a prior run; every invocation processes every image found by folder discovery.

#### Scenario: Rerun on an already-tagged image
- **WHEN** the tool is run a second time over a folder whose images already carry species keywords from a previous run
- **THEN** every image is sent through identification and tagging again, with no skip logic
