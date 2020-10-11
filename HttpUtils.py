import requests


class HttpUtils:
        @staticmethod
        def post(url, data):
                json = data.json()
                r = requests.post(url=url, data=json)
                response = r.text
                return response
