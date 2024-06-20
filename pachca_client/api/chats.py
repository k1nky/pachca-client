from pachca_client.api.client import Client

class Chats:
    METHOD_CHATS = 'chats'

    def __init__(self, client: Client):
        self.client = client

    def list_chats(self):
        return self.client.call_api_get(self.METHOD_CHATS)