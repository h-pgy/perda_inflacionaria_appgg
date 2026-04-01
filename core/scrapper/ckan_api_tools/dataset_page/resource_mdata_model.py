from pydantic import BaseModel
from typing import Optional

class ResourceMdataModel(BaseModel):
    id: str 
    title: str
    format: str
    description: Optional[str] = None

    class Config:
        populate_by_name = True