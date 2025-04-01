import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.user_manager import fastapi_users, current_active_user
from app.auth.schemas import UserRead, UserCreate, UserUpdate
from app.auth.backend import auth_backend
from app.service.links import links_router
from app.service.stats import stats_router

app = FastAPI(title="Link Shortener Service")

# CORS
origins = ["http://localhost",
           "http://localhost:8000",]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI Users
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Routers
app.include_router(links_router,prefix="/links", tags=["links"])
app.include_router(stats_router,prefix="/links", tags=["stats"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)