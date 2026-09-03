"""Unit tests for tagging.py's confidence-bucket logic.

Covers the four metadata-tagging spec scenarios (confident single/multiple
species, below-threshold guess, no detection) plus the full confidence x
threshold matrix (task 7.1: "high/medium/low across each threshold setting").
"""

import pytest

from species_tag.backends.base import SpeciesResult
from species_tag.tagging import build_keywords


def test_single_confident_species():
    # metadata-tagging spec: "Single confident species"
    results = [SpeciesResult("African Elephant", "high")]
    assert build_keywords(results, "medium") == ["African Elephant"]


def test_multiple_confident_species():
    # metadata-tagging spec: "Multiple confident species"
    results = [SpeciesResult("Zebra", "high"), SpeciesResult("Wildebeest", "medium")]
    assert build_keywords(results, "medium") == ["Zebra", "Wildebeest"]


def test_guess_below_threshold():
    # metadata-tagging spec: "Guess below threshold"
    results = [SpeciesResult("Impala", "low")]
    assert build_keywords(results, "medium") == ["Impala", "review_needed"]


def test_no_detection():
    # metadata-tagging spec: "Empty camera-trap frame"
    assert build_keywords([], "medium") == ["no_detection"]


def test_threshold_raised_to_high_flags_medium_as_review_needed():
    # metadata-tagging spec: "Threshold raised to high"
    results = [SpeciesResult("Lion", "medium")]
    assert build_keywords(results, "high") == ["Lion", "review_needed"]


def test_mixed_confidence_flags_review_needed_once():
    # One confident + one below-threshold result in the same image: species name
    # for both is always included, review_needed is appended once, not per-result.
    results = [SpeciesResult("Zebra", "high"), SpeciesResult("Impala", "low")]
    assert build_keywords(results, "medium") == ["Zebra", "Impala", "review_needed"]


@pytest.mark.parametrize(
    "confidence,threshold,expect_review_needed",
    [
        ("low", "low", False),
        ("low", "medium", True),
        ("low", "high", True),
        ("medium", "low", False),
        ("medium", "medium", False),
        ("medium", "high", True),
        ("high", "low", False),
        ("high", "medium", False),
        ("high", "high", False),
    ],
)
def test_confidence_threshold_matrix(confidence, threshold, expect_review_needed):
    results = [SpeciesResult("Kudu", confidence)]
    keywords = build_keywords(results, threshold)
    assert "Kudu" in keywords
    assert ("review_needed" in keywords) == expect_review_needed
