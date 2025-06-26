"""
This file implements the DetectionPipeline class, which handles the real-time detection
of medicine packages using a YOLO model and extracts text via OCR.
"""

import os
import subprocess
import time
from typing import Optional

import cv2
import numpy as np
import ultralytics
from ultralytics import YOLO

from medicine_recognizer.ocr_pipeline import OCRPipeline

# from ocr_pipeline import OCRPipeline


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
        self,
        yolo_model_path: str = os.path.join(
            os.path.dirname(__file__), "models", "best.pt"
        ),
        stability_threshold: int = 10,
        light_controller=None,
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
        self.light_controller = light_controller

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
        Captures a single image using subprocess, applies YOLO detection,
        runs OCR on the first detected box, and returns the extracted text.

        Returns:
            str: Extracted text from the detected medicine box.
        """
        if self.light_controller is not None:
            self.light_controller.green_on()

        image_path = "/tmp/captured.jpg"

        try:
            # Captura a imagem usando libcamera-jpeg
            subprocess.run(
                [
                    "libcamera-jpeg",
                    "-o",
                    image_path,
                    "-n",
                    "--width",
                    "640",
                    "--height",
                    "480",
                ],
                check=True,
            )

            # Aguarda um pouco para garantir que a imagem seja salva
            time.sleep(1)

            # Lê a imagem capturada
            frame = cv2.imread(image_path)
            if frame is None:
                raise RuntimeError("Failed to load captured image.")

            if self.light_controller is not None:
                self.light_controller.blue_on()

            results = self.yolo_model(frame)[0]

            if len(results.boxes) > 0:
                x1, y1, x2, y2 = map(int, results.boxes[0].xyxy[0])
                crop = frame[y1:y2, x1:x2]
                text = self.process_ocr(crop)
                return text.strip()

            return ""

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to capture image with subprocess: {e}")
