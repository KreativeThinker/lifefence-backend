import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    database_url: str
    jwt_secret: str
    jwt_valid_duration: int
    encoding_algorithm: str


config = Config(
    database_url=os.getenv("DATABASE_URL", "sqlite:///app/app/database.db"),
    jwt_secret=os.getenv("JWT_SECRET", "secret"),
    jwt_valid_duration=12,
    encoding_algorithm="HS256",
)
