from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import requests

BASE_URL = "https://serena-api-mn6f.onrender.com"


class SerenaAPIClient:
    """
    API client for interacting with the Serena system.
    Handles authentication, automatic token renewal, and provides access to key routes.
    """

    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password
        self.token: Optional[str] = None
        self.headers: Dict[str, str] = {}
        self.login()

    def login(self) -> None:
        """
        Authenticates the user using OAuth2 password grant and sets the authorization token.
        """
        url = f"{BASE_URL}/auth/login"
        payload = {
            "grant_type": "password",
            "username": self.email,
            "password": self.password,
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        data = response.json()
        self.token = data.get("access_token")
        if not self.token:
            raise ValueError("No access_token found in login response.")
        token_type = data.get("token_type", "Bearer")
        self.headers = {"Authorization": f"{token_type} {self.token}"}

    def _auto_reauth(func: Callable) -> Callable:
        """
        Decorator that retries the API call with re-authentication if the token is expired.
        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except requests.HTTPError as e:
                if e.response.status_code == 401:
                    self.login()
                    return func(self, *args, **kwargs)
                raise

        return wrapper

    @_auto_reauth
    def get_medication_list(self) -> List[Dict[str, Any]]:
        """
        Retrieves the list of available medications from the system.
        """
        url = f"{BASE_URL}/medications"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @_auto_reauth
    def get_dispenser_status(self, device_id: int) -> List[Dict[str, Any]]:
        """
        Gets the status of the 14 compartments in the dispenser.

        Returns:
            A list of dictionaries with:
            - compartment_id
            - medication_name
            - quantity
        """
        url = f"{BASE_URL}/dispenser/by_device/{device_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @_auto_reauth
    def get_valid_prescriptions(self, device_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves valid prescriptions for the senior linked to a device.
        """
        url = f"{BASE_URL}/prescriptions/by_device/{device_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @_auto_reauth
    def update_compartment_amount(
        self, compartment_id: str, medication_id: str, quantity: int
    ) -> Dict[str, Any]:
        """
        Updates the amount of medication in a specific compartment.
        """
        url = f"{BASE_URL}/compartment/{compartment_id}"
        payload = {"quantity": quantity, "medication_id": medication_id}
        response = requests.patch(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @_auto_reauth
    def create_symptom_by_device(
        self,
        device_id: int,
        senior_id: int,
        symptom_name: str,
        description: str,
        pain_level: int,
    ) -> Dict[str, Any]:
        """
        Records a new symptom reported by a senior, based on the device ID.
        """
        url = f"{BASE_URL}/symptoms/by_device/{device_id}"
        payload = {
            "name": symptom_name,
            "description": description,
            "pain_level": pain_level,
            "senior_id": str(senior_id),
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @_auto_reauth
    def get_senior_id_by_device(self, device_id: int) -> Dict[str, Any]:
        """
        Retrieves the senior ID linked to a device.
        """
        url = f"{BASE_URL}/senior/by_device/{device_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @_auto_reauth
    def get_compartment_by_id(self, compartment_id: str) -> Dict[str, Any]:
        """
        Retrieves information about a specific compartment by its ID.

        Returns:
            A dictionary with:
            - medication_id
            - quantity
            - compartment_id
            - dispenser_id
        """
        url = f"{BASE_URL}/compartment/{compartment_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @_auto_reauth
    def get_enriched_prescriptions(self, device_id: int) -> List[Dict[str, Any]]:
        """
        Returns a list of valid prescriptions enriched with medication names and descriptions.

        Each enriched prescription contains:
        - prescription_id
        - medication_name
        - medication_description
        - frequency
        - dosage
        - start_date
        - end_date
        - senior_id
        """
        prescriptions = self.get_valid_prescriptions(device_id)
        medications = self.get_medication_list()
        med_lookup: Dict[str, Dict[str, Any]] = {m["id"]: m for m in medications}

        enriched: List[Dict[str, Any]] = []
        for p in prescriptions:
            med_info = med_lookup.get(p["medication_id"], {})
            enriched.append(
                {
                    "prescription_id": p["id"],
                    "medication_name": med_info.get("name", "Unknown"),
                    "medication_description": med_info.get("description", ""),
                    "frequency": p["frequency"],
                    "dosage": p["dosage"],
                    "start_date": p["start_date"],
                    "end_date": p["end_date"],
                    "senior_id": p["senior_id"],
                }
            )
        return enriched

    @_auto_reauth
    def get_full_dispenser_status(self, device_id: int) -> List[Dict[str, Any]]:
        """
        Returns enriched dispenser status for all compartments of a given device.

        Each item includes:
        - compartment_id
        - medication_name
        - medication_id
        - quantity
        """
        compartments = self.get_dispenser_status(device_id)
        enriched_status = []

        for c in compartments:
            compartment_info = self.get_compartment_by_id(c["compartment_id"])
            enriched_status.append(
                {
                    "compartment_id": c["compartment_id"],
                    "medication_name": c["medication_name"],
                    "medication_id": compartment_info.get("medication_id"),
                    "quantity": c["quantity"],
                }
            )

        return enriched_status
