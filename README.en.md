[![RU](https://img.shields.io/badge/lang-RU-blue.svg)](https://github.com/k1nky/pachca-client/blob/main/README.md)
[![EN](https://img.shields.io/badge/lang-EN-green.svg)](https://github.com/k1nky/pachca-client/blob/main/README.en.md)


# Pachca Client

The package provides a client for **pachca.com**.

## Supported features

- [x] chats
- [ ] chat members
- [x] file upload
- [x] messages
- [x] reactions
- [ ] status
- [ ] tasks
- [ ] tags
- [x] threads
- [ ] users

## Installation

```
python -m pip install pachca-client
```

Pachca Client requires Python 3.6 or higher.


# Examples

## Get the client

```
from pachca_client import get_pachca

# default client
pachca =  get_pachca('MY_ACCESS_TOKEN')
```

Alternatively you can create the client like this:

```
from pachca_client import Client, Cache, Pachca

pachca = Pachca(Client('MY_ACCESS_TOKEN'), Cache())
```

## Messages

### Send a message

```
# to chat by its ID
message = pachca.new_message(chat_id=111111, content="My message")

# to chat by its Name
message = pachca.new_message(chat_id='MyChatName', content="My message")

# to user by its ID
message = pachca.new_message(chat_id=222222, chat_type='user', content="My message")

# to user by its Name
message = pachca.new_message(chat_id='User Name', chat_type='user', content="My message")

# to thread by its ID
# where 333333 is thread id created by `new_thread`
message = pachca.new_message(chat_id=333333, chat_type='thread', content="My message")
```

### Send a message to thread

```
message = pachca.new_message(chat_id=111111, content="My message")
thread = pachca.new_thread(message['id'])
thread_message = pachca.new_message(chat_id=thread['id'], content="My message in the thread", chat_type='thread')
```

### Send a message with files

```
from pachca_client import File
files = [
    File('file_a.txt'),
    File('image_a.png', file_type='image')
]
message = pachca.new_message(chat_id=123456, content="Test message!", files=files)

```

## HTTP/HTTPS Proxy

If you need to use a proxy, you can set `proxies` parameter or environment variables. For more information see https://docs.python-requests.org/en/latest/user/advanced/.

```
from pachca_client import get_pachca

proxies = {
  'http': 'http://10.10.1.10:3128',
  'https': 'http://10.10.1.10:1080',
}
pachca =  get_pachca('MY_ACCESS_TOKEN', proxies=proxies)

```
