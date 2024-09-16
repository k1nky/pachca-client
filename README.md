[![RU](https://img.shields.io/badge/lang-RU-green.svg)](https://github.com/k1nky/pachca-client/blob/main/README.md)
[![EN](https://img.shields.io/badge/lang-EN-blue.svg)](https://github.com/k1nky/pachca-client/blob/main/README.en.md)

# Pachca Client

Python клиент для мессенджера Пачка (pachca.com).

## Поддерживаемый функционал

- [x] чаты
- [ ] участники чата
- [x] загрузка файлов
- [x] сообщения
- [x] реакции
- [ ] статус
- [ ] задачи
- [ ] теги
- [x] треды
- [ ] пользователи

## Установка

```
python -m pip install pachca-client
```

Pachca Client требует Python 3.6 или выше.


# Примеры

## Создание клиента

```
from pachca_client import get_pachca

# клиент по умолчанию
pachca =  get_pachca('MY_ACCESS_TOKEN')
```

Альтернативно клиент можно создать следующим способом:

```
from pachca_client import Client, Cache, Pachca

pachca = Pachca(Client('MY_ACCESS_TOKEN'), Cache())
```

## Сообщения

### Отправка сообщения

```
# по ID чата
message = pachca.new_message(chat_id=111111, content="My message")

# по имени чата
message = pachca.new_message(chat_id='MyChatName', content="My message")

# по ID пользователя
message = pachca.new_message(chat_id=222222, chat_type='user', content="My message")

# по имени пользователя
message = pachca.new_message(chat_id='User Name', chat_type='user', content="My message")

# по ID треда
message = pachca.new_message(chat_id=333333, chat_type='thread', content="My message")
```

### Отправка сообщений в тред

```
message = pachca.new_message(chat_id=111111, content="My message")
thread = pachca.new_thread(message['id'])
thread_message = pachca.new_message(chat_id=thread['id'], content="My message in the thread", chat_type='thread')
```

### Отправка сообщения с вложением

```
from pachca_client import File
files = [
    File('file_a.txt'),
    File('image_a.png', file_type='image')
]
message = pachca.new_message(chat_id=123456, content="Test message!", files=files)

```

## HTTP/HTTPS Proxy

Если требуется использование http прокси, то можно указать параметр `proxies` или соответсвующие переменные окружения (см. https://docs.python-requests.org/en/latest/user/advanced/).

```
from pachca_client import get_pachca

proxies = {
  'http': 'http://10.10.1.10:3128',
  'https': 'http://10.10.1.10:1080',
}
pachca =  get_pachca('MY_ACCESS_TOKEN', proxies=proxies)

```
