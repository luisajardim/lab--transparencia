import json
import os
import requests

# Obtém o diretório do script para encontrar config.json
script_dir = os.path.dirname(os.path.abspath(__file__))

def ler_configuracao(origem: str):
    if origem == "local":
        config_path = os.path.join(script_dir, "config.json")
        with open(config_path) as f:
            return json.load(f)
    elif origem == "http":
        resp = requests.get("http://config-srv/config")
        return resp.json()
    elif origem == "s3":
        raise NotImplementedError("S3 não configurado neste lab")

try:
    cfg = ler_configuracao("local")
    print("Configuração carregada:", cfg)
except FileNotFoundError:
    print("config.json não encontrado — crie um para testar")