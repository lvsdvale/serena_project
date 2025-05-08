"""test_get_prescription tool"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_DIR)

from llm_fixtures import *
from tools.get_prescripiton_tool import get_prescriptions_by_device


def test_get_prescription_by_device_return(
    mock_db_url, mock_device_id, mock_prescription_query_response
):
    result = get_prescriptions_by_device.invoke(
        {"database_url": mock_db_url, "device_id": mock_device_id}
    )
    assert result == mock_prescription_query_response
