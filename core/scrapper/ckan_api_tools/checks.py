import requests


def test_status_show(api_url: str) -> bool:
    endpoint: str = f"{api_url.rstrip('/')}/api/3/action/status_show"
    
    try:
        response: requests.Response = requests.get(endpoint)
        response.raise_for_status()
        data: dict = response.json()
        return data.get("success") is True
    except requests.exceptions.RequestException:
        return False