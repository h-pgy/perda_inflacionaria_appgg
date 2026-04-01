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
        preseted_encoding = self.read_kwargs.get("encoding", None)
        if preseted_encoding is None:
            automatic_encoding = detect_file_encoding(self.fpath)
            self.read_kwargs['encoding'] = automatic_encoding
            return automatic_encoding
        return preseted_encoding
    
    def __read_tabular_data(self) -> pd.DataFrame:
        if self.format != "csv":
            return pd.read_excel(self.fpath, **self.read_kwargs)

        self.__solve_encoding()
        
        # Lista de encodings para tentativa em ordem de prioridade
        encodings_to_try = [
            self.read_kwargs.get('encoding'), 
            'cp1252', 
            'latin1'
        ]

        for encoding in encodings_to_try:
            if not encoding:
                continue
                
            self.read_kwargs['encoding'] = encoding
            try:
                return pd.read_csv(self.fpath, **self.read_kwargs)
            except (UnicodeDecodeError, TypeError) as e:
                last_error = e 
                continue

        # Se chegar aqui, nenhuma tentativa funcionou
        raise last_error
        
    
    @property
    def data(self) -> pd.DataFrame:
        if self.__data is None:
            if not os.path.exists(self.fpath):
                self.download(file_name=self.file_name, folder_path=self.folder_path)
            
            self.__data = self.__read_tabular_data()
                
        return self.__data