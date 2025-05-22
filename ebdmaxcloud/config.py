from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
    USER_AGENT = os.getenv("USER_AGENT", "your_default_user_agent")
    COOKIE_TEMP = os.getenv("COOKIE_TEMP")
    COOKIE_IDENTITY = os.getenv("COOKIE_IDENTITY")
    COOKIE_MAXIMADADOS = os.getenv("COOKIE_MAXIMADADOS")
    MENU_CLIENT = os.getenv("MENU_CLIENT")
    DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///site.db")
    DEBUG = os.getenv("DEBUG", "False") == "True"