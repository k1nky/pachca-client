from requests import Request, Session
import requests
from urllib.parse import urljoin
from http import HTTPStatus
import logging
from json import JSONDecodeError

from pachca_client.api.exceptions import (PachcaClientUnexpectedResponseException,
                                          PachcaClientBadRequestException,
                                          PachcaClientException)

logger = logging.getLogger(__name__)

class Client:
    API_URL = 'https://api.pachca.com/api/shared/v1/'

    def __init__(self, access_token: str, proxies: dict = {}, raise_on_error: bool = True):
        self.headers = {
            'Authorization': f'Bearer {access_token}'
        }
        self.proxies = proxies
        self.raise_on_error = raise_on_error
        self.session = Session()

    def request_url(self, method: str):
        return urljoin(self.API_URL, method)

    def call_api_post(self, method: str, **kwargs) -> list:        
        request = Request(method='post', url=self.request_url(method), headers=self.headers)
        if len(kwargs) > 0:
            request.json = kwargs
        return self.call(request)
    
    def call_api_get(self, method: str, **kwargs) -> list:
        request = Request(method='get', url=self.request_url(method), headers=self.headers)
        if len(kwargs) > 0:
            request.params = kwargs
        return self.call(request)
    
    def call(self, request: requests.Request) -> list:
        prequest = request.prepare()
        response = self.session.send(prequest, proxies=self.proxies)
        return self.handle_response(response)
    
    def handle_response(self, response: requests.Response) -> list:
        try:
            self.check_response_status(response)
        except PachcaClientException as e:
            logger.error(f'request failed with {e}')
            if self.raise_on_error:
                raise e
        try:
            body = response.json()
        except JSONDecodeError:
            return []
        if 'data' in body:
            return body['data']
        return []
    
    def check_response_status(self, response: requests.Response):
        if response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NOT_FOUND):
            return
        if response.status_code >= 400 and response.status_code < 500:
            error_message = 'no error message'
            try:
                body = response.json()
            except JSONDecodeError:
                error_message = response.text
            if 'errors' in body:
                error_message = body['errors']
            raise PachcaClientBadRequestException(error_message)
        raise PachcaClientUnexpectedResponseException(f"unexpected response with status code {response.status_code}")
