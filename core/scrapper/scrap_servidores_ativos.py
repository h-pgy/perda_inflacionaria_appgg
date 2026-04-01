from .ckan_api_tools import TabularResource, DatasetPageScraper, ResourceMdataModel
from core.utils.datetime import extract_date_from_ptbr_description
from typing import List, Generator
from config import URL_DATASET_SERVIDORES_ATIVOS, BASE_URL_CKAN, DATA_FOLDER

class ScrapServidoresAtivos:

    def __init__(self, base_api_url:str=BASE_URL_CKAN, dataset_url:str=URL_DATASET_SERVIDORES_ATIVOS, data_folder:str=DATA_FOLDER):
        self.base_api_url = base_api_url
        self.dataset_url: str = dataset_url
        self.resource_page_scraper = DatasetPageScraper(dataset_url)
        self.data_folder= data_folder

    def is_dataset_servidores_resource(self, resource:ResourceMdataModel)->bool:

        title = resource.title.lower().strip()
        check = title =='base de dados - funcionalismo'
        return check
    
    def is_csv_resource(self, resource:ResourceMdataModel)->bool:

        format = resource.format.lower().strip()
        check = format == 'csv'
        return check
    
    def extract_reference_date(self, resource:ResourceMdataModel)->datetime:

        description = resource.description or ''
        date = extract_date_from_ptbr_description(description)
        return date
    
    def is_after_2016(self, resource:ResourceMdataModel)->bool:

        reference_date = self.extract_reference_date(resource)
        if reference_date is None:
            return False
        check = reference_date.year >= 2016
        return check
    
    def resource_selected(self, resource:ResourceMdataModel)->bool:

        checks = [
            self.is_dataset_servidores_resource(resource),
            self.is_csv_resource(resource),
            self.is_after_2016(resource)
        ]
        return all(checks)
    
    def filter_resources(self, resource_list:List[ResourceMdataModel])->List[ResourceMdataModel]:

        selected_resources = [resource for resource in resource_list if self.resource_selected(resource)]
        return selected_resources
    
    def build_fname(self, resource:ResourceMdataModel)->str:

        reference_date = self.extract_reference_date(resource)
        fname = f'servidores_ativos_{reference_date.strftime("%Y_%m")}.csv'
        return fname
    
    def build_tabular_resource(self, resource:ResourceMdataModel)->TabularResource:

        resource_id = resource.id
        fname= self.build_fname(resource)
        tabular_resource = TabularResource(base_url=self.base_api_url, 
                                           resource_id=resource_id, file_name=fname, folder_path=self.data_folder,
                                           read_kwargs={'sep' : ';'})

        setattr(tabular_resource, 'reference_date', self.extract_reference_date(resource))

        return tabular_resource

    def yield_tabular_resources(self)->Generator[TabularResource, None, None]:

        resource_list = self.resource_page_scraper()
        selected_resources = self.filter_resources(resource_list)
        for resource in selected_resources:
            yield self.build_tabular_resource(resource)

    def __call__(self)->Generator[TabularResource, None, None]:
        return self.yield_tabular_resources()