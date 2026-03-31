from .base_resource import CkanResource
import pandas as pd
import os
from core.utils.download import detect_file_encoding
from typing import Optional, Any

class TabularResource(CkanResource):
    ALLOWED_FORMATS: list[str] = ["csv", "xls", "xlsx"]

    def __init__(
            self, 
            base_url: str, 
            resource_id: str, 
            file_name: str, 
            folder_path: str = ".", 
            read_kwargs: Optional[dict[str, Any]] = None
        ) -> None:

        super().__init__(base_url, resource_id)
        
        if self.format not in self.ALLOWED_FORMATS:
            raise RuntimeError(
                f"O recurso {self.resource_id} possui o formato '{self.format}'. "
                f"A classe TabularResource aceita apenas: {', '.join(self.ALLOWED_FORMATS)}."
            )
        
        self.file_name: str = file_name
        self.folder_path: str = folder_path
        self.read_kwargs: dict[str, Any] = read_kwargs or {}
        self.__data: Optional[pd.DataFrame] = None

    @property
    def fpath(self) -> str:
        return os.path.join(self.folder_path, self.file_name)
    
    def __solve_encoding(self) -> str:
        return self.read_kwargs.pop("encoding", None) or detect_file_encoding(self.fpath)
    
    def __read_tabular_data(self) -> pd.DataFrame:
        if self.format == "csv":
            encoding = self.__solve_encoding()
            return pd.read_csv(self.fpath, encoding=encoding, **self.read_kwargs)
        return pd.read_excel(self.fpath, **self.read_kwargs)
    
    @property
    def data(self) -> pd.DataFrame:
        if self.__data is None:
            if not os.path.exists(self.fpath):
                self.download(file_name=self.file_name, folder_path=self.folder_path)
            
            self.__data = self.__read_tabular_data()
                
        return self.__data