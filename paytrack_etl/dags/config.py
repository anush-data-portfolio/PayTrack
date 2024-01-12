from dotenv import load_dotenv
import os



class Config:
    def __init__(self) -> None:
        #load .env.local
        env = load_dotenv()
        print(env)

        """Initialize Config object"""
        self.DEBUG = True
        self.SECRET_KEY = os.environ.get('SECRET')
        self.API_URL = os.environ.get('API_URL')
        self.AUTH_API = self.API_URL + os.environ.get('AUTH')
        self.USERNAME = os.environ.get('USERNAME')
        self.PASSWORD = os.environ.get('PASSWORD')
        self.TIMECARD = self.API_URL + os.environ.get('TIMECARD')
        # postgres config
        self.POSTGRES_USER = os.environ.get('PAYTRACK_USER')
        self.POSTGRES_PASSWORD = os.environ.get('PAYTRACK_PASSWORD')
        self.POSTGRES_HOST = os.environ.get('PAYTRACK_HOST')
        self.POSTGRES_PORT = os.environ.get('PAYTRACK_PORT')
        self.POSTGRES_DB = os.environ.get('PAYTRACK_DB')
        self.DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        # self.DATABASE_URI = f'sqlite:///test.db'
        # notion config
        self.NOTION_API_KEY = os.environ.get('NOTION_API_KEY')
        self.NOTION_PAGE_ID = os.environ.get('NOTION_PAGE_ID')
