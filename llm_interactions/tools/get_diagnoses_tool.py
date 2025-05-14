"""This file implements the get_diagnoses_by_device tool"""

import json
from datetime import datetime

from langchain.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@tool
def get_diagnoses_by_device(database_url: str, device_id: str) -> json:
    """
    Retrieves all diagnosed diseases for the patient associated with the given device ID. use everytime to generate a good response.

    Parameters:
        database_url(str): the database acess url.
        device_id: The device identifier associated with the patient.

    Returns:
        A Json listing the diseases diagnosed for the patient, or a message if none are found.
    """
    try:
        engine = create_engine(database_url, echo=True)
        Session = sessionmaker(bind=engine)
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

        disease_query = text(
            """
            SELECT dd.disease_name,
                    dd.diagnosed_at
            FROM disease_diagnosis dd
            WHERE dd.senior_senior_id = :senior_id
                            """
        )
        results = session.execute(disease_query, {"senior_id": senior_id}).fetchall()

        disease_list = list()
        for row in results:
            disease_list.append(
                {
                    "disease_name": row[0],
                    "diagnosed_at": (
                        row[2].strftime("%Y-%m-%d %H:%M:%S")
                        if isinstance(row[1], datetime)
                        else row[1]
                    ),
                }
            )
        return json.dumps(disease_list, indent=2, ensure_ascii=False)

    except Exception as e:
        return f"Error retrieving diagnoses: {str(e)}"
    finally:
        session.close()
