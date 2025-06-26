"""implement useful functions"""

import json
import re
import time
from typing import Any, Dict, List, Union

from llm_interactions.tools.get_compartment_stock_tool import \
    get_compartment_stock_by_device
from llm_interactions.tools.get_medication_names_tool import get_medication
from llm_interactions.tools.update_compartment_stock_amout_tool import \
    update_compartment_stock
from medicine_recognizer.detection_pipeline import DetectionPipeline

# from dispenser_controller.dispenser import MedicineDispenser


def try_except(log_error=True, default_return=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    print(f"[!] Erro em '{func.__name__}': {e}")
                return default_return

        return wrapper

    return decorator


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
    print(stock_data)
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
    if "dis" in option:
        return 1
    elif "câmera" in option:
        return 2
    return None


def parse_to_json(llm_output: str) -> Dict[str, Any]:
    """
    Extracts the first valid JSON object from a string returned by a language model (LLM),
    removing any surrounding text, headers, or formatting (e.g., markdown or comments).

    Parameters:
        llm_output (str): The raw output string returned by the LLM.

    Returns:
        Dict[str, Any]: A Python dictionary representing the parsed JSON object.

    Raises:
        ValueError: If no JSON is found or the JSON is invalid.
    """
    try:
        match = re.search(r"\{.*\}", llm_output, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in the LLM output.")

        raw_json = match.group(0)
        return json.loads(raw_json)

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")


@try_except(default_return="Computer Vision Pipeline ERROR")
def computer_vision_pipeline(
    medicine_names: Union[str, list],
    medication_list,
    decoder,
    light_controller=None,
    timeout: int = 90,
):
    """
    Runs a vision-based medication recognition pipeline with a timeout.

    Args:
        medicine_names (Union[str, list]): Name or list of expected medicines.
        medication_list (list): List of valid medications in the system.
        decoder: Decoder object with a string_to_speech() method.
        timeout (int): Maximum time (in seconds) to confirm each medicine.
    """
    if isinstance(medicine_names, str):
        medicine_names = [medicine_names]

    decoder.string_to_speech(
        "Iniciando reconhecimento do medicamento, deixa caixa próxima a camera"
    )

    for medicine in medicine_names:
        medicine_confirmation = False
        detection_pipeline = DetectionPipeline(light_controller=light_controller)
        start_time = time.time()

        while not medicine_confirmation:
            # Check for timeout
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                decoder.string_to_speech(
                    f"Tempo esgotado para identificar o remédio {medicine}"
                )
                break  # or raise TimeoutError("Timeout during medicine confirmation")

            detection_response = detection_pipeline.run_detection()
            print(detection_response)

            medication_list = [med.lower() for med in medication_list]
            detection_response_words = [
                word.lower() for word in detection_response.split(" ")
            ]
            medication_found = set(detection_response_words) & set(medication_list)
            if not medication_found:
                decoder.string_to_speech(
                    f"Rémedio não identificado, você gostaria de tentar novamente"
                )
                option = decoder.audio_to_string()
                while not option.strip():
                    decoder.string_to_speech("Desculpe, não entendi. Pode repetir?")
                    option = decoder.audio_to_string()
                if "não" in option.lower():
                    break

            if medication_found:
                if medicine.lower() not in detection_response_words:
                    decoder.string_to_speech(
                        f"Esse não é o remédio correto, o remédio correto é {medicine}, você mostrou o {list(medication_found)[0]}"
                    )
                    continue
                medicine_confirmation = True
            else:
                decoder.string_to_speech(
                    "O Remédio mostrado está fora da base de dados"
                )

        if medicine_confirmation:
            decoder.string_to_speech("Esse é o remédio certo, pode tomar")


def get_compartments_by_medicine_name(
    medicine_names: List[str], stock_list: List[Dict]
) -> List[Dict]:
    stocks_to_update_list = []
    index_list = []
    for name in medicine_names:
        for index in range(len(stock_list)):
            if stock_list[index]["medication_name"].lower() == name.lower():
                index_list.append(index + 1)
                stocks_to_update_list.append(stock_list[index])
                break
    return stocks_to_update_list, index_list


def dispenser_pipeline(
    device_compartments: List[Dict],
    medicine_names: Union[str, List[str]],
    medication_list: List[str],
    quantity_used_list: List[int],
    decoder,
    dispenser_controller,
    light_controller,
) -> List[Dict]:
    if isinstance(medicine_names, str):
        medicine_names = [medicine_names]

    compartments, compartments_indexes = get_compartments_by_medicine_name(
        medicine_names, device_compartments
    )
    updates = []
    if not compartments or len(compartments) < len(medicine_names):
        decoder.string_to_speech(
            "O remédio sugerido não se encontra no dispenser, você gostária de utilizar a camera"
        )
        command = decoder.audio_to_string()
        while not command.strip():
            decoder.string_to_speech("Desculpe, não entendi. Pode repetir?")
            command = decoder.audio_to_string()
        if "sim" in command.lower():
            computer_vision_pipeline(
                medicine_names,
                medication_list,
                decoder,
                light_controller=light_controller,
            )
        return updates

    dispenser_controller.run(compartments_indexes)
    for index in range(len(compartments)):
        compartment = compartments[index]
        quantity_used = quantity_used_list[index]
        new_amount = compartment["quantity"] - quantity_used
        updates.append(
            {
                "compartment_id": compartment["compartment_id"],
                "medication_name": compartment["medication_name"],
                "medication_id": compartment["medication_id"],
                "quantity": new_amount,
            }
        )

    return updates
