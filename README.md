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
# to a chat by its ID
message = pachca.new_message(entity_id=111111, content="My message")

# to a chat by its Name
message = pachca.new_message(entity_name='MyChatName', content="My message")

# to a user by its ID
message = pachca.new_message(entity_id=222222, entity_type='user' content="My message")

# to a user by its Name
message = pachca.new_message(entity_user='User Name', entity_type='user' content="My message")

# to a thread by its ID
# where 333333 is thread id created by `new_thread`
message = pachca.new_message(entity_id=333333, entity_type='thread' content="My message")
```

### Send a message with files:

```
from pachca_client import File
f = File('/home/shal/dev/pachca-client/requirements.txt')
files = [
    File('files_a.txt'),
    File('image_a.png', file_type='image')
]
message = pachca.new_message(entity_name="Test", content="Test message!", files=files)

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
