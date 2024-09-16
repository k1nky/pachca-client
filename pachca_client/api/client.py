from http import HTTPStatus
from json import JSONDecodeError
import logging
from requests import Request, Session, Response
from urllib.parse import urljoin
from typing import Dict, List, Union, Optional, IO

from pachca_client.api.exceptions import (PachcaClientUnexpectedResponseException,
                                          PachcaClientBadRequestException,
                                          PachcaClientException,
                                          PachcaClientEntryNotFound)


# Types
ApiResponse = Union[Dict, List, str]
ApiJsonPayload = Optional[Union[Dict, List]]

# Constants
DEFAULT_TIMEOUT = 30

logger = logging.getLogger(__name__)


class Client:
    API_URL = 'https://api.pachca.com/api/shared/v1/'

    def __init__(self, access_token: str, proxies: Dict = {}, raise_on_error: bool = True, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.headers = {
            'Authorization': f'Bearer {access_token}'
        }
        self.proxies = proxies
        self.raise_on_error = raise_on_error
        self.session = Session()
        self.timeout = timeout

    def call_api(self, path: str, method: str = 'get', payload: ApiJsonPayload = None) -> ApiResponse:
        request = Request(method=method, url=self.request_url(path), headers=self.headers)
        if payload:
            if method == 'get':
                request.params = payload
            else:
                request.json = payload
        return self.call(request)

    def call(self, request: Request) -> ApiResponse:
        prequest = request.prepare()
        response = self.session.send(prequest, proxies=self.proxies, timeout=self.timeout)
        return self.handle_response(response)

    def check_response_status(self, response: Response) -> None:
        if response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NO_CONTENT):
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
            if response.status_code == HTTPStatus.NOT_FOUND:
                raise PachcaClientEntryNotFound(error_message)
            raise PachcaClientBadRequestException(error_message)
        raise PachcaClientUnexpectedResponseException(f"unexpected response with status code {response.status_code}")

    def handle_response(self, response: Response) -> ApiResponse:
        try:
            self.check_response_status(response)
        except PachcaClientException as e:
            logger.error(f'request failed with {e}')
            if self.raise_on_error:
                raise e
        try:
            body = response.json()
        except JSONDecodeError:
            # the response body does not contain valid json
            return response.text
        if isinstance(body, dict):
            try:
                return body['data']
            except KeyError:
                return body
        return response.text

    def request_url(self, path: str) -> str:
        return urljoin(self.API_URL, path)

    def upload(self, url: str, file: IO, data: Dict) -> ApiResponse:
        request = Request(method='post', url=url, headers=self.headers, data=data)
        request.files = {'file': file}
        return self.call(request)
