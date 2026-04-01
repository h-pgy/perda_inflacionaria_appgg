from core.utils.url import join_url
from core.utils.path import prepare_path, build_folder_if_not_exists

BASE_URL_CKAN='https://dados.prefeitura.sp.gov.br/'
URL_DATASET_SERVIDORES_ATIVOS=join_url(BASE_URL_CKAN, 'dataset/servidores-ativos-da-prefeitura')
DATA_FOLDER=build_folder_if_not_exists('data')

