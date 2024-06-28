import unittest.mock as mock
import unittest
from pachca_client import Client
import pachca_client.api.exceptions as ex


def mock_response(status_code, body="", exception=None):
    mm = mock.MagicMock()
    mm.status_code = status_code
    if exception is not None:
        mm.json.side_effect = exception()
    else:
        mm.json.return_value = body
    mm.text = body
    return mm


class CheckResponseCase:
    def __init__(self, name, response, expected_exception=None, expected_message=""):
        self.name = name
        self.response = response
        self.expected_exception = expected_exception
        self.expected_message = expected_message


class TestCheckResponse(unittest.TestCase):

    def test_check_response_with_raised_error(self):
        cases = [
            CheckResponseCase("Empty Text", mock_response(401, ''), ex.PachcaClientBadRequestException, ''),
            CheckResponseCase("Plain Text", mock_response(401, 'plain_error_text', ValueError), ex.PachcaClientBadRequestException, 'plain_error_text'),
            CheckResponseCase("Moved", mock_response(307, ""), ex.PachcaClientUnexpectedResponseException, 'unexpected response with status code 307'),
            CheckResponseCase("Unauthorized", mock_response(401, {'errors': 'custom error'}), ex.PachcaClientBadRequestException, 'custom error'),
            CheckResponseCase("InvalidJson", mock_response(401, 'errors=custom error'), ex.PachcaClientBadRequestException, 'errors=custom error'),
            CheckResponseCase("Internal", mock_response(501, ""), ex.PachcaClientUnexpectedResponseException, 'unexpected response with status code 501'),
            CheckResponseCase("Not Found", mock_response(404, {'errors': 'custom error'}), ex.PachcaClientEntryNotFound, 'custom error')
        ]
        client = Client('')
        for case in cases:
            with self.assertRaises(case.expected_exception) as context:
                client.check_response_status(case.response)
            self.assertTrue(case.expected_message in context.exception.args, case.name)

    def test_check_response_with_no_error(self):
        cases = [
            CheckResponseCase("Created", mock_response(201)),
        ]
        client = Client('')
        for case in cases:
            raised = False
            try:
                client.check_response_status(case.response)
            except Exception:
                raised = True
            self.assertFalse(raised)


class TestSuccessHandleResponse(unittest.TestCase):
    def setUp(self):
        self.client = Client('')

    def test_empty_list_response(self):
        result = self.client.handle_response(mock_response(201, []))
        self.assertListEqual(result, [])

    def test_empty_response(self):
        result = self.client.handle_response(mock_response(201))
        self.assertEqual(result, '')

    def test_data_attribute(self):
        result = self.client.handle_response(mock_response(200, {'data': [{'id': 123, 'name': 'Name'}]}))
        self.assertListEqual(result, [{'id': 123, 'name': 'Name'}])

    def test_no_data_attribute(self):
        result = self.client.handle_response(mock_response(200, {'id': 123, 'name': 'Name'}))
        self.assertDictEqual(result, {'id': 123, 'name': 'Name'})


class TestFailedHandleResponse(unittest.TestCase):

    def test_with_raised_error(self):
        client = Client('')
        with self.assertRaises(ex.PachcaClientBadRequestException):
            client.handle_response(mock_response(401))

    def test_with_silent_error(self):
        client = Client('', raise_on_error=False)
        raised = False
        try:
            client.handle_response(mock_response(401))
        except ex.PachcaClientException:
            raised = True
        self.assertFalse(raised)


class TestCallApi(unittest.TestCase):

    def test_call_api_get(self):
        client = Client('secret-token')

        def mock_get(*args, **kwargs):
            request = args[0]
            self.assertEqual(request.url, 'https://api.pachca.com/api/shared/v1/some_method?arg1=value1&arg2=value2')
            self.assertEqual(request.headers['Authorization'], 'Bearer secret-token')
            return mock_response(200, '')
        mm = mock.MagicMock()
        mm.send.side_effect = mock_get
        client.session = mm
        client.call_api('some_method', 'get', {'arg1': 'value1', 'arg2': 'value2'})

    def test_call_api_post(self):
        client = Client('secret-token')

        def mock_post(*args, **kwargs):
            request = args[0]
            self.assertEqual(request.url, 'https://api.pachca.com/api/shared/v1/some_method')
            self.assertEqual(request.headers['Authorization'], 'Bearer secret-token')
            self.assertEqual(request.body, b'{"arg1": "value1", "arg2": "value2"}')
            return mock_response(200, '')
        mm = mock.MagicMock()
        mm.send.side_effect = mock_post
        client.session = mm
        client.call_api('some_method', 'post', {'arg1': 'value1', 'arg2': 'value2'})


if __name__ == '__main__':
    unittest.main()
