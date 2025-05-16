"""this file test ia agent"""

import warnings

from fixtures import *
from ocr_pipeline import OCRPipeline

warnings.filterwarnings("ignore", message="'pin_memory' argument is set as true")


def test_ocr_pipeline_initialization():
    """Test if OCRPipeline initializes with None attributes."""
    pipeline = OCRPipeline()

    assert (
        pipeline.raw_text_output is None
    ), "raw_text_output should be None on initialization"
    assert (
        pipeline.processed_text_output is None
    ), "processed_text_output should be None on initialization"


def test_ocr_pipeline_has_attributes():
    """Test if OCRPipeline has required attributes and methods."""
    pipeline = OCRPipeline()

    assert hasattr(
        pipeline, "_OCRPipeline__raw_text_output"
    ), "Should have private attribute __raw_text_output"
    assert hasattr(
        pipeline, "_OCRPipeline__processed_text_output"
    ), "Should have private attribute __processed_text_output"
    assert hasattr(pipeline, "raw_text_output"), "Should have property raw_text_output"
    assert hasattr(
        pipeline, "processed_text_output"
    ), "Should have property processed_text_output"
    assert hasattr(pipeline, "preprocess_image"), "Should have method preprocess_image"
    assert hasattr(pipeline, "process_output"), "Should have method process_output"
    assert hasattr(pipeline, "image_to_string"), "Should have method image_to_string"
    assert hasattr(
        pipeline, "image_path_to_string"
    ), "Should have method image_path_to_string"


def test_raw_text_output_setter_type_error():
    """Test if raw_text_output setter raises TypeError with correct error message when given invalid type."""
    pipeline = OCRPipeline()

    with pytest.raises(TypeError) as exc_info:
        pipeline.raw_text_output = 123

    assert (
        str(exc_info.value)
        == "last raw output must be str or None, instead got <class 'int'>"
    )


def test_processed_text_output_setter_type_error():
    """Test if processed_text_output setter raises TypeError with correct error message when given invalid type."""
    pipeline = OCRPipeline()

    with pytest.raises(TypeError) as exc_info:
        pipeline.processed_text_output = ["wrong type"]

    assert (
        str(exc_info.value)
        == "last raw output must be str or None, instead got <class 'list'>"
    )


def test_raw_text_output_set_and_get(sample_raw_text):
    """Test setting and getting raw_text_output."""
    pipeline = OCRPipeline()
    pipeline.raw_text_output = sample_raw_text

    assert (
        pipeline.raw_text_output == sample_raw_text
    ), "raw_text_output should return the set value"


def test_processed_text_output_set_and_get(sample_processed_text):
    """Test setting and getting processed_text_output."""
    pipeline = OCRPipeline()
    pipeline.processed_text_output = sample_processed_text

    assert (
        pipeline.processed_text_output == sample_processed_text
    ), "processed_text_output should return the set value"


def test_ocr_image_to_string(mock_medication_image):
    """test if ocr is capturing the medicine name using PIL Image input"""
    pipeline = OCRPipeline()
    pipeline.image_to_string(mock_medication_image)
    assert (
        "ibuprofeno" in pipeline.processed_text_output
    ), "the medicine name was not found correctly"


def test_ocr_image_path_to_text(mock_medication_image_path):
    """test if ocr is capturing the medicine name using path as input"""
    pipeline = OCRPipeline()
    pipeline.image_path_to_string(mock_medication_image_path)
    assert (
        "ibuprofeno" in pipeline.processed_text_output
    ), "the medicine name was not found correctly"
