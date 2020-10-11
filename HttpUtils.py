import requests
import json


class HttpUtils:
        @staticmethod
        def post(url, data):
                json_data = data.toJSON()
                r = requests.post(url=url, data=json_data, verify=False)
                response = r.text
                return response
