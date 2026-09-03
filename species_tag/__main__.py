"""CLI entry point: `python -m species_tag <folder> --config config.yaml`.

Wires discovery -> identification -> tagging into one pipeline. Per-image
try/except here is the error-handling boundary (design.md's "Error handling
shape"): a failure in any stage for one image is caught, reported, counted,
and the batch continues.
"""

import argparse
import sys
from pathlib import Path

from . import discovery, exif, reporting, tagging
from .backends.ollama import OllamaBackend
from .config import ConfigError, load_config


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="species_tag",
        description="Batch-tag a folder of wildlife photos with species keywords using a local Ollama vision model.",
    )
    parser.add_argument("folder", help="Folder to recursively scan for images")
    parser.add_argument("--config", required=True, help="Path to config.yaml")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 1

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"Error: '{folder}' is not a directory", file=sys.stderr)
        return 1

    backend = OllamaBackend(host=config.ollama.host, model=config.ollama.active_model)
    images = discovery.find_images(folder)
    tally = reporting.Tally()

    for image_path in images:
        try:
            if discovery.is_raw(image_path):
                image_bytes = exif.extract_preview(image_path)
            else:
                image_bytes = image_path.read_bytes()

            results = backend.identify(image_bytes, config.region_context)
            keywords = tagging.build_keywords(results, config.min_confidence)
            exif.write_keywords(image_path, keywords)

            outcome = reporting.classify_outcome(keywords)
            reporting.print_progress(image_path, outcome, config.ollama.active_model)
            tally.record(outcome)
        except Exception as exc:  # noqa: BLE001 - intentional: one bad image must not halt the batch
            reporting.print_progress(image_path, "error", config.ollama.active_model, detail=str(exc))
            tally.record("error")

    reporting.print_summary(tally)
    return 0


if __name__ == "__main__":
    sys.exit(main())
