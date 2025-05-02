"""This file implements the log interaction tool"""

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

load_dotenv()

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# SQLAlchemy setup
engine = create_engine(DB_URL, echo=True)
Session = sessionmaker(bind=engine)


@tool
def log_interaction(symptom: str, suggestion: str, patient_id: str) -> str:
    """
    Logs a patient's reported symptom and the suggested treatment in the database.

    Args:
        symptom: Symptom reported by the patient.
        suggestion: Medication or advice provided by the assistant.
        patient_id: ID of the patient.

    Returns:
        A confirmation string with timestamp of the log entry.
    """
    try:
        session = Session()

        timestamp = datetime.utcnow()
        query = text(
            """
            INSERT INTO interactions (patient_id, symptom, suggestion, timestamp)
            VALUES (:patient_id, :symptom, :suggestion, :timestamp)
        """
        )
        session.execute(
            query,
            {
                "patient_id": patient_id,
                "symptom": symptom,
                "suggestion": suggestion,
                "timestamp": timestamp,
            },
        )
        session.commit()

        return f"Interaction logged successfully at {timestamp}."

    except Exception as e:
        return f"Error logging interaction: {str(e)}"
    finally:
        session.close()
