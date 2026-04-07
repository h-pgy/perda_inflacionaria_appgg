import requests
import re
import json
from typing import Optional
from datetime import datetime

class CalculadoraFatorInflacao:

    URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"

    INDICES = {
        'ipca' : 433,
        'inpc' : 188,
        'igp-m' : 189,
        'ipc-fipe' : 193
    }


    def __init__(self, indice:str='ipca', file_indices_memoizados:Optional[str]=None) -> None:
        '''Calcula o fator inflacionario de um período.O padrao é o IPCA'''
        self.indice_code = self.__get_indice_code(indice)
        self.url_base = self.__build_url_base(self.indice_code)

        self.file_indices_memoizados = file_indices_memoizados or 'indices_memoizados.json'

        self.__load_indices()


    def __load_indices(self)->None:
        try:
            with open(self.file_indices_memoizados, 'r') as f:
                self.INDICES_CALCULADOS = json.load(f)
        except FileNotFoundError:
            self.INDICES_CALCULADOS = {}


    def save_indices(self)->None:

        with open(self.file_indices_memoizados, 'w') as f:
            json.dump(self.INDICES_CALCULADOS, f, indent=4)
        

    def __get_indice_code(self, indice:str)->int:

        if indice not in self.INDICES:
            raise ValueError(f'Indice {indice} não disponível. Disponíveis: {self.INDICES.keys()}')
        
        return self.INDICES[indice]

    def __build_url_base(self, numero_indice:int)->str:

        return self.URL + f'.{numero_indice}/dados'

    def validar_datas(self, data_inicio, data_fim) -> tuple[datetime, datetime]:
        padrao = r"^\d{2}/\d{2}/\d{4}$"
        if not re.match(padrao, data_inicio) or not re.match(padrao, data_fim):
            raise ValueError("Formato de data inválido. Use DD/MM/AAAA.")
        
        try:
            d1 = datetime.strptime(data_inicio, "%d/%m/%Y")
            d2 = datetime.strptime(data_fim, "%d/%m/%Y")
        except ValueError:
            raise ValueError("Data inexistente informada.")

        if d1 > d2:
            raise ValueError("A data de início não pode ser posterior à data de fim.")
        
        hoje = datetime.today()
        if d1 > hoje or d2 > hoje:
            raise ValueError("As datas não podem estar no futuro.")
        
        return d1, d2

    def buscar_dados(self, data_inicio:datetime, data_fim:datetime):
        
        data_inicio, data_fim = self.validar_datas(data_inicio, data_fim)
        
        params = {
            "formato": "json",
            "dataInicial": data_inicio.strftime("%d/%m/%Y"),
            "dataFinal": data_fim.strftime("%d/%m/%Y")
        }
        
        try:
            response = requests.get(self.url_base, params=params)
            response.raise_for_status()
            dados = response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Erro na conexão com o Banco Central: {e}. {response.url}")

        if not dados:
            raise ValueError(f"Sem dados disponíveis para o período {data_inicio} a {data_fim}.")
        print(f'Dados obtidos com sucesso na URL: {response.url}')
        return dados

    def calcular_fator(self, data_inicio, data_fim):
        series_historica = self.buscar_dados(data_inicio, data_fim)
        
        fator = 1.0
        for registro in series_historica:
            variacao = float(registro['valor']) / 100
            fator *= (1 + variacao)
            
        return fator
    

    def __chave_indice(self, data_inicial:str, data_final:str)->str:

        return f'{data_inicial} :: {data_final}'
    
    def get_from_memory(self, data_inicial:str, data_final:str)->float|None:

        chave = self.__chave_indice(data_inicial, data_final)

        return self.INDICES_CALCULADOS.get(chave, None)
    
    def add_to_memory(self, data_inicial:str, data_final:str, fator:float)->None:

        chave = self.__chave_indice(data_inicial, data_final)

        self.INDICES_CALCULADOS[chave] = fator

    def get_indice_memoized(self, data_inicial:str, data_final:str)->float:

        fator_memoria = self.get_from_memory(data_inicial, data_final)
        if fator_memoria is not None:
            return fator_memoria
        
        fator_calculado = self.calcular_fator(data_inicial, data_final)
        self.add_to_memory(data_inicial, data_final, fator_calculado)
        return fator_calculado

    def __call__(self, data_inicial:str, data_final:str)->float:

        return self.get_indice_memoized(data_inicial, data_final)