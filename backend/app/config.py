from pydantic import BaseModel
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

class Settings(BaseModel):
    app_name: str = 'TissuePilot'
    version: str = '1.8.0'
    pubmed_email: str | None = None
    semantic_scholar_api_key: str | None = None

settings = Settings()
