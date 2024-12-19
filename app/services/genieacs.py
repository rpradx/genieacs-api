import json
import logging
import requests
from typing import List, Dict, Optional
from fastapi import HTTPException
from app.config import GENIEACS_URL, MAPPING_FILE, REQUEST_TIMEOUT

class GenieACS:
    """API wrapper para interação com o servidor GenieACS NBI."""

    def __init__(self, base_url: str, mapping: Dict):
        self.base_url = base_url
        self.session = requests.Session()
        self.mapping = mapping
        self.logger = logging.getLogger(__name__)

    def _request(self, method: str, endpoint: str, params: Dict = None, data=None) -> Optional[Dict]:
        url = f"{self.base_url}/{endpoint}"
        self.logger.info(f"Making {method} request to URL: {url} with params: {params}, data: {data}")
        try:
            response = self.session.request(method=method, url=url, params=params, json=data, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error in request: {e}")
            raise HTTPException(status_code=500, detail=f"Erro na requisição: {e}")

        if response.text.strip():
            try:
                return response.json()
            except json.JSONDecodeError:
                return None
        return None

    def get(self, endpoint: str, params: Dict = None):
        return self._request("GET", endpoint, params=params)

    def list_devices(self, query: Dict = None) -> List[Dict]:
        params = {"query": json.dumps(query)} if query else {}
        devices = self.get("devices", params=params)
        return devices if devices else []

    def get_device_by_id(self, device_id: str) -> Optional[Dict]:
        query = {"_id": device_id}
        devices = self.list_devices(query=query)
        return devices[0] if devices else None

    def extract_mapped_parameters(self, device_data: Dict) -> Dict:
        """Extrai os parâmetros mapeados do dispositivo."""
        extracted = {}
        for path, name in self.mapping.items():
            pattern = path.replace("{i}", "*").replace("<VENDOR>", "*")
            pattern_keys = pattern.split('.')
            matches = self.find_matching_paths(device_data, pattern_keys)
            for match in matches:
                value = self.get_value_by_path(device_data, match)
                if value is not None:
                    if name in extracted:
                        if not isinstance(extracted[name], list):
                            extracted[name] = [extracted[name]]
                        extracted[name].append(value)
                    else:
                        extracted[name] = value
        return extracted

    def find_matching_paths(self, data: Dict, pattern: List[str], current_path: List[str] = []) -> List[List[str]]:
        if not pattern:
            return [current_path]
        key = pattern[0]
        remaining = pattern[1:]
        paths = []
        if key == "*":
            if isinstance(data, dict):
                for k in data.keys():
                    paths.extend(self.find_matching_paths(data[k], remaining, current_path + [k]))
            elif isinstance(data, list):
                for idx, item in enumerate(data):
                    paths.extend(self.find_matching_paths(item, remaining, current_path + [str(idx)]))
        else:
            if isinstance(data, dict) and key in data:
                paths.extend(self.find_matching_paths(data[key], remaining, current_path + [key]))
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and key in item:
                        paths.extend(self.find_matching_paths(item[key], remaining, current_path + [key]))
        return paths

    def get_value_by_path(self, data: Dict, path: List[str]) -> Optional[str]:
        for key in path:
            if isinstance(data, dict):
                data = data.get(key)
            elif isinstance(data, list):
                try:
                    index = int(key)
                    data = data[index]
                except (ValueError, IndexError):
                    return None
            else:
                return None
            if data is None:
                return None
        if isinstance(data, dict) and "_value" in data:
            return data["_value"]
        return data

with open(MAPPING_FILE, "r") as f:
    PARAMETER_MAP = json.load(f)

genieacs = GenieACS(base_url=GENIEACS_URL, mapping=PARAMETER_MAP)
