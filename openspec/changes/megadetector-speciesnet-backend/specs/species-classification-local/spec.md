## Purpose

Classifies a cropped animal region (from `blank-frame-filtering`) into a specific species using a purpose-trained classifier's fixed taxonomy, instead of a general vision-language model's free-form naming.

## ADDED Requirements

### Requirement: Species classification on a cropped region
The system SHALL run a SpeciesNet-family classifier on each cropped animal region produced by `blank-frame-filtering` and return a species name and confidence score.

#### Scenario: Confident classification
- **WHEN** a cropped region clearly matches one of the classifier's known species
- **THEN** that species name and a confidence score are returned

#### Scenario: Low-confidence or out-of-taxonomy match
- **WHEN** a cropped region doesn't clearly match any species in the classifier's taxonomy (e.g. a species outside its training distribution, or a poor-quality crop)
- **THEN** the classifier's best-guess species and a low confidence score are returned, rather than a hard failure — this feeds the same `review_needed` bucket as v1's confidence-threshold behavior

### Requirement: Output shape matches the existing SpeciesResult contract
The system SHALL return classification results in the same shape v1's `species-identification` capability already produces (a species name plus a low/medium/high confidence level per detected animal), so `metadata-tagging` and `cli-reporting` from v1 work unchanged against this backend.

#### Scenario: Multiple animals in one image
- **WHEN** `blank-frame-filtering` produced two cropped regions for one image
- **THEN** classification runs independently on each, and both results are combined into one `SpeciesResult` list for that image — same multi-species-per-image behavior as v1

### Requirement: Region-hint context is not required
Unlike the Ollama backend's free-text `region_context` prompt hint, the system SHALL rely on the classifier's own fixed, pre-trained global taxonomy rather than a per-run geographic hint.

#### Scenario: Running against photos from a different continent
- **WHEN** the target folder contains wildlife photos from outside the classifier's best-represented regions
- **THEN** classification still runs against the same global taxonomy — accuracy may vary by region, but no config change is required to attempt it (a known accuracy caveat to validate once real test volume is available, not a blocker)
