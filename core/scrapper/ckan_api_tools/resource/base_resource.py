import requests
from typing import Any, Optional
from .checks import test_status_show
from core.utils.path import prepare_path
from core.utils.download import stream_download

class CKANResourceDownloader:
    def __init__(self, base_url: str, resource_id: str):
        self.base_url: str = base_url.rstrip("/")
        self.resource_id: str = resource_id
        self.resource_url: str = self.build_resource_url()
        self.__metadata: Optional[dict[str, Any]] = None
        
        if not test_status_show(self.base_url):
            raise ConnectionError(f"A API em {self.base_url} não está respondendo corretamente.")

    def build_resource_url(self) -> str:
        return f"{self.base_url}/api/3/action/resource_show?id={self.resource_id}"

    def fetch_resource_metadata(self) -> dict[str, Any]:
        response: requests.Response = requests.get(self.resource_url)
        response.raise_for_status()
        
        data: dict[str, Any] = response.json()
        
        if not data.get("success"):
            raise Exception(f"A API retornou sucesso falso para o recurso {self.resource_id}.")
            
        result: Optional[dict[str, Any]] = data.get("result")
        if result is None:
            raise ValueError(f"A API retornou sucesso, mas o campo 'result' está vazio para o recurso {self.resource_id}.")
            
        return result

    @property
    def metadata(self) -> dict[str, Any]:
        if self.__metadata is None:
            self.__metadata = self.fetch_resource_metadata()
        return self.__metadata
    
    @property
    def format(self)->str:
        resource_format: Optional[str] = self.metadata.get("format")
        
        if not resource_format:
            raise ValueError(f"O atributo 'format' está vazio ou não existe nos metadados do recurso {self.resource_id}.")
            
        return resource_format.lower().strip()

    
    @property
    def download_url(self) -> str:
        url: Optional[str] = self.metadata.get("url")
        
        if not url:
            raise ValueError(f"O atributo 'url' de download está vazio ou não existe nos metadados do recurso {self.resource_id}.")
            
        if not url.lower().endswith(self.format):
            raise ValueError(f"A URL de download não termina com o formato esperado: {self.format}")
            
        return url


    def download(self, file_name: str, folder_path: str = ".") -> str:
        if not file_name.lower().endswith(f".{self.format}"):
            raise ValueError(f"O nome do arquivo '{file_name}' deve terminar com a extensão '.{self.format}' correspondente ao recurso.")
        
        full_path: str = prepare_path(folder_path, file_name)
        
        stream_download(self.download_url, full_path)
        
        return full_path

    