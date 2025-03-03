import pathlib
from pathlib import Path
from environs import Env


env = Env()
env.read_env()


BASE_DIR: pathlib.Path = Path(env.str("BASE_DIR"))

CIAN_API_URL: str = env.str("CIAN_API_URL")
ACCESS_TOKEN = env.str("ACCESS_TOKEN")

LOGGING_LEVEL: int = env.int("LOGGING_LEVEL", 10)

USE_CACHE: bool = env.bool("USE_CACHE", False)

if USE_CACHE:
    CACHE_HOST: str = env.str("CACHE_HOST")
    CACHE_PORT: int = env.int("CACHE_PORT")
    CACHE_PASSWORD: str = env.str("CACHE_PASSWORD")
