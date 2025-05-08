"""This file implements the get_diagnoses_by_device tool"""

import os
import sys

from langchain.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_DIR)

from dotenv import load_dotenv

load_dotenv()

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DB_URL, echo=True)
Session = sessionmaker(bind=engine)


@tool
def get_diagnoses_by_device(device_id: str) -> str:
    """
    Retrieves all diagnosed diseases for the patient associated with the given device ID. use everytime to generate a good response.

    Parameters:
        device_id: The device identifier associated with the patient.

    Returns:
        A string listing the diseases diagnosed for the patient, or a message if none are found.
    """
    try:
        session = Session()

        query = text(
            """
            SELECT d.disease_name, dd.diagnosed_at
            FROM senior s
            JOIN disease_diagnosis dd ON s.senior_id = dd.Senior_senior_id
            JOIN disease d ON dd.disease_disease_type_id = d.disease_type_id
            WHERE s.serena_device_serena_device_code = :device_id
        """
        )
        results = session.execute(query, {"device_id": device_id}).fetchall()

        if not results:
            return f"No diagnosed diseases found for device ID '{device_id}'."

        disease_list = [
            f"{row['disease_name']} (diagnosed at {row['diagnosed_at']})"
            for row in results
        ]

        return "Diagnosed diseases: " + "; ".join(disease_list)

    except Exception as e:
        return f"Error retrieving diagnoses: {str(e)}"
    finally:
        session.close()
