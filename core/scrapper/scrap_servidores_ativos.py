from .ckan_api_tools import TabularResource, DatasetPageScraper, ResourceMdataModel
from config import URL_DATASET_SERVIDORES_ATIVOS

class ScrapServidoresAtivos:

    def __init__(self, dataset_url:str=URL_DATASET_SERVIDORES_ATIVOS):
        self.dataset_url: str = dataset_url
        self.resource_pagE_scraper = DatasetPageScraper(dataset_url)
