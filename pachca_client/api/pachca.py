from pachca_client.api.client import Client
from pachca_client.api.cache import Cache
from pachca_client.api.file import File

ENTITY_TYPE_DISCUSSION = 'discussion'
ENTITY_TYPE_USER = 'user'
ENTITY_TYPE_THREAD = 'thread'

METHOD_CHATS = 'chats'
METHOD_PROFILE_STATUS = 'profile/status'
METHOD_MESSAGES = 'messages'
METHOD_USERS = 'users'
METHOD_UPLOAD = 'uploads'

class Pachca:
    def __init__(self, client: Client, cache: Cache = None):
        self.client = client
        self.cache = cache

    def set_cached(self, scope: str, value: any):
        if self.cache is None:
            return
        self.cache.update(scope, value)
        return value
    
    def get_cached(self, scope: str):
        if self.cache is None:
            return None
        return self.cache.get(scope)
    
    def resolve_chat_name(self, name):
        chats = self.get_cached(METHOD_CHATS)
        if chats is None:
            chats = self.list_chats()
        for chat in chats:
            if chat['name'] == name:
                return chat['id']
        return None

    def resolve_user_name(self, name):
        users = self.get_cached(METHOD_USERS)
        if users is None:
            users = self.list_users()
        for user in users:
            if user['nickname'] == name:
                return user['id']
        return None

    def list_chats(self):
        return self.set_cached(METHOD_CHATS, self.client.call_api_get(METHOD_CHATS))
    
    def list_users(self):
        return self.set_cached(METHOD_USERS, self.client.call_api_get(METHOD_USERS))

    def get_status(self):
        return self.client.call_api_get(METHOD_PROFILE_STATUS)
    
    def new_message(self,
                    content: str,
                    entity_type: str = ENTITY_TYPE_DISCUSSION,
                    entity_name: str = '',
                    entity_id: int = None,
                    parent_message_id: int = None,
                    files: list[File] = []):
        if entity_id is None and len(entity_name) > 0:
            if entity_type == ENTITY_TYPE_DISCUSSION:
                entity_id = self.resolve_chat_name(entity_name)
            elif entity_type == ENTITY_TYPE_USER:
                entity_id = self.resolve_user_name(entity_name)
        message = {
            'entity_type': entity_type,
            'content': content,
            'entity_id': entity_id
            }
        if parent_message_id is not None:
            message['parent_message_id'] = parent_message_id
        if len(files) != 0:
            message['files'] = []
            for file in files:
                file_info = self.upload(file)
                file.prepare(file_info['key'])
                message['files'].append(file.as_dict())
        payload = {
            'message': message
        }
        return self.client.call_api_post(METHOD_MESSAGES, payload)
    
    def new_thread(self, id: int):
        method = f'{METHOD_USERS}/{id}/thread'
        return self.client.call_api_post(method)
    
    def get_status(self, message_id):
        method = f'{METHOD_MESSAGES}/{message_id}'
        return self.client.call_api_get(method)

    def upload(self, file: File):
        # get pre-sign object
        info = self.client.call_api_post(METHOD_UPLOAD)
        # upload file
        url = info['direct_url']
        del info['direct_url']
        with open(file.path, 'rb') as f:
            response = self.client.upload(url, f, info)            
        return info
