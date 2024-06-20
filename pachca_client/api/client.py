import requests
from urllib.parse import urljoin
from http import HTTPStatus
import logging

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

    def request_url(self, method: str):
        return urljoin(self.API_URL, method)

    def call_api_post(self, method: str, **kwargs) -> list:
        response = requests.post(self.request_url(method), 
                      headers=self.headers,
                      proxies=self.proxies,
                      json=kwargs)
        return self.handle_response(response)
    
    def call_api_get(self, method: str, **kwargs) -> list:
        response = requests.get(self.request_url(method), 
                      headers=self.headers,
                      proxies=self.proxies,
                      params=kwargs)
        return self.handle_response(response)
    
    def handle_response(self, response: requests.Response) -> list:
        status_code = response.status_code
        body = response.json()
        try:
            self.check_response_status(status_code, body)
        except PachcaClientException as e:
            logger.error(f'request failed with {e}')
            if self.raise_on_error:
                raise e
        if 'data' in body:
            return body['data']
        return []
    
    def check_response_status(self, status_code: int, body: dict):
        if status_code in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NOT_FOUND):
            return
        if status_code >= 400 and status_code < 500:
            error_message = 'no error message'
            if 'errors' in body:
                error_message = body['errors']
            raise PachcaClientBadRequestException(error_message)
        raise PachcaClientUnexpectedResponseException(f"unexpected response with status code {status_code}")
