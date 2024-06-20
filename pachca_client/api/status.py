from pachca_client.api.client import Client

class Status(Client):
    METHOD_PROFILE_STATUS = 'profile/status'

    def __init__(self, client: Client):
        self.client = client

    def get_status(self):
        return self.client.call_api_get(method=self.METHOD_PROFILE_STATUS)