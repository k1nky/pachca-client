from requests import Request, Session
import requests
from typing import IO
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
        if method.startswith('http'):
            return method
        return urljoin(self.API_URL, method)
    
    def upload(self, url: str, file: IO, data: dict):
        request = Request(method='post', url=url, headers=self.headers, data=data)
        request.files = {'file': file}
        return self.call(request)

    def call_api_post(self, method: str, payload: any = None) -> any:
        request = Request(method='post', url=self.request_url(method), headers=self.headers)
        if payload:
            request.json = payload
        return self.call(request)
    
    def call_api_get(self, method: str, payload: any = None) -> any:
        request = Request(method='get', url=self.request_url(method), headers=self.headers)
        if payload:
            request.params = payload
        return self.call(request)
    
    def call(self, request: requests.Request) -> any:
        prequest = request.prepare()
        response = self.session.send(prequest, proxies=self.proxies)
        return self.handle_response(response)
    
    def handle_response(self, response: requests.Response) -> any:
        try:
            self.check_response_status(response)
        except PachcaClientException as e:
            logger.error(f'request failed with {e}')
            if self.raise_on_error:
                raise e
        try:
            body = response.json()
        except JSONDecodeError:
            return response.text
        if isinstance(body, dict):
            try:
                return body['data']
            except KeyError:
                return body
        return response.text
    
    def check_response_status(self, response: requests.Response):
        if response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NOT_FOUND, HTTPStatus.NO_CONTENT):
            return
        if response.status_code >= 400 and response.status_code < 500:
            error_message = ''
            try:
                body = response.json()
                if isinstance(body, dict) and 'errors' in body:
                    error_message = body['errors']
                else:
                    error_message = response.text
            except ValueError:
                error_message = response.text
            raise PachcaClientBadRequestException(error_message)
        raise PachcaClientUnexpectedResponseException(f"unexpected response with status code {response.status_code}")
