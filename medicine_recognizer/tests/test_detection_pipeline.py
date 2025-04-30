"""
This file contains unit tests for the DetectionPipeline class, which is responsible for detecting medicine boxes
and extracting text using OCR from video frames.

Test coverage includes:
- Validation of the stability threshold property.
- Bounding box movement stability checks.
- Type safety for the YOLO model and OCR pipeline attributes.

The tests use pytest to ensure expected behaviors and to catch improper usage of the class.
"""

import os
import sys

import numpy as np
import pytest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_DIR = os.path.dirname(MODULE_DIR)

sys.path.append(MODULE_DIR)
sys.path.append(PROJECT_DIR)

from detection_pipeline import DetectionPipeline


def test_stability_threshold_setter():
    """
    Test that setting a valid stability threshold updates the property correctly.
    """
    detection_pipeline = DetectionPipeline("medicine_recognizer/models/best.pt")
    detection_pipeline.stability_threshold = 15
    assert detection_pipeline.stability_threshold == 15


def test_stability_threshold_type_error():
    """
    Test that assigning a non-integer value to stability_threshold raises a TypeError.
    """
    detection_pipeline = DetectionPipeline("medicine_recognizer/models/best.pt")

    with pytest.raises(TypeError):
        detection_pipeline.stability_threshold = "not an int"


def test_is_stable_within_threshold():
    """
    Test that is_stable returns True when the movement between bounding boxes is within the threshold.
    """
    detection_pipeline = DetectionPipeline("medicine_recognizer/models/best.pt")
    last_bbox = np.array([10, 10, 100, 100])
    current_bbox = np.array([12, 12, 102, 102])
    detection_pipeline.stability_threshold = 10
    assert detection_pipeline.is_stable(last_bbox, current_bbox)


def test_is_stable_exceeds_threshold():
    """
    Test that is_stable returns False when the movement between bounding boxes exceeds the threshold.
    """
    detection_pipeline = DetectionPipeline("medicine_recognizer/models/best.pt")
    last_bbox = np.array([10, 10, 100, 100])
    current_bbox = np.array([50, 50, 140, 140])
    detection_pipeline.stability_threshold = 10
    assert not detection_pipeline.is_stable(last_bbox, current_bbox)


def test_yolo_model_setter_invalid_type():
    """
    Test that assigning a non-YOLO model to the yolo_model property raises a TypeError.
    """
    detection_pipeline = DetectionPipeline("medicine_recognizer/models/best.pt")
    with pytest.raises(TypeError):
        detection_pipeline.yolo_model = "invalid_model"


def test_ocr_pipeline_setter_invalid_type():
    """
    Test that assigning a non-OCRPipeline object to the ocr_pipeline property raises a TypeError.
    """
    detection_pipeline = DetectionPipeline("medicine_recognizer/models/best.pt")
    with pytest.raises(TypeError):
        detection_pipeline.ocr_pipeline = "invalid_pipeline"
