"""This file implements the get prescription tool"""

import os
import sys
from datetime import datetime

from langchain.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_DIR)

from dotenv import load_dotenv

from medicine_recognizer.detection_pipeline import DetectionPipeline

load_dotenv()

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# SQLAlchemy setup
engine = create_engine(DB_URL, echo=True)
Session = sessionmaker(bind=engine)


@tool
def trigger_detection() -> str:
    """
    Starts the visual recognition process via video + OCR
    to detect the medicine being taken by the patient.

    Returns:
        A string with the name of the detected medicine.
    """
    detection_pipeline = DetectionPipeline()
    try:
        detected = detection_pipeline.run_detection()
        return f"Detected medicine: {detected}"
    except Exception as e:
        return f"Error during detection: {str(e)}"
