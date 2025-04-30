"""This file implements a OCR class for medicine names"""

import os
import re
from typing import Optional

import cv2
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pytesseract import image_to_string


class OCRPipeline:
    """
    A class that encapsulates an OCR pipeline for extracting and cleaning text from images.

    The OCR process includes:
    - Reading and preprocessing the input image
    - Extracting text using Tesseract OCR
    - Removing Portuguese stopwords from the extracted text

    Attributes:
        raw_text_output (str): Raw text output from Tesseract OCR.
        processed_text_output (str): Cleaned text output with stopwords removed.
    """

    def __init__(self):
        """
        Initializes the OCRPipeline class and downloads necessary NLTK resources.
        """
        self.__raw_text_output: Optional[str] = None
        self.__processed_text_output: Optional[str] = None

        nltk.download("stopwords")
        nltk.download("punkt")
        nltk.download("punkt_tab")

    @property
    def raw_text_output(self) -> Optional[str]:
        """Returns the raw text output from the OCR process."""
        return self.__raw_text_output

    @raw_text_output.setter
    def raw_text_output(self, raw_text_output: Optional[str]) -> None:
        """
        Sets the raw text output.

        Parameters:
            raw_text_output (Optional[str]): The raw text extracted from the image.

        Raises:
            TypeError: If the input is not a string or None.
        """
        if not isinstance(raw_text_output, str) and raw_text_output is not None:
            raise TypeError(
                f"last raw output must be str or None, instead got {type(raw_text_output)}"
            )
        self.__raw_text_output = raw_text_output

    @property
    def processed_text_output(self) -> Optional[str]:
        """Returns the cleaned, processed text output with stopwords removed."""
        return self.__processed_text_output

    @processed_text_output.setter
    def processed_text_output(self, processed_text_output: Optional[str]) -> None:
        """
        Sets the processed text output.

        Parameters:
            processed_text_output (Optional[str]): Cleaned version of the OCR text.

        Raises:
            TypeError: If the input is not a string or None.
        """
        if (
            not isinstance(processed_text_output, str)
            and processed_text_output is not None
        ):
            raise TypeError(
                f"last raw output must be str or None, instead got {type(processed_text_output)}"
            )
        self.__processed_text_output = processed_text_output

    def read_image(self, image_path: str):
        """
        Reads and converts the image to RGB format.

        Parameters:
            image_path (str): Path to the input image.

        Returns:
            image: Preprocessed RGB image.
        """
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    def preprocess_image(image: np.ndarray) -> np.ndarray:
        """
        Preprocess the image for better OCR performance.

        parameters:
            img (np.ndarray): RGB input image.

        Returns:
            np.ndarray: Thresholded and sharpened grayscale image.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(blur, -1, sharpen_kernel)
        _, thresh = cv2.threshold(
            sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return thresh

    def process_output(self) -> None:
        """
        Processes the raw OCR text by removing Portuguese stopwords and storing the result.
        """
        stopwords_pt = set(stopwords.words("portuguese"))
        if self.raw_text_output is not None:
            processed_text = word_tokenize(self.raw_text_output.lower())
            processed_text_without_stopwords = [
                word
                for word in processed_text
                if word not in stopwords_pt and word.isalnum()
            ]
            processed_text = " ".join(processed_text_without_stopwords)
            words = re.findall(r"\b[a-zA-Záéíóúãõâêôç]{2,}\b", processed_text.lower())
            clean_words = [w for w in words if len(w) > 3]
            processed_text = " ".join(clean_words)
            self.processed_text_output = processed_text

    def image_to_string(self, image: str) -> None:
        """
        Executes the OCR pipeline: reads the image, extracts text, and processes it.

        Parameters:
            image_path (str): Path to the input image.

        Prints:
            str: The cleaned, processed OCR output.
        """
        self.raw_text_output = image_to_string(image)
        self.process_output()
        print(self.processed_text_output)

    def image_path_to_string(self, image_path: str) -> None:
        """
        Executes the OCR pipeline: reads the image, extracts text, and processes it.

        Parameters:
            image_path (str): Path to the input image.

        Prints:
            str: The cleaned, processed OCR output.
        """
        image = self.read_image(image_path)
        self.raw_text_output = image_to_string(image)
        self.process_output()
        print(self.processed_text_output)
