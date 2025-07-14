import requests
from typing import Optional

def create_access_key(api_url: str, name: str = None) -> Optional[dict]:
    """Создать новый ключ доступа через Outline Manager API с именем."""
    try:
        data = {"name": name} if name else None
        resp = requests.post(f"{api_url}/access-keys", json=data, timeout=10, verify=False)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Ошибка при создании ключа: {e}")
        return None

def get_access_keys(api_url: str) -> Optional[list]:
    """Получить список всех ключей на сервере."""
    try:
        resp = requests.get(f"{api_url}/access-keys", timeout=10, verify=False)
        resp.raise_for_status()
        return resp.json().get('accessKeys', [])
    except Exception as e:
        print(f"Ошибка при получении ключей: {e}")
        return None

def delete_access_key(api_url: str, access_key_id: str) -> bool:
    """Удалить ключ доступа через Outline Manager API."""
    try:
        resp = requests.delete(f"{api_url}/access-keys/{access_key_id}", timeout=10, verify=False)
        return resp.status_code == 204
    except Exception as e:
        print(f"Ошибка при удалении ключа: {e}")
        return False 