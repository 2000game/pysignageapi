import requests
import json
from .const import PLAYER_UNAVAILABLE, SUCCESS
class PySignageAPI():
    def __init__(self, host, username, password, port):
        self.host = f"http://{username}:{password}@{host}:{port}/api"

    def _post_call(self, datapoint, body=None):
        try:
            r = requests.post(self.host + datapoint, data=body, timeout=5)
            if r.status_code == 200:
                return SUCCESS
        except TypeError:
            raise
        except requests.exceptions.ConnectionError:
            raise

    def _get_call(self, datapoint):
        try:
            r = requests.get(self.host + datapoint, timeout=5)
            if r.status_code == 200:
                return self._string_to_json(r.text)
        except TypeError:
            raise
        except requests.exceptions.ConnectionError:
            raise

    def _string_to_json(self, string):
        return json.loads(string)