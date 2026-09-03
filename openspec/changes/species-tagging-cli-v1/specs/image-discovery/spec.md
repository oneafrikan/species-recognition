## Purpose

Walks a folder tree to find every processable image, and normalizes RAW files into a JPEG the vision backend can consume, so the rest of the pipeline only ever handles plain JPEG bytes.

## ADDED Requirements

### Requirement: Recursive folder scan
The system SHALL recursively scan a given target folder for image files, including all subdirectories.

#### Scenario: Mixed folder contents
- **WHEN** the target folder contains RAW files, JPEGs, PNGs, and non-image files across nested subfolders
- **THEN** every RAW, JPEG, and PNG file at any depth is queued for processing
- **AND** non-image files are skipped without being counted as errors

### Requirement: Supported RAW formats
The system SHALL recognize Canon (CR2, CR3), Nikon (NEF), Fujifilm (RAF), and Sony (ARW) RAW files by extension.

#### Scenario: Each supported RAW extension is picked up
- **WHEN** the target folder contains a `.CR2`, `.CR3`, `.NEF`, `.RAF`, and `.ARW` file
- **THEN** all five are queued for processing

### Requirement: RAW preview extraction
For RAW files, the system SHALL extract the embedded preview JPEG (via exiftool) as the image sent downstream, rather than performing a full RAW decode.

#### Scenario: RAW file with a usable embedded preview
- **WHEN** a queued RAW file has an embedded preview image
- **THEN** that preview is extracted and passed to species identification
- **AND** no RAW decoding library is invoked

#### Scenario: RAW file with no extractable preview
- **WHEN** a queued RAW file has no embedded preview exiftool can extract
- **THEN** the file is reported as an error for that image
- **AND** processing continues with the next file

### Requirement: JPEG/PNG pass-through
The system SHALL pass JPEG and PNG files directly to species identification without a preview-extraction step.

#### Scenario: Plain JPEG input
- **WHEN** a queued file is a `.jpg`/`.jpeg` or `.png`
- **THEN** it is sent to species identification unmodified
