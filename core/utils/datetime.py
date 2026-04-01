import re
from datetime import datetime

def extract_date_from_ptbr_description(description: str) -> datetime:
    months_map: dict[str, int] = {
        "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
        "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
        "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
    }
    
    pattern: str = r"(\w+)\s+de\s+(\d{4})"
    match = re.search(pattern, description.lower())
    
    if not match:
        raise ValueError(f"Não foi possível encontrar uma data no formato 'mês de ano' na descrição: {description}")
        
    month_str, year_str = match.groups()
    
    if month_str not in months_map:
        raise ValueError(f"Mês '{month_str}' não reconhecido na descrição: {description}")
        
    return datetime(year=int(year_str), month=months_map[month_str], day=1)