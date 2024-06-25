from typing import Any, Optional, Dict, List, Union

from pachca_client.api.client import Client
from pachca_client.api.cache import Cache
from pachca_client.api.file import File

ENTITY_TYPE_DISCUSSION = 'discussion'
ENTITY_TYPE_THREAD = 'thread'
ENTITY_TYPE_USER = 'user'

PATH_CHATS = 'chats'
PATH_MESSAGES = 'messages'
PATH_UPLOAD = 'uploads'
PATH_USERS = 'users'


class Pachca:
    def __init__(self, client: Client, cache: Cache = None) -> None:
        self.client = client
        self.cache = cache

    def get_cached(self, scope: str) -> Any:
        if self.cache is None:
            return None
        return self.cache.get(scope)

    def get_message(self, message_id) -> Optional[Dict]:
        return self.client.call_api_get(f'{PATH_MESSAGES}/{message_id}')

    def get_chat(self, chat_id: Union[str, int]) -> Optional[Dict]:
        if isinstance(chat_id, str):
            chat_id = self.resolve_chat_name(chat_id)
        path = f'{PATH_CHATS}/{chat_id}'
        return self.client.call_api(path)

    def list_all_chats(self, per: int = 50) -> List:
        page = 1
        chats = []
        while True:
            response = self.list_chats(per, page)
            chats.extend(response)
            if len(response) == per:
                page += 1
                continue
            break
        return self.set_cached(PATH_CHATS, chats)

    def list_all_users(self, per: int = 50) -> List:
        page = 1
        users = []
        while True:
            response = self.list_users(per=per, page=page)
            users.extend(response)
            if len(response) == per:
                page += 1
                continue
            break
        return self.set_cached(PATH_USERS, users)

    def list_chats(self,
                   per: int = 50,
                   page: int = 1,
                   availability: str = 'is_member',
                   last_message_at_after: Optional[str] = None,
                   last_message_at_before: Optional[str] = None) -> List:
        payload = {
            'per': per,
            'page': page,
            'availability': availability}
        if last_message_at_after:
            payload['last_message_at_after'] = last_message_at_after
        if last_message_at_before:
            payload['last_message_at_before'] = last_message_at_before
        response = self.client.call_api(path=PATH_CHATS, payload=payload)
        if response is None:
            return []
        return response

    def list_messages(self, chat_id: int, per: int = 50, page: int = 1) -> Optional[List]:
        payload = {
            'chat_id': chat_id,
            'per': per,
            'page': page}
        return self.client.call_api(path=PATH_MESSAGES, payload=payload)

    def list_users(self, per: int = 50, page: int = 1, query: Optional[str] = None) -> List:
        payload = {
            'per': per,
            'page': page
        }
        if query:
            payload['query'] = query
        response = self.client.call_api(path=PATH_USERS, payload=payload)
        if response is None:
            return []
        return response

    def new_message(self,
                    entity_id: Union[str, int],
                    content: str,
                    entity_type: str = ENTITY_TYPE_DISCUSSION,
                    parent_message_id: int = None,
                    files: List[File] = []) -> Optional[Dict]:
        if isinstance(entity_id, str):
            if entity_type == ENTITY_TYPE_DISCUSSION:
                entity_id = self.resolve_chat_name(entity_id)
            elif entity_type == ENTITY_TYPE_USER:
                entity_id = self.resolve_user_name(entity_id)
        message = {
            'entity_type': entity_type,
            'content': content,
            'entity_id': entity_id}
        if parent_message_id is not None:
            message['parent_message_id'] = parent_message_id
        if len(files) != 0:
            message['files'] = []
            for file in files:
                file_info = self.upload(file)
                file.prepare(file_info['key'])
                message['files'].append(file.as_dict())
        payload = {
            'message': message}
        return self.client.call_api(path=PATH_MESSAGES, method='post', payload=payload)

    def new_thread(self, id: int) -> Optional[Dict]:
        method = f'{PATH_MESSAGES}/{id}/thread'
        return self.client.call_api(method, method='post')

    def resolve_chat_name(self, name: str) -> Optional[int]:
        chats = self.get_cached(PATH_CHATS)
        if chats is None:
            chats = self.list_all_chats()
        for chat in chats:
            if chat['name'] == name:
                return chat['id']
        return None

    def resolve_user_name(self, name: str) -> Optional[int]:
        users = self.get_cached(PATH_USERS)
        if users is None:
            users = self.list_all_users()
        for user in users:
            if user['nickname'] == name:
                return user['id']
        return None

    def set_cached(self, scope: str, value: Any) -> Any:
        if self.cache is None:
            return value
        self.cache.update(scope, value)
        return value

    def update_message(self, message_id: int, content: str, files: List[File] = []) -> Optional[Dict]:
        message = {
            'content': content,
            'files': []
        }
        # TODO: update files
        payload = {'message': message}
        self.client.call_api(f'{PATH_MESSAGES}/{message_id}', 'put', payload)

    def upload(self, file: File) -> Optional[Dict]:
        # get pre-signed url
        info = self.client.call_api_post(PATH_UPLOAD)
        # upload file
        url = info['direct_url']
        del info['direct_url']
        with open(file.path, 'rb') as f:
            self.client.upload(url, f, info)
        return info
