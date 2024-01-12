from dotenv import load_dotenv
import os

class Config:
    def __init__(self) -> None:
        """
        Initialize Config object.

        Loads environment variables from .env.local and sets up configuration attributes.

        Attributes:
        - DEBUG (bool): Debug mode indicator.
        - SECRET_KEY (str): Secret key for the application.
        - API_URL (str): Base API URL.
        - AUTH_API (str): Authentication API URL.
        - USERNAME (str): User's username.
        - PASSWORD (str): User's password.
        - TIMECARD (str): Timecard API URL.
        - POSTGRES_USER (str): PostgreSQL database user.
        - POSTGRES_PASSWORD (str): PostgreSQL database password.
        - POSTGRES_HOST (str): PostgreSQL database host.
        - POSTGRES_PORT (str): PostgreSQL database port.
        - POSTGRES_DB (str): PostgreSQL database name.
        - DATABASE_URI (str): Connection URI for PostgreSQL database.
        - NOTION_API_KEY (str): Notion API key.
        - NOTION_PAGE_ID (str): Notion page ID.
        """
        # Load .env.local
        env = load_dotenv()
        print(env)  # This line prints the loaded environment variables to the console

        self.DEBUG = True
        self.SECRET_KEY = os.environ.get('SECRET')
        self.API_URL = os.environ.get('API_URL')
        self.AUTH_API = self.API_URL + os.environ.get('AUTH')
        self.USERNAME = os.environ.get('USERNAME')
        self.PASSWORD = os.environ.get('PASSWORD')
        self.TIMECARD = self.API_URL + os.environ.get('TIMECARD')

        # PostgreSQL config
        self.POSTGRES_USER = os.environ.get('PAYTRACK_USER')
        self.POSTGRES_PASSWORD = os.environ.get('PAYTRACK_PASSWORD')
        self.POSTGRES_HOST = os.environ.get('PAYTRACK_HOST')
        self.POSTGRES_PORT = os.environ.get('PAYTRACK_PORT')
        self.POSTGRES_DB = os.environ.get('PAYTRACK_DB')
        self.DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

        # Notion config
        self.NOTION_API_KEY = os.environ.get('NOTION_API_KEY')
        self.NOTION_PAGE_ID = os.environ.get('NOTION_PAGE_ID')
