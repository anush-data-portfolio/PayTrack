from dotenv import load_dotenv
import os


load_dotenv()


class Config:
    API_URL = os.getenv("API_URL")
    AUTH_API = API_URL + "/login"