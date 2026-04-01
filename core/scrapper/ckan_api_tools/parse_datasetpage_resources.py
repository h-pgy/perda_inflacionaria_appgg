import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from typing import Any, Optional

class ResourceModel(BaseModel):
    id: str 
    title: str
    format: str
    description: Optional[str] = None

    class Config:
        populate_by_name = True

class CkanScraper:
    def __init__(self, dataset_url: str):
        self.dataset_url: str = dataset_url
        self.__html: Optional[str] = None
        self.__soup: Optional[BeautifulSoup] = None

    def fetch_html(self) -> str:
        response = requests.get(self.dataset_url)
        response.raise_for_status()
        self.__html = response.text
        return self.__html

    def make_soup(self) -> BeautifulSoup:
        if self.__html is None:
            self.fetch_html()
        self.__soup = BeautifulSoup(self.__html, "html.parser")
        return self.__soup

    def get_resource_list_items(self) -> list[Any]:
        if self.__soup is None:
            self.make_soup()
        
        resource_list = self.__soup.find("ul", class_="resource-list")
        if not resource_list:
            raise RuntimeError(f"Não foi possível encontrar a lista de recursos em {self.dataset_url}")
            
        return resource_list.find_all("li", class_="resource-item")

    def __extract_id(self, item: Any) -> str:
        resource_id = item.get("data-id")
        if not resource_id:
            raise ValueError(f"Item da lista não possui 'data-id'. HTML interno: {item.decode_contents()}")
        return resource_id

    def __extract_title(self, item: Any) -> str:
        heading_anchor = item.find("a", class_="heading")
        if not heading_anchor or not heading_anchor.get("title"):
            raise ValueError(f"Recurso sem título no atributo 'title'. HTML interno: {item.decode_contents()}")
        return heading_anchor.get("title")

    def __extract_format(self, item: Any) -> str:
        format_span = item.find("span", class_="format-label")
        if not format_span:
            raise ValueError(f"Recurso sem a tag de formato 'format-label'. HTML interno: {item.decode_contents()}")
        
        data_format = format_span.get("data-format")
        if not data_format:
            raise ValueError(f"O atributo 'data-format' está vazio ou ausente. HTML interno: {item.decode_contents()}")
        return data_format

    def __extract_description(self, item: Any) -> str:
        description_tag = item.find("p", class_="description")
        if not description_tag:
            return ""
        
        return description_tag.get_text(strip=True)

    def parse_resource_item(self, item: Any) -> ResourceModel:
        return ResourceModel(
            id=self.__extract_id(item),
            title=self.__extract_title(item),
            format=self.__extract_format(item),
            description=self.__extract_description(item)
        )

    def run_pipeline(self) -> list[dict[str, Any]]:
        items = self.get_resource_list_items()
        return [self.parse_resource_item(item).model_dump() for item in items]

    def __call__(self) -> list[dict[str, Any]]:
        return self.run_pipeline()