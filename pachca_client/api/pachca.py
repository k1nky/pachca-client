from typing import Any, Optional, Dict, List, Union

from pachca_client.api.client import Client
from pachca_client.api.cache import Cache
from pachca_client.api.file import File
from pachca_client.api.exceptions import PachcaClientNotResolved

CHAT_TYPE_DISCUSSION = 'discussion'
CHAT_TYPE_THREAD = 'thread'
CHAT_TYPE_USER = 'user'

PATH_CHATS = 'chats'
PATH_MESSAGES = 'messages'
PATH_UPLOAD = 'uploads'
PATH_USERS = 'users'


def validate_paging(func):
    def inner(*args, **kwargs):
        if 'page' in kwargs and kwargs['page'] < 0:
            raise ValueError('page should be greater 1')
        if 'per' in kwargs and (kwargs['per'] < 0 or kwargs['per'] > 50):
            raise ValueError('per should between 1 and 50')
        return func(*args, **kwargs)

    return inner


class Pachca:
    def __init__(self, client: Client, cache: Cache = None) -> None:
        self.client = client
        self.cache = cache

    def delete_reaction(self, message_id: int, code: str) -> None:
        payload = {
            'code': code
        }
        self.client.call_api(f'{PATH_MESSAGES}/{message_id}/reactions', method='delete', payload=payload)    

    def get_cached(self, scope: str) -> Any:
        if self.cache is None:
            return None
        return self.cache.get(scope)

    def get_message(self, message_id) -> Optional[Dict]:
        return self.client.call_api(f'{PATH_MESSAGES}/{message_id}')

    def get_chat(self, chat_id: Union[str, int]) -> Optional[Dict]:
        if isinstance(chat_id, str):
            chat_id = self.resolve_chat_name(chat_id)
            if chat_id is None:
                raise PachcaClientNotResolved(chat_id)
        path = f'{PATH_CHATS}/{chat_id}'
        return self.client.call_api(path)

    @validate_paging
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

    @validate_paging
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

    @validate_paging
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

    @validate_paging
    def list_messages(self,
                      chat_id: int,
                      per: int = 50,
                      page: int = 1) -> Optional[List]:
        payload = {
            'chat_id': chat_id,
            'per': per,
            'page': page}
        return self.client.call_api(path=PATH_MESSAGES, payload=payload)

    @validate_paging
    def list_reactions(self,
                       message_id: int,
                       per: int = 50,
                       page: int = 1) -> Optional[List]:
        payload = {
            'per': per,
            'page': page
        }
        return self.client.call_api(path=f'{PATH_MESSAGES}/{message_id}/reactions', payload=payload)

    @validate_paging
    def list_users(self,
                   per: int = 50,
                   page: int = 1,
                   query: Optional[str] = None) -> List:
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

    def new_chat(self,
                 name: str,
                 members: List[int],
                 group_tags: Optional[List[int]] = None,
                 is_channel: bool = False,
                 is_public: bool = False) -> Optional[Dict]:
        chat = {
            'name': name,
            'member_ids': members,
            'channel': is_channel,
            'public': is_public
        }
        if group_tags is not None:
            chat['group_tag_ids'] = group_tags
        payload = {
            'chat': chat
        }
        response = self.client.call_api(PATH_CHATS, 'post', payload)
        if self.cache is not None:
            self.list_all_chats()
        return response

    def new_message(self,
                    chat_id: Union[str, int],
                    content: str,
                    chat_type: str = CHAT_TYPE_DISCUSSION,
                    parent_message_id: int = None,
                    files: List[File] = []) -> Optional[Dict]:
        if isinstance(chat_id, str):
            if chat_type == CHAT_TYPE_DISCUSSION:
                chat_id = self.resolve_chat_name(chat_id)
            elif chat_type == CHAT_TYPE_USER:
                chat_id = self.resolve_user_name(chat_id)
            if chat_id is None:
                raise PachcaClientNotResolved(chat_id)
        message = {
            'entity_type': chat_type,
            'content': content,
            'entity_id': chat_id}
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

    def new_reaction(self, message_id: int, code: str) -> None:
        payload = {
            'code': code
        }
        self.client.call_api(f'{PATH_MESSAGES}/{message_id}/reactions', method='post', payload=payload)

    def new_thread(self, id: int) -> Optional[Dict]:
        return self.client.call_api(f'{PATH_MESSAGES}/{id}/thread', method='post')

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

    def update_chat(self,
                    chat_id: Union[str, int],
                    name: str,
                    is_public: bool = False) -> Optional[Dict]:
        if isinstance(chat_id, str):
            chat_id = self.resolve_chat_name(chat_id)
        payload = {
            'chat': {
                'name': name,
                'public': is_public
            }
        }
        path = f'{PATH_CHATS}/{chat_id}'
        response = self.client.call_api(path, 'put', payload)
        if self.cache is not None:
            self.list_all_chats()
        return response

    def update_message(self,
                       message_id: int,
                       content: str,
                       files: List[File] = []) -> Optional[Dict]:
        message = {
            'content': content,
            'files': []
        }
        # TODO: update files
        payload = {'message': message}
        self.client.call_api(f'{PATH_MESSAGES}/{message_id}', 'put', payload)

    def upload(self, file: File) -> Optional[Dict]:
        # get pre-signed url
        info = self.client.call_api(PATH_UPLOAD, 'post')
        # upload file
        url = info['direct_url']
        del info['direct_url']
        with open(file.path, 'rb') as f:
            self.client.upload(url, f, info)
        return info
