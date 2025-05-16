"""implement useful functions"""

import re
from typing import Union

from llm_interactions.tools.get_compartment_stock_tool import \
    get_compartment_stock_by_device
from llm_interactions.tools.get_medication_names_tool import get_medication
from llm_interactions.tools.update_compartment_stock_amout_tool import \
    update_compartment_stock
from medicine_recognizer.detection_pipeline import DetectionPipeline


def get_stock_ids_by_name(medicine_names, stock_data):
    """
    Retrieves a list of stock IDs for one or more medicine names from the provided stock data.

    Args:
        medicine_names (str or list): A single medicine name (str) or a list of medicine names.
        stock_data (list): A list of dictionaries, each containing 'stock_id' and 'medicine_name'.

    Returns:
        list: A list of stock IDs corresponding to the given medicine names. Names not found are ignored.
    """
    if isinstance(medicine_names, str):
        medicine_names = [medicine_names]

    medicine_index = {
        item["medicine_name"].lower(): item["stock_id"] for item in stock_data
    }

    return [
        medicine_index[name.lower()]
        for name in medicine_names
        if name.lower() in medicine_index
    ]


def extract_quantity_from_dose(dose_str):
    """
    Extracts the integer quantity from a dose string like '1 comprimido'.
    Returns None if no integer found.
    """
    match = re.search(r"\d+", dose_str)
    return int(match.group()) if match else None


def hash_option(option: str) -> int:
    if "dispenser" in option:
        return 1
    elif "câmera" in option:
        return 2
    return None


def computer_vision_pipeline(
    database_url: str, medicine_names: Union[str, list], decoder
):
    medication_list = [
        medication["medication_name"]
        for medication in get_medication({"database_url": database_url})
    ]
    for medicine in medicine_names:
        medicine_confirmation = False
        detection_pipeline = DetectionPipeline()
        while not medicine_confirmation:
            detection_response = detection_pipeline.run_detection()
            medication_found = set(detection_response.split(" ")) & set(medication_list)
            if medication_found:
                if medicine in detection_response:
                    medicine_confirmation = True
            else:
                decoder.string_to_speech(
                    f"Esse não é o remédio correto, o remédio correto é {medicine}, você mostrou o {detection_response}"
                )
        decoder.string_to_speech("Esse é o remédio certo pode tomar")


def dispenser_pipeline(
    database_url: str,
    device_id: str,
    medicine_names: Union[str, list],
    quantity_used_list: list,
    decoder,
):
    compartment_stock = get_compartment_stock_by_device(device_id)
    compartment_ids = get_stock_ids_by_name(medicine_names, compartment_stock)
    if not compartment_ids or medicine_names > compartment_ids:
        computer_vision_pipeline(database_url, medicine_names, decoder)
    for index in range(len(compartment_ids)):
        compartment_id = compartment_ids[index]
        quantity_used = quantity_used_list[index]

        update_compartment_stock(
            {
                "database_url": database_url,
                "stock_id": compartment_id,
                "quantity_used": quantity_used,
            }
        )
