from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.scoring import router as scoring_router

app = FastAPI(title="CareerWatch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scoring_router)

@app.get("/health")
def health():
    return {"status": "ok"}
