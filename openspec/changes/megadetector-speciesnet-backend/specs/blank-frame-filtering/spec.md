## Purpose

Runs a purpose-built animal/human/vehicle/empty detector on each image before any species classification happens, so obviously-empty frames (the majority of most camera-trap batches) are tagged cheaply and correctly without ever reaching the slower species classifier.

## ADDED Requirements

### Requirement: Four-way frame classification
The system SHALL classify each image into exactly one of: Animal, Human, Vehicle, or Empty, using a MegaDetector-family model.

#### Scenario: Empty camera-trap trigger
- **WHEN** an image contains no animal, human, or vehicle (e.g. wind-triggered blank frame)
- **THEN** it is classified Empty and no bounding box is produced

#### Scenario: Animal present
- **WHEN** an image contains one or more animals
- **THEN** it is classified Animal, with a bounding box per detected animal

### Requirement: Empty and non-animal frames skip species classification entirely
The system SHALL NOT invoke species classification for any image classified Human, Vehicle, or Empty — only Animal-classified images proceed to the next stage.

#### Scenario: Human in frame
- **WHEN** an image is classified Human (e.g. a ranger walking past a camera trap)
- **THEN** no species classification call is made for that image
- **AND** it is tagged the same way as a v1 `no_detection` outcome (no species keyword written) — this is not a false negative, it's a correct "not wildlife" call

### Requirement: Cropped region per animal detection
For each Animal-classified detection, the system SHALL produce a cropped image region (the bounding box, or a sensible padded version of it) to hand to species classification.

#### Scenario: Multiple animals in one frame
- **WHEN** an image contains two distinct animal bounding boxes
- **THEN** two separate cropped regions are produced, each handed independently to species classification
