from datetime import timedelta
from authx import AuthXConfig, AuthX
import os
from dotenv import load_dotenv


load_dotenv()  # Загружаем переменные из .env


config = AuthXConfig()
config.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
config.JWT_ACCESS_COOKIE_NAME = os.getenv("JWT_ACCESS_COOKIE_NAME")
config.JWT_TOKEN_LOCATION = ["cookies"]

config.JWT_COOKIE_CSRF_PROTECT = False
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")))

security = AuthX(config=config)
