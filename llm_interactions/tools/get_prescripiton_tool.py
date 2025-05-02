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
engine = create_engine(DB_URL, echo=True)
Session = sessionmaker(bind=engine)


@tool
def get_prescription(symptom: str, patient_id: str, table_name: str) -> str:
    """
    Queries the database for medications recommended for a given symptom,
    considering the patient's medical conditions and contraindications.
    After querying the database, it generates a prescription recommendation
    using the LLM.

    Args:
        symptom: Symptom reported by the patient (e.g., "headache").
        patient_id: Unique identifier of the patient in the database.
        table_name: Name of the prescription table to query.

    Returns:
        A string with the medication recommendation.
    """
    try:
        session = Session()

        # 1. Retrieve patient information
        query = text(
            """
            SELECT contraindications, medical_history
            FROM patients
            WHERE patient_id = :patient_id
        """
        )
        result = session.execute(query, {"patient_id": patient_id}).fetchone()

        if not result:
            return f"No patient found with ID '{patient_id}'."

        contraindications = (
            result["contraindications"].split(",")
            if result["contraindications"]
            else []
        )
        patient_history = result["medical_history"]

        query = text(
            f"""
            SELECT name, dosage, substances
            FROM {table_name}
            WHERE :symptom ILIKE ANY (symptoms)
        """
        )
        prescriptions = session.execute(query, {"symptom": symptom}).fetchall()

        safe_meds = []
        prescription_guidance = ""
        for presc in prescriptions:
            substances = presc["substances"].split(",") if presc["substances"] else []
            if any(
                c.lower() in [s.lower() for s in substances] for c in contraindications
            ):
                continue
            safe_meds.append(f"{presc['name']} ({presc['dosage']})")

        if not safe_meds:
            return "No safe medications found for the reported symptom."

        prescription_guidance = ", ".join(safe_meds)
        prescription_guidance = prescription_guidance.join(patient_history)

        return prescription_guidance

    except Exception as e:
        return f"Error while querying prescriptions: {str(e)}"
    finally:
        session.close()
