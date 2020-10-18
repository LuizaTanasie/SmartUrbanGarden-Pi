import requests
import json


class HttpUtils:
    @staticmethod
    def post(url, data):
        json_data = data.to_json()
        r = requests.post(url=url, json=json_data, verify=False)
        print(json_data + "\n")
        response = r.text
        return response
