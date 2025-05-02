"""This file implements the log interaction tool"""

import os
import sys

from get_prescripiton_tool import get_prescription
from langchain.tools import tool

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_DIR)

from config import llm


@tool
def process_patient_input(patient_input: str, patient_id: str) -> str:
    """
    This function processes the spoken input of the patient,
    determines whether the input contains a symptom, and if so,
    retrieves the appropriate medication advice.

    Args:
        patient_input: The speech input from the patient (e.g., "I'm having a headache").
        patient_id: Unique identifier of the patient in the database.

    Returns:
        A response indicating the next steps, such as medication advice or follow-up questions.
    """
    symptom = identify_symptom(patient_input)

    if symptom:
        prescription_advice = get_prescription(
            symptom, patient_id, "prescriptions_table"
        )
        return prescription_advice
    else:
        return "Could you please describe your symptoms in more detail?"


def identify_symptom(patient_input: str) -> str:
    """
    This function uses the LLM to analyze the patient's input and decide if a symptom is mentioned.

    Args:
        patient_input: The speech input from the patient.

    Returns:
        A string representing the symptom detected, or None if no symptom is identified.
    """

    symptom_template = """
    Given the following input from a patient, determine if it describes a symptom:
    Patient says: "{patient_input}"    
    If it's a symptom, return the symptom name. Otherwise, return "None".
    """

    prompt = symptom_template.format(patient_input=patient_input)

    symptom = llm(prompt)

    if symptom.lower() != "none":
        return symptom.strip()
    else:
        return None
