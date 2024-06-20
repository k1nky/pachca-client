from pachca_client.api.client import Client


class Messages:
    METHOD_MESSAGES = 'messages'

    def __init__(self, client: Client):
        self.client = client

    def new_message(self, message):
        payload = {
            'message': message
        }
        return self.client.call_api_post(self.METHOD_MESSAGES, **payload)
    
    def get_status(self, message_id):
        method = f'{self.METHOD_MESSAGES}/{message_id}'
        return self.client.call_api_get(method)
