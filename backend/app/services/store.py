import json
from pathlib import Path
from ..config import DATA

def _read(name):
    with open(DATA/name, encoding='utf-8') as f: return json.load(f)

def cells(): return _read('cell_database.json')
def materials(): return _read('materials.json')
def tissues(): return _read('tissue_catalog.json')
