from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth_router import router as auth_router
from app.routers.user_router import router as user_router



API_PREFIX = "/api/v1"

app = FastAPI(
    title="FastAPI JWT UUID Role API",
    description="Reusable JWT authentication, refresh token, UUID IDs and role-based permissions",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "FastAPI API is running successfully",
    }


app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(user_router, prefix=API_PREFIX)