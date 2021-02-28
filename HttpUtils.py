import requests
import json

class HttpUtils:
    @staticmethod
    def post(url, data):
        json_data = json.loads(data.to_json())
        r = requests.post(url=url, json=json_data, verify=False)
        response = r.text
        return response
