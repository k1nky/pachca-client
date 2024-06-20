import unittest.mock as mock
import unittest
from pachca_client import Client
import pachca_client.api.exceptions as ex

class CheckResponseCase:
    def __init__(self, name, status_code, body = "", expected_exception = None, expected_message = ""):
        self.name = name
        self.status_code = status_code
        self.body = body
        self.expected_exception = expected_exception
        self.expected_message = expected_message


class TestCheckResponse(unittest.TestCase):

    def test_check_response_with_raised_error(self):
        cases = [
            CheckResponseCase("Unauthorized", 401, "", ex.PachcaClientBadRequestException, 'no error message'),
            CheckResponseCase("Moved", 307, "", ex.PachcaClientUnexpectedResponseException, 'unexpected response with status code 307'),
            CheckResponseCase("Unauthorized", 401, {'errors': 'custom error'}, ex.PachcaClientBadRequestException, 'custom error'),
            CheckResponseCase("Internal", 501, "", ex.PachcaClientUnexpectedResponseException, 'unexpected response with status code 501')
        ]
        client = Client('no-token')
        for case in cases:
            with self.assertRaises(case.expected_exception) as context:
                client.check_response_status(case.status_code, case.body)
            self.assertTrue(case.expected_message in context.exception.args)

    def test_check_response_with_no_error(self):
        cases = [
            CheckResponseCase("Created", 201),
            CheckResponseCase("Not found", 404),
        ]
        client = Client('')
        for case in cases:
            raised = False
            try:
                client.check_response_status(case.status_code, case.body)
            except Exception as e:
                raised = True
            self.assertFalse(raised)


def mock_response(status_code, body):
    mm = mock.MagicMock()
    mm.status_code = status_code
    mm.json.return_value = body
    return mm

class HandleResponseCase:
    def __init__(self, name, status_code, body, expected_data):
        self.name = name
        self.status_code = status_code
        self.body = body
        self.expected_data = expected_data

class TestHandleResponse(unittest.TestCase):
    def test_with_no_error(self):
        cases = [
            HandleResponseCase('', 201, [], []),
            HandleResponseCase('', 201, '', []),
            HandleResponseCase('', 200, {'data': [{'id': 123, 'name': 'Name'}]}, [{'id': 123, 'name': 'Name'}]),
        ]
        client = Client('')
        for case in cases:
            result = client.handle_response(mock_response(case.status_code, case.body))
            self.assertListEqual(result, case.expected_data)

    def test_with_raised_error(self):
        client = Client('')
        with self.assertRaises(ex.PachcaClientBadRequestException):
            client.handle_response(mock_response(401, ''))

    def test_with_silent_error(self):
        client = Client('', raise_on_error=False)
        raised = False
        try:
            client.handle_response(mock_response(401, ''))
        except ex.PachcaClientException:
            raised = True
        self.assertFalse(raised)


class TestCallApi(unittest.TestCase):

    def test_call_api_get(self):
        client = Client('secret-token')
        def mock_get(*args, **kwargs):
            self.assertEqual(args[0], 'https://api.pachca.com/api/shared/v1/some_method')
            self.assertDictEqual(kwargs['headers'], {'Authorization': 'Bearer secret-token'})
            self.assertDictEqual(kwargs['params'], {'arg1': 'value1', 'arg2': 'value2'})
            return mock_response(200, '')
        with mock.patch('requests.get', side_effect=mock_get):
            client.call_api_get('some_method', arg1='value1', arg2='value2')

    def test_call_api_post(self):
        client = Client('secret-token')
        def mock_post(*args, **kwargs):
            self.assertEqual(args[0], 'https://api.pachca.com/api/shared/v1/some_method')
            self.assertDictEqual(kwargs['headers'], {'Authorization': 'Bearer secret-token'})
            self.assertDictEqual(kwargs['json'], {'arg1': 'value1', 'arg2': 'value2'})
            return mock_response(200, '')
        with mock.patch('requests.post', side_effect=mock_post):
            client.call_api_post('some_method', arg1='value1', arg2='value2')


if __name__ == '__main__':
    unittest.main()