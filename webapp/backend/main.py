from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.gaps import router as gaps_router
from routers.jobs import router as jobs_router
from routers.scoring import router as scoring_router
from routers.user import router as user_router

app = FastAPI(title="CareerWatch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gaps_router)
app.include_router(jobs_router)
app.include_router(scoring_router)
app.include_router(user_router)

@app.get("/health")
def health():
    return {"status": "ok"}
