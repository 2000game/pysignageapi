import requests
import json
class PySignageAPI():
    def __init__(self, host, username, password, port):
        self.host = f"http://{username}:{password}@{host}:{port}/api"

    def post_call(self, datapoint, body=None):
        r = requests.post(self.host + datapoint, data=body)
        if r.status_code == 200:
            return True
        else:
            raise TypeError

    def get_call(self, datapoint):
        r = requests.get(self.host + datapoint)
        if r.status_code == 200:
            return self.string_to_json(r.text)
        else:
            return

    def string_to_json(self, string):
        return json.loads(string)