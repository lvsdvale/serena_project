import os
import re
from typing import Optional
import numpy as np # Importa numpy para o tipo de imagem
import cv2 # Importa OpenCV para imencode

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from google.cloud import vision

class OCRPipeline:
    """
    A class that encapsulates an OCR pipeline for extracting and cleaning text from images
    using Google Cloud Vision API, while maintaining original function names.

    The OCR process includes:
    - Extracting text using Google Cloud Vision API
    - Removing Portuguese stopwords from the extracted text

    Attributes:
        raw_text_output (str): Raw text output from Google Cloud Vision API.
        processed_text_output (str): Cleaned text output with stopwords removed.
    """

    def __init__(self, credentials_path: str = 'gen-lang-client-0227226319-73e9fc54298a.json'):
        """
        Initializes the OCRPipeline class, sets up Google Cloud Vision client,
        and downloads necessary NLTK resources.

        Parameters:
            credentials_path (str): Path to the Google Cloud service account JSON key file.
        """
        self.__raw_text_output: Optional[str] = None
        self.__processed_text_output: Optional[str] = None

        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        self.vision_client = vision.ImageAnnotatorClient()

        try:
            nltk.data.find('corpora/stopwords')
        except nltk.downloader.DownloadError:
            nltk.download("stopwords")
        try:
            nltk.data.find('tokenizers/punkt')
        except nltk.downloader.DownloadError:
            nltk.download("punkt")

    @property
    def raw_text_output(self) -> Optional[str]:
        return self.__raw_text_output

    @raw_text_output.setter
    def raw_text_output(self, raw_text_output: Optional[str]) -> None:
        if not isinstance(raw_text_output, str) and raw_text_output is not None:
            raise TypeError(
                f"raw_text_output must be str or None, instead got {type(raw_text_output)}"
            )
        self.__raw_text_output = raw_text_output

    @property
    def processed_text_output(self) -> Optional[str]:
        return self.__processed_text_output

    @processed_text_output.setter
    def processed_text_output(self, processed_text_output: Optional[str]) -> None:
        if (
            not isinstance(processed_text_output, str)
            and processed_text_output is not None
        ):
            raise TypeError(
                f"processed_text_output must be str or None, instead got {type(processed_text_output)}"
            )
        self.__processed_text_output = processed_text_output

    def process_output(self) -> None:
        """
        Processes the raw OCR text by removing Portuguese stopwords and storing the result.
        """
        stopwords_pt = set(stopwords.words("portuguese"))
        if self.raw_text_output is not None:
            processed_text = word_tokenize(self.raw_text_output.lower())
            processed_text_without_stopwords = [
                word for word in processed_text
                if word not in stopwords_pt and word.isalnum()
            ]
            processed_text = " ".join(processed_text_without_stopwords)

            words = re.findall(r"\b[a-zA-Záéíóúãõâêôç]{2,}\b", processed_text)
            clean_words = [w for w in words if len(w) > 2]

            self.processed_text_output = " ".join(clean_words)
        else:
            self.processed_text_output = None

    def image_to_string(self, image: np.ndarray) -> None:
        """
        Executes the OCR pipeline using Google Cloud Vision API.
        This function now expects an OpenCV image (numpy array) as input.

        Parameters:
            image (np.ndarray): The input image as a NumPy array (from cv2.imread).

        Prints:
            str: The cleaned, processed OCR output.
        """
        try:
            # Converte a imagem OpenCV (array NumPy) para bytes no formato JPEG
            # O ".jpg" é uma sugestão de formato; pode ser ".png" se preferir.
            # O importante é que seja um formato de imagem válido.
            is_success, buffer = cv2.imencode(".jpg", image)
            if not is_success:
                raise ValueError("Could not encode image to JPEG format.")

            content = buffer.tobytes()
            vision_image = vision.Image(content=content)

            # Chama a API do Google Cloud Vision para detecção de texto
            response = self.vision_client.text_detection(image=vision_image)
            texts = response.text_annotations

            if texts:
                self.raw_text_output = texts[0].description
            else:
                self.raw_text_output = None
                print("Nenhum texto detectado pela Google Cloud Vision API.")

            if response.error.message:
                raise Exception(f"Erro na Vision API: {response.error.message}")

            self.process_output()
            print("Texto processado (chamada image_to_string):")
            print(self.processed_text_output)

        except Exception as e:
            print(f"Ocorreu um erro durante o OCR (image_to_string): {e}")
            self.raw_text_output = None
            self.processed_text_output = None

    def image_path_to_string(self, image_path: str) -> None:
        """
        Executes the OCR pipeline using Google Cloud Vision API: reads the image from path,
        extracts text, and processes it.

        Parameters:
            image_path (str): Path to the input image.

        Prints:
            str: The cleaned, processed OCR output.
        """
        try:
            # Lendo a imagem com OpenCV para ter o mesmo tipo de entrada que image_to_string espera agora
            image_from_path = cv2.imread(image_path)
            if image_from_path is None:
                raise FileNotFoundError(f"Não foi possível carregar a imagem do caminho: {image_path}")

            # Delega para image_to_string, que agora aceita o array NumPy
            self.image_to_string(image_from_path)
            print("Texto processado (chamada image_path_to_string):")
            print(self.processed_text_output)

        except FileNotFoundError as e:
            print(f"Erro: {e}")
            self.raw_text_output = None
            self.processed_text_output = None
        except Exception as e:
            print(f"Ocorreu um erro durante o OCR (image_path_to_string): {e}")
            self.raw_text_output = None
            self.processed_text_output = None