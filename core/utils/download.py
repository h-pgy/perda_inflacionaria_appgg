import os
import requests

def stream_download(url: str, full_path: str, chunk_size: int = 8192) -> str:
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(full_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Falha no download: o arquivo {full_path} não foi encontrado.")
        
    if not os.path.isfile(full_path):
        raise OSError(f"O caminho {full_path} existe, mas não é um arquivo válido.")
    
    return os.path.abspath(full_path)