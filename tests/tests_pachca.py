import unittest.mock as mock
import unittest
from pachca_client import get_pachca, Pachca, Client, Cache


class TestResolveName(unittest.TestCase):
    def setUp(self):
        self.pachca = get_pachca('')

    def test_resolve_user_name(self):
        self.pachca.get_cached = mock.MagicMock()
        self.pachca.get_cached.return_value = None
        self.pachca.list_all_users = mock.MagicMock()
        self.pachca.list_all_users.return_value = [
            {'nickname': 'andrey', 'id': 100}, {'nickname': 'sergey', 'id': 200}
        ]
        self.assertEqual(self.pachca.resolve_user_name('andrey'), 100)
        self.assertEqual(self.pachca.resolve_user_name('dmitriy'), None)

    def test_resolve_user_name_cached(self):
        self.pachca.get_cached = mock.MagicMock()
        self.pachca.get_cached.return_value = [
            {'nickname': 'andrey', 'id': 100}, {'nickname': 'sergey', 'id': 200}
        ]
        self.assertEqual(self.pachca.resolve_user_name('andrey'), 100)
        self.assertEqual(self.pachca.resolve_user_name('dmitriy'), None)

    def test_resolve_chat_name(self):
        self.pachca.get_cached = mock.MagicMock()
        self.pachca.get_cached.return_value = None
        self.pachca.list_all_chats = mock.MagicMock()
        self.pachca.list_all_chats.return_value = [
            {'name': 'Chat1', 'id': 100}, {'name': 'Chat2', 'id': 200}
        ]
        self.assertEqual(self.pachca.resolve_chat_name('Chat1'), 100)
        self.assertEqual(self.pachca.resolve_chat_name('Chat3'), None)

    def test_resolve_chat_name_cached(self):
        self.pachca.get_cached = mock.MagicMock()
        self.pachca.get_cached.return_value = [
            {'name': 'Chat1', 'id': 100}, {'name': 'Chat2', 'id': 200}
        ]
        self.assertEqual(self.pachca.resolve_chat_name('Chat1'), 100)
        self.assertEqual(self.pachca.resolve_chat_name('Chat3'), None)


class TestCached(unittest.TestCase):
    def test_set_cached_no_cache(self):
        pachca = Pachca(Client(''), None)
        self.assertEqual(pachca.set_cached('scope1', 'value1'), 'value1')

    def test_set_cached(self):
        pachca = Pachca(Client(''), Cache())
        pachca.cache.update = mock.MagicMock()
        pachca.cache.update.return_value = None
        self.assertEqual(pachca.set_cached('scope1', 'value1'), 'value1')
        pachca.cache.update.assert_called_once_with('scope1', 'value1')


class TestChats(unittest.TestCase):
    def setUp(self):
        self.pachca = get_pachca('')

    def test_get_chat_by_id(self):
        self.pachca.client.call_api = mock.MagicMock()
        self.pachca.client.call_api.return_value = {'name': 'Chat1', 'id': 100}
        self.assertDictEqual(self.pachca.get_chat(100), {'name': 'Chat1', 'id': 100})

    def test_get_chat_by_name(self):
        self.pachca.client.call_api = mock.MagicMock()
        self.pachca.client.call_api.return_value = {'name': 'Chat1', 'id': 100}
        self.pachca.resolve_chat_name = mock.MagicMock()
        self.pachca.resolve_chat_name.return_value = 100
        self.assertDictEqual(self.pachca.get_chat('Chat1'), {'name': 'Chat1', 'id': 100})
        self.pachca.resolve_chat_name.assert_called_once()
        self.pachca.client.call_api.assert_called_once_with('chats/100')

    def test_list_all_chats(self):
        self.pachca.list_chats = mock.MagicMock()

        def mock_list_chats(per: int, page: int):
            if page == 1:
                return [{'name': 'Chat1', 'id': 100}, {'name': 'Chat2', 'id': 200}]
            if page == 2:
                return [{'name': 'Chat3', 'id': 300}]

        self.pachca.list_chats.side_effect = mock_list_chats
        chats = self.pachca.list_all_chats(per=2)
        self.assertListEqual(chats, [{'name': 'Chat1', 'id': 100}, {'name': 'Chat2', 'id': 200}, {'name': 'Chat3', 'id': 300}])


class TestMessages(unittest.TestCase):
    def setUp(self):
        self.pachca = get_pachca('')

    def test_new_message_to_named_chat(self):
        self.pachca.resolve_chat_name = mock.MagicMock(return_value={'name': 'ChatName', 'id': 100})
        self.pachca.client.call_api = mock.MagicMock(return_value={'id': 200})
        response = self.pachca.new_message(chat_id='ChatName1', content='Message')
        self.assertDictEqual(response, {'id': 200})
        self.pachca.resolve_chat_name.assert_called_once_with('ChatName1')
        self.pachca.client.call_api.assert_called_once()


class TestUpload(unittest.TestCase):
    def setUp(self):
        self.pachca = get_pachca('')


if __name__ == '__main__':
    unittest.main()
