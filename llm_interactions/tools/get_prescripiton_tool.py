"""This file implements the get prescription tool"""

import json
from datetime import datetime

from langchain.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@tool
def get_prescriptions_by_device(database_url: str, device_id: str) -> json:
    """
    Returns all prescriptions for the patient associated with a given device ID. Use this tool to see what medications the patient is already prescribed. It can be helpful in assessing what they can take for a reported symptom.

    Parameters:
        database_url(str): the database acess url.
        device_id: The code of the Serena device (serena_device_code).

    Returns:
        A JSON string containing all prescription items for the patient.
    """
    engine = create_engine(database_url, echo=True)
    Session = sessionmaker(bind=engine)

    try:
        session = Session()
        senior_query = text(
            """
            SELECT senior_senior_id
            FROM serena_device
            WHERE serena_device_code = :device_id
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
            pi.medicine_name,
            pi.dosage,
            pi.duration_time
        FROM prescription p
        JOIN prescription_item pi ON p.prescription_id = pi.prescription_prescription_id
        WHERE p.senior_senior_id = :senior_id
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
