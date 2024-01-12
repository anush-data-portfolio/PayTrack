import requests
from config import Config


class Auth:
    # cookie based authentication
    def __init__(self) -> None:
        """Initialize Auth object"""
        self.payload = {'username': None,
                        'password': None}
        self.session = requests.Session()
        self.config = Config()
    
    def __login(self) -> None:
        """Login to the API"""
        try:
            print("Logging in")
            re = self.session.post(self.config.AUTH_API, data=self.payload)
            print(re)
            re.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
            raise Exception("Error logging in")
        except requests.exceptions.ConnectionError as e:
            print(e)
            raise Exception("Error connecting to API")
        except requests.exceptions.Timeout as e:
            print(e)
            raise Exception("Connection timed out")
        except requests.exceptions.RequestException as e:
            print(e)
            raise Exception("Error logging in")
        print("Successfully logged in")

    
    def get_session(self, username: str, password: str) -> requests.Session:
        """Return the session"""
        print("Authenticating...")
        self.payload['username'] = username
        self.payload['password'] = password
        print("Logging in")
        try:
            self.__login()
            print("Authentication successful")
            return self.session
        except Exception as e:
            print(e)
            return None

        
