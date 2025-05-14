"""This file implement get medication tool"""

import json
from typing import Union

from langchain.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@tool
def get_medication(database_url: str) -> str:
    """
    Retrieve a JSON-formatted list of medication names from the database.

    This tool connects to the provided SQL database using the given `database_url`,
    executes a query to fetch all medication names from the `medication` table,
    and returns the results as a JSON string.

    Parameters:
        database_url (str): A SQLAlchemy-compatible database URL

    Returns:
        str: A JSON string containing a list of medications,
             or a JSON string with an error message.

    """
    try:
        engine = create_engine(database_url, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()

        medication_query = text(
            """
            SELECT m.medication_name
            FROM medication m
        """
        )
        results = session.execute(medication_query).fetchall()

        medications = [{"medication_name": row[0]} for row in results]
        return json.dumps(medications, ensure_ascii=False)

    except Exception as e:
        return json.dumps(
            {"error": f"Error retrieving medication: {str(e)}"},
            ensure_ascii=False,
            indent=2,
        )
    finally:
        session.close()
