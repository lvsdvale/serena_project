"""implement useful functions"""

import re


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


def dispenser_pipeline():
    pass


def computer_vision_pipenile():
    pass
