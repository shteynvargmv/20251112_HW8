"""Конфигурация для JWT токена."""

from pathlib import Path

from authx import AuthX, AuthXConfig
from dotenv import dotenv_values

env_path = Path(__file__).parent/ '.env'
dotenv = dotenv_values(env_path)
jwt_secret_key=dotenv['JWT_SECRET_KEY']
jwt_access_cookie_name = dotenv['JWT_ACCESS_COOKIE_NAME']

config = AuthXConfig(
    JWT_SECRET_KEY=jwt_secret_key,
    JWT_ACCESS_COOKIE_NAME=jwt_access_cookie_name,
    JWT_TOKEN_LOCATION=['cookies']
)

security = AuthX(config=config)
