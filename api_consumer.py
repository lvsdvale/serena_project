from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import requests

from utils import load_json_from_file, save_json_to_file

BASE_URL = "https://serena-api-mn6f.onrender.com"


class SerenaAPIClient:
    def __init__(self, email: str, password: str, timeout: float = 15.0) -> None:
        self.email = email
        self.password = password
        self.timeout = timeout
        self.token: Optional[str] = None
        self.headers: Dict[str, str] = {}
        self.login()

    def login(self) -> None:
        url = f"{BASE_URL}/auth/login"
        payload = {
            "grant_type": "password",
            "username": self.email,
            "password": self.password,
        }
        try:
            response = requests.post(url, data=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("access_token")
            if not self.token:
                raise ValueError("No access_token found in login response.")
            token_type = data.get("token_type", "Bearer")
            self.headers = {"Authorization": f"{token_type} {self.token}"}
        except requests.exceptions.Timeout:
            print("[ERROR] Timeout during authentication (login).")
        except Exception as e:
            print(f"[ERROR] Login failed: {e}")

    def _auto_reauth(cache_file: Optional[str] = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                try:
                    result = func(self, *args, **kwargs)
                    if result is not None and cache_file:
                        save_json_to_file(result, cache_file)
                    return result
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 401:
                        self.login()
                        try:
                            result = func(self, *args, **kwargs)
                            if result is not None and cache_file:
                                save_json_to_file(result, cache_file)
                            return result
                        except Exception as e2:
                            print(f"[ERROR] Failed after re-authentication: {e2}")
                            if cache_file:
                                print(f"[WARNING] Loading cache from {cache_file}")
                                return load_json_from_file(cache_file)
                            return None
                    raise
                except requests.exceptions.Timeout:
                    print(f"[ERROR] Timeout in function '{func.__name__}'.")
                    if cache_file:
                        print(f"[WARNING] Loading cache from {cache_file}")
                        return load_json_from_file(cache_file)
                    return None
                except Exception as e:
                    print(f"[ERROR] Exception in function '{func.__name__}': {e}")
                    if cache_file:
                        print(f"[WARNING] Loading cache from {cache_file}")
                        return load_json_from_file(cache_file)
                    return None

            return wrapper

        return decorator

    @_auto_reauth(cache_file="medications_cache.json")
    def get_medication_list(self) -> Optional[List[Dict[str, Any]]]:
        url = f"{BASE_URL}/medications"
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    @_auto_reauth(cache_file="dispenser_status_cache.json")
    def get_dispenser_status(self, device_id: int) -> Optional[List[Dict[str, Any]]]:
        url = f"{BASE_URL}/dispenser/by_device/{device_id}"
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    @_auto_reauth(cache_file="prescriptions_cache.json")
    def get_valid_prescriptions(self, device_id: int) -> Optional[List[Dict[str, Any]]]:
        url = f"{BASE_URL}/prescriptions/by_device/{device_id}"
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    @_auto_reauth(cache_file=None)
    def update_compartment_amount(
        self, compartment_id: str, medication_id: str, quantity: int
    ) -> Optional[Dict[str, Any]]:
        url = f"{BASE_URL}/compartment/{compartment_id}"
        payload = {"quantity": quantity, "medication_id": medication_id}
        response = requests.patch(
            url, json=payload, headers=self.headers, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    @_auto_reauth(cache_file=None)
    def create_symptom_by_device(
        self,
        device_id: int,
        senior_id: int,
        symptom_name: str,
        description: str,
        pain_level: int,
    ) -> Optional[Dict[str, Any]]:
        url = f"{BASE_URL}/symptoms/by_device/{device_id}"
        payload = {
            "name": symptom_name,
            "description": description,
            "pain_level": pain_level,
            "senior_id": str(senior_id),
        }
        response = requests.post(
            url, json=payload, headers=self.headers, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    @_auto_reauth(cache_file=None)
    def get_senior_id_by_device(self, device_id: int) -> Optional[Dict[str, Any]]:
        url = f"{BASE_URL}/senior/by_device/{device_id}"
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    @_auto_reauth(cache_file="get_compartment_by_id_cache.json")
    def get_compartment_by_id(self, compartment_id: str) -> Optional[Dict[str, Any]]:
        url = f"{BASE_URL}/compartment/{compartment_id}"
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    @_auto_reauth(cache_file="enriched_prescriptions_cache.json")
    def get_enriched_prescriptions(
        self, device_id: int
    ) -> Optional[List[Dict[str, Any]]]:
        prescriptions = self.get_valid_prescriptions(device_id)
        medications = self.get_medication_list()

        if prescriptions is None or medications is None:
            print("[WARNING] Using cached enriched prescriptions due to API failure.")
            return load_json_from_file("enriched_prescriptions_cache.json")

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

    @_auto_reauth(cache_file="full_dispenser_status_cache.json")
    def get_full_dispenser_status(
        self, device_id: int
    ) -> Optional[List[Dict[str, Any]]]:
        compartments = self.get_dispenser_status(device_id)
        if compartments is None:
            print(f"[WARNING] Using cached full dispenser status due to API failure.")
            return load_json_from_file("full_dispenser_status_cache.json")

        enriched_status = []
        for c in compartments:
            compartment_info = self.get_compartment_by_id(c["compartment_id"])
            if compartment_info is None:
                continue
            enriched_status.append(
                {
                    "compartment_id": c["compartment_id"],
                    "medication_name": c["medication_name"],
                    "medication_id": compartment_info.get("medication_id"),
                    "quantity": c["quantity"],
                }
            )

        save_json_to_file(enriched_status, "full_dispenser_status_cache.json")
        return enriched_status
