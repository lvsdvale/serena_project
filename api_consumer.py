import requests
from typing import Dict, Any, List, Optional, Callable
from functools import wraps

BASE_URL = "https://serena-api-mn6f.onrender.com"


class SerenaAPIClient:
    """
    API client for interacting with the Serena system.
    Handles authentication, automatic token renewal, and provides access to key routes.
    """

    def __init__(self, email: str, password: str) -> None:
        """
        Initializes the client and performs initial login.

        Args:
            email (str): The user's email address.
            password (str): The user's password.
        """
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
            "password": self.password
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
        Decorator that retries the API call with re-authentication if token is expired.

        Args:
            func (Callable): The API method to wrap.

        Returns:
            Callable: The wrapped function with retry logic.
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
        Gets medication list.

        Returns:
            List[Dict[str, Any]]: A list of compartments with name, amount, and compartment_id.
        """
        url = f"{BASE_URL}/medications"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()


    @_auto_reauth
    def get_dispenser_status(self, device_id: int) -> List[Dict[str, Any]]:
        """
        Gets the status of the 14 compartments in the dispenser.

        Args:
            device_id (int): The ID of the device.

        Returns:
            List[Dict[str, Any]]: A list of compartments with name, amount, and compartment_id.
        """
        url = f"{BASE_URL}/dispenser/by_device/{device_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @_auto_reauth
    def get_valid_prescriptions(self, device_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves valid prescriptions for the senior linked to a device.

        Args:
            device_id (int): The ID of the device.

        Returns:
            List[Dict[str, Any]]: A list of valid prescription records.
        """
        url = f"{BASE_URL}/prescriptions/by_device/{device_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @_auto_reauth
    def update_compartment_amount(self, compartment_id: int, quantity: int) -> Dict[str, Any]:
        """
        Updates the amount of medication in a specific compartment.

        Args:
            compartment_id (int): The ID of the compartment.
            new_amount (int): The new amount of medication.

        Returns:
            Dict[str, Any]: The updated compartment data.
        """
        url = f"{BASE_URL}/compartment/{compartment_id}"
        payload = {"quantity": quantity}
        response = requests.patch(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @_auto_reauth
    def create_symptom(self, senior_id: int, symptom_name: str, description: str) -> Dict[str, Any]:
        """
        Records a new symptom reported by a senior.

        Args:
            senior_id (int): The ID of the senior.
            symptom_name (str): The name of the symptom.
            description (str): A description of the symptom.

        Returns:
            Dict[str, Any]: The created symptom record.
        """
        url = f"{BASE_URL}/symptoms/"
        payload = {
            "senior_id": senior_id,
            "name": symptom_name,
            "description": description
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

    @_auto_reauth
    def get_senior_id_by_device(self, device_id: int) -> Dict[str, Any]:
        """
        Retrieves the senior ID linked to a device.

        Args:
            device_id (int): The ID of the device.

        Returns:
            Dict[str, Any]: A dictionary containing the senior_id.
        """
        url = f"{BASE_URL}/senior/by_device/{device_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
