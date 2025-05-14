"""this implements fixtures"""

import json
import os
import sys

import pytest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_DIR)

from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def mock_db_url():
    DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    return DB_URL


@pytest.fixture
def mock_prescription_query_response():
    expected_value = [
        {
            "prescription_id": 1,
            "medication_name": "Paracetamol",
            "dosage": "1 comprimido",
            "duration_time": 2,
        },
    ]
    return json.dumps(expected_value, indent=2)


@pytest.fixture
def mock_device_id():
    return "SERENA001"
