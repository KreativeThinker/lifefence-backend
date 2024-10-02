from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

import app.api.routes as routes
import app.models
from app.config import config


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await Tortoise.init(db_url=config.database_url, modules={"models": ["app.models"]})
    await Tortoise.generate_schemas()

    yield
    await Tortoise.close_connections()


app = FastAPI(
    title="LifeFence",
    lifespan=app_lifespan,
)
app.include_router(routes.router)

origins = ["http://ctf.lugvitc.org", "*"]  # Remove '*' once out of deployment

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
