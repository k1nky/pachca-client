from pachca_client.api.client import Client
from datetime import datetime

METHOD_CHATS = 'chats'
METHOD_PROFILE_STATUS = 'profile/status'
METHOD_MESSAGES = 'messages'
METHOD_USERS = 'users'

class Cache:
    def __init__(self, ttl = 60):
        self.cache = {}
        self.ttl = {}
        self.max_ttl = ttl

    def update(self, scope, value):
        self.cache[scope] = value
        self.ttl[scope] = datetime.now().timestamp() + self.max_ttl

    def get(self, scope):
        if self.ttl[scope] < datetime.now().timestamp:
            return None
        if scope not in self.cache:
            return None
        return self.cache[scope]

class Pachca:
    def __init__(self, client: Client, cache: Cache = None):
        self.client = client
        self.cache = cache

    def set_cache(self, scope, value):
        if self.cache is None:
            return
        self.cache.update(scope, value)
        return value
    
    def get_cache(self, scope):
        if self.cache is None:
            return None
        return self.cache.get(scope)
    
    def resolve_chat_name(self, name):
        chats = self.get_cache(METHOD_CHATS)
        if chats is None:
            chats = self.list_chats()
        for chat in chats:
            if chat['name'] == name:
                return chat['id']
        return None

    def resolve_user_name(self, name):
        users = self.get_cache(METHOD_USERS)
        if users is None:
            users = self.list_chats()
        for user in users:
            if user['name'] == name:
                return user['id']
        return None

    def list_chats(self):
        return self.set_cache(METHOD_CHATS, self.client.call_api_get(METHOD_CHATS))
    
    def list_users(self):
        return self.set_cache(METHOD_USERS, self.client.call_api_get(METHOD_USERS))

    def get_status(self):
        return self.client.call_api_get(METHOD_PROFILE_STATUS)

    def new_message(self, content: str, entity_type: str = 'discussion', entity_name: str = '', entity_id: int = None, parent_message_id: int = None, files: list = []):
        if entity_id is None and len(entity_name) > 0:
            if entity_type == 'discussion':
                entity_id = self.resolve_chat_name(entity_name)
            elif entity_type == 'user':
                entity_id = self.resolve_user_name(entity_name)
        payload = {
            'message': {
                'entity_type': entity_type,
                'content': content,
                'entity_id': entity_id
            }
        }
        if parent_message_id is not None:
            payload['message']['parent_message_id'] = parent_message_id
        return self.client.call_api_post(METHOD_MESSAGES, **payload)
    
    def get_status(self, message_id):
        method = f'{METHOD_MESSAGES}/{message_id}'
        return self.client.call_api_get(method)
