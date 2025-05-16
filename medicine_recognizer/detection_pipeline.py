"""
This file implements the DetectionPipeline class, which handles the real-time detection
of medicine packages using a YOLO model and extracts text via OCR.
"""

from typing import Optional

import cv2
import numpy as np
import ultralytics
from ultralytics import YOLO

from medicine_recognizer.ocr_pipeline import OCRPipeline


class DetectionPipeline:
    """
    DetectionPipeline implements a video-based object detection and OCR pipeline for medicine packages.

    This class captures video from the default webcam, applies a YOLO model to detect medicine boxes,
    checks for bounding box stability across frames, and applies OCR to extract and return text.

    Attributes:
        yolo_model (YOLO): YOLO object detection model instance.
        ocr_pipeline (OCRPipeline): OCR processing pipeline instance.
        stability_threshold (int): Movement threshold in pixels for bounding box stability.
    """

    def __init__(
        self, yolo_model_path: str = "models/best.pt", stability_threshold: int = 10
    ):
        """
        Initializes the DetectionPipeline with a YOLO model and an OCR pipeline.

        Parameters:
            yolo_model_path (str): Path to the YOLO model (.pt file).
            stability_threshold (int): Maximum pixel movement to consider a detection stable.
        """
        self.__ocr_pipeline = OCRPipeline()
        self.__yolo_model = YOLO(yolo_model_path)
        self.stability_threshold_setter(stability_threshold)

    @property
    def yolo_model(self) -> ultralytics.models.yolo.model.YOLO:
        """
        Returns:
            YOLO: The current YOLO model instance.
        """
        return self.__yolo_model

    @yolo_model.setter
    def yolo_model(self, yolo_model: ultralytics.models.yolo.model.YOLO) -> None:
        """
        Sets a new YOLO model instance.

        Parameters:
            yolo_model (YOLO): A YOLO model instance.

        Raises:
            TypeError: If the input is not a YOLO instance.
        """
        if not isinstance(yolo_model, ultralytics.models.yolo.model.YOLO):
            raise TypeError(
                f"the yolo model must be a ultralytics.models.yolo.model.YOLO, got {type(yolo_model)} instead"
            )
        self.__yolo_model = yolo_model

    @property
    def ocr_pipeline(self) -> OCRPipeline:
        """
        Returns:
            OCRPipeline: The current OCR pipeline instance.
        """
        return self.__ocr_pipeline

    @ocr_pipeline.setter
    def ocr_pipeline(self, ocr_pipeline: OCRPipeline) -> None:
        """
        Sets a new OCRPipeline instance.

        Parameters:
            ocr_pipeline (OCRPipeline): The new OCR pipeline.

        Raises:
            TypeError: If the input is not an OCRPipeline instance.
        """
        if not isinstance(ocr_pipeline, OCRPipeline):
            raise TypeError(
                f"ocr_pipeline must be an OCRPipeline class type, instead got {type(ocr_pipeline)}"
            )
        self.__ocr_pipeline = ocr_pipeline

    @property
    def stability_threshold(self) -> int:
        """
        Returns:
            int: The current stability threshold.
        """
        return self.__stability_threshold

    @stability_threshold.setter
    def stability_threshold(self, stability_threshold) -> None:
        """
        Sets the stability threshold.

        Parameters:
            stability_threshold (int): New stability threshold value.

        Raises:
            TypeError: If the value is not an integer.
        """
        if not isinstance(stability_threshold, int):
            raise TypeError(
                f"stability_threshold must be an int, instead got {type(stability_threshold)}"
            )
        self.__stability_threshold = stability_threshold

    def stability_threshold_setter(self, stability_threshold):
        """
        Helper method to call the setter from within __init__.

        Parameters:
            stability_threshold (int): Value to set.
        """
        self.stability_threshold = stability_threshold

    def is_stable(
        self, last_bbox: Optional[np.ndarray], current_bbox: np.ndarray
    ) -> bool:
        """
        Determines whether the bounding box has remained stable across frames.

        Parameters:
            last_bbox (Optional[np.ndarray]): Bounding box from the previous frame.
            current_bbox (np.ndarray): Current bounding box.

        Returns:
            bool: True if the box has moved less than the stability threshold, else False.
        """
        if last_bbox is None:
            return False
        movement = np.linalg.norm(current_bbox - last_bbox)
        return movement < self.stability_threshold

    def process_ocr(self, crop: np.ndarray) -> str:
        """
        Processes the cropped image using the OCR pipeline.

        Parameters:
            crop (np.ndarray): Cropped BGR image of the detected medicine box.

        Returns:
            str: Cleaned text extracted from the image.
        """
        cropped_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        processed_img = self.ocr_pipeline.preprocess_image(cropped_rgb)
        self.ocr_pipeline.image_to_string(processed_img)
        text = self.ocr_pipeline.processed_text_output
        return text

    def run_detection(self) -> str:
        """
        Runs the main detection and OCR pipeline.

        Starts video capture, detects medicine boxes using YOLO, waits until a box is stable
        for several frames, then runs OCR on the detected region and returns the extracted text.

        Returns:
            str: Extracted text from the detected medicine box.
        """
        cap = cv2.VideoCapture(0)

        last_bbox: Optional[np.ndarray] = None
        stable_counter: int = 0
        stable_required: int = 6

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = self.yolo_model(frame)[0]
            annotated_frame = results.plot()
            cv2.imshow("YOLO Detection", annotated_frame)

            if len(results.boxes) > 0:
                x1, y1, x2, y2 = map(int, results.boxes[0].xyxy[0])
                current_bbox = np.array([x1, y1, x2, y2])

                if self.is_stable(last_bbox, current_bbox):
                    stable_counter += 1
                else:
                    stable_counter = 0

                last_bbox = current_bbox

                if stable_counter >= stable_required:
                    crop = frame[y1:y2, x1:x2]
                    text = self.process_ocr(crop)

                    try:
                        if text.strip():
                            print(f"OCR output: {text}")
                            cap.release()
                            cv2.destroyAllWindows()
                            return text
                    except Exception as e:
                        print(f"Decoder error: {e}")
