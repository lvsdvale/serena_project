"""This file implements the get prescription tool"""

import json
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

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", "5432"),
}

print(DB_CONFIG)

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# SQLAlchemy setup


@tool
def get_prescriptions_by_device(database_url: str, device_id: str) -> str:
    """
    Returns all prescriptions for the patient associated with a given device ID. Use this tool to see what medications the patient is already prescribed. It can be helpful in assessing what they can take for a reported symptom.

    Parameters:
        device_id: The code of the Serena device (serena_device_code)

    Returns:
        A JSON string containing all prescription items for the patient.
    """
    engine = create_engine(database_url, echo=True)
    Session = sessionmaker(bind=engine)

    try:
        session = Session()
        senior_query = text(
            """
            SELECT senior_user_id
            FROM senior
            WHERE device_code = :device_id
        """
        )
        senior_result = session.execute(
            senior_query, {"device_id": device_id}
        ).fetchone()

        if not senior_result:
            return f"No senior found with device ID '{device_id}'."

        senior_id = senior_result[0]
        prescription_query = text(
            """
            SELECT
                p.prescription_id,
                pi.medication_name,
                pi.dosage,
                pi.duration_time
            FROM prescription p
            JOIN prescription_item pi ON p.prescription_id = pi.prescription_id
            WHERE p.senior_user_id = :senior_id
        """
        )

        results = session.execute(
            prescription_query, {"senior_id": senior_id}
        ).fetchall()

        if not results:
            return f"No prescriptions found for senior with device ID '{device_id}'."

        prescriptions = []
        for row in results:
            prescriptions.append(
                {
                    "prescription_id": row[0],
                    "medication_name": row[1],
                    "dosage": row[2],
                    "duration_time": (
                        row[3].strftime("%Y-%m-%d %H:%M:%S")
                        if isinstance(row[3], datetime)
                        else row[3]
                    ),
                }
            )

        return json.dumps(prescriptions, indent=2)

    except Exception as e:
        return f"Error while querying prescriptions: {str(e)}"
    finally:
        session.close()
