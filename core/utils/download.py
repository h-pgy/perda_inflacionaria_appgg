import os
import requests
import chardet


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


def detect_file_encoding(file_path: str, sample_size: int = 10000) -> str:
    with open(file_path, 'rb') as f:
        raw_data = f.read(sample_size)
        
        if not raw_data:
            return "utf-8"
            
        result: dict[str, Any] = chardet.detect(raw_data)
        encoding: str = result.get("encoding", "utf-8")
        confidence: float = result.get("confidence", 0.0)
        
        if encoding is None or confidence < 0.5:
            return "utf-8"
            
        return encoding.lower()