import requests
import json


class BaseRequestSender(object):
    def __init__(self, body, request_type, url):
        self.url = url
        self.request_type = request_type
        self.body = body
        self.headers = {
            "Host": "localhost:5000",
            "Connection": "keep-alive",
            "Postman-Token": "c27d99fd-ef9c-f7bb-7cd8-a60e4045ced1",
            "Cache-Control": "no-cache",
            "Origin": "chrome-extension://fhbjgbiflinjbdggehcddcbncdddomop",
            "User-Agent": """Mozilla/5.0 (Windows NT 6.1; Win64; x64) 
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 
            Safari/537.36""",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,sr;q=0.2"}
        self.rest_message = None
        self.request = None

    def __add_length(self):
        if self.body:
            self.headers['Content-Length'] = len(self.body)

    def send_message(self):
        if self.request_type == 'GET':
            self.request = requests.get(self.url,
                                        headers=self.headers)
        elif self.request_type == 'POST':
            self.__add_length()
            self.request = requests.post(self.url,
                                         headers=self.headers,
                                         data=json.dumps(self.body))
        return self.request


class GetServicesRequestSender(BaseRequestSender):
    def __init__(self):
        super(GetServicesRequestSender, self)\
            .__init__(body=None,
                      request_type='GET',
                      url='http://localhost:5000/services')


class EnableServiceRequestSender(BaseRequestSender):
    def __init__(self, body):
        super(EnableServiceRequestSender, self)\
            .__init__(body=None,
                      request_type='POST',
                      url='http://localhost:5000/client/add_service')
        self.body = body


class CheckClientServicesRequestSender(BaseRequestSender):
    def __init__(self, body):
        super(CheckClientServicesRequestSender, self)\
            .__init__(body=None,
                      request_type='POST',
                      url='http://localhost:5000/client/services')
        self.body = body

