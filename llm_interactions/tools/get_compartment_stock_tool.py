"""Implements compartment stock toll"""

import json

from langchain.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@tool
def get_compartment_stock_by_device(database_url: str, device_id: str) -> json:
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

        compartment_query = text(
            """
            SELECT c.stock_id,
                    c.medicine_name,
                    c.amount
            FROM compartment c
            WHERE c.serena_device_serena_device_code = :device_id
                            """
        )
        results = session.execute(
            compartment_query, {"device_id": device_id}
        ).fetchall()

        stock_list = list()
        for row in results:
            stock_list.append(
                {"stock_id": row[0], "medicine_name": row[1], "amount": row[2]}
            )
        return json.dumps(stock_list, indent=2, ensure_ascii=False)

    except Exception as e:
        return f"Error retrieving diagnoses: {str(e)}"
    finally:
        session.close()
