from dotenv import load_dotenv
import os



class Config:
    def __init__(self) -> None:
        env = load_dotenv()

        """Initialize Config object"""
        self.DEBUG = True
        self.SECRET_KEY = os.environ.get('SECRET')
        self.POSTGRES_USER = os.environ.get('PAYTRACK_USER')
        self.POSTGRES_PASSWORD = os.environ.get('PAYTRACK_PASSWORD')
        self.POSTGRES_HOST = os.environ.get('PAYTRACK_HOST')
        self.POSTGRES_PORT = os.environ.get('PAYTRACK_PORT')
        self.POSTGRES_DB = os.environ.get('PAYTRACK_DB')
        # self.DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        self.DATABASE_URI = f'sqlite:///test.db'
