

def join_url(base_url, path) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"