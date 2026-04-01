import os

def build_folder_if_not_exists(folder_path: str) -> str:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return os.path.abspath(folder_path)

def prepare_path(folder_path: str, file_name: str) -> str:
    
    folder_path = build_folder_if_not_exists(folder_path)
    
    full_path = os.path.join(folder_path, file_name)
    return os.path.abspath(full_path)