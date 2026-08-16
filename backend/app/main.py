from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.api import router

app = FastAPI(title="TissuePilot", version="1.8.0", description="Evidence-aware tissue engineering research decision support")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

@app.get('/api/health')
def health():
    return {'status':'ok','version':'1.8.0','scientific_mode':True}
