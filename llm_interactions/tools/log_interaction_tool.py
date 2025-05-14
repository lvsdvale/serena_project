"""This file implements the log interaction tool"""

import os
import sys
from datetime import datetime

from langchain.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@tool
def log_interaction(
    database_url: str, symptom: str, suggestion: str, device_id: str
) -> str:
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
    engine = create_engine(database_url, echo=True)
    Session = sessionmaker(bind=engine)
    try:
        session = Session()

        senior_query = text(
            """
            SELECT senior_senior_id, senior_user_id
            FROM serena_device
            WHERE serena_device_code = :device_id
        """
        )
        senior = session.execute(senior_query, {"device_id": device_id}).fetchone()

        if not senior:
            return f"No patient associated with device ID '{device_id}'."

        senior_id = senior[0]
        user_id = senior[1]

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        insert_query = text(
            """
            INSERT INTO complaint (symptom, serena_llm_response, create_time, senior_senior_id, senior_user_user_id)
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
