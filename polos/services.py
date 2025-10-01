import requests
from time import sleep

def get_coordinates_from_address(endereco, cidade, estado):
    """
    Obtém as coordenadas geográficas (latitude e longitude) de um endereço usando OpenStreetMap Nominatim.
    Inclui um delay de 1 segundo para respeitar os limites da API.
    """
    try:
        # Formato do endereço para busca
        query = f"{endereco}, {cidade}, {estado}, Brazil"
        
        # Faz a requisição para a API do Nominatim
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "limit": 1,
            "countrycodes": "br"
        }
        
        headers = {
            "User-Agent": "UNIVESP_Polos/1.0"
        }
        
        # Delay para respeitar os limites da API
        sleep(1)
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if data:
            return {
                'latitude': float(data[0]['lat']),
                'longitude': float(data[0]['lon'])
            }
        return None
        
    except Exception as e:
        print(f"Erro ao obter coordenadas: {str(e)}")
        return None

def get_address_from_cep(cep):
    """
    Obtém o endereço a partir de um CEP usando a API OpenCEP.
    """
    try:
        cep = cep.replace("-", "").replace(".", "")
        response = requests.get(f'https://opencep.com/v1/{cep}')
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        print(f"Erro ao buscar CEP: {str(e)}")
        return None

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calcula a distância em quilômetros entre duas coordenadas usando a fórmula de Haversine.
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Raio da Terra em km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance
