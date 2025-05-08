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
def log_interaction(symptom: str, suggestion: str, device_id: str) -> str:
    """
    Logs a patient's reported symptom and the assistant's response in the database
    using the device_id to identify the patient.

    Args:
        symptom: Symptom reported by the patient (e.g., "headache").
        suggestion: Assistant's recommendation or treatment suggestion.
        device_id: Device identifier associated with the patient.

    Returns:
        A confirmation message with timestamp or error description.
    """
    try:
        session = Session()

        senior_query = text(
            """
            SELECT senior_id, user_user_id
            FROM senior
            WHERE serena_device_serena_device_code = :device_id
        """
        )
        senior = session.execute(senior_query, {"device_id": device_id}).fetchone()

        if not senior:
            return f"No patient associated with device ID '{device_id}'."

        senior_id = senior["senior_id"]
        user_id = senior["user_user_id"]

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        insert_query = text(
            """
            INSERT INTO complaint (syptom, serena_llm_response, create_time, Senior_senior_id, Senior_user_user_id)
            VALUES (:symptom, :suggestion, :timestamp, :senior_id, :user_id)
        """
        )
        session.execute(
            insert_query,
            {
                "symptom": symptom,
                "suggestion": suggestion,
                "timestamp": timestamp,
                "senior_id": senior_id,
                "user_id": user_id,
            },
        )

        session.commit()
        return f"Symptom logged successfully at {timestamp}."

    except Exception as e:
        return f"Error logging symptom: {str(e)}"
    finally:
        session.close()
