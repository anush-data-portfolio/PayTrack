import requests
from config import Config
from paytrack.models.schema import User

class Auth:
    def __init__(self) -> None:
        """
        Initialize Auth object.

        Attributes:
        - payload (dict): Payload for authentication containing 'username' and 'password'.
        - session (requests.Session): Session object for making authenticated requests.
        - config (Config): Configuration object.
        """
        self.payload = {'username': None, 'password': None}
        self.session = requests.Session()
        self.config = Config()

    def __login(self) -> None:
        """
        Login to the API.

        Raises:
        - Exception: If an error occurs during login.
        """
        try:
            print("Logging in")
            response = self.session.post(self.config.AUTH_API, data=self.payload)
            print(response)
            response.raise_for_status()
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

    def get_session(self, user: User) -> requests.Session:
        """
        Return the authenticated session.

        Parameters:
        - user (User): User object containing username and password.

        Returns:
        requests.Session: Authenticated session.
        """
        print("Authenticating...")
        self.payload['username'] = user.username
        self.payload['password'] = user.password
        print("Logging in")
        self.__login()
        print("Authentication successful")
        return self.session
