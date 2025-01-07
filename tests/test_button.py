from pachca_client.api.button import Button
import unittest


class TestButton(unittest.TestCase):
    def test_with_empty_text(self):
        with self.assertRaises(ValueError):
            Button.url('', 'value_a')

    def test_with_empty_value(self):
        with self.assertRaises(ValueError):
            Button.data('text_a', '')

    def test_valid_args(self):
        got = Button.data('text_a', 'value_a')
        self.assertDictEqual(got, {'text': 'text_a', 'data': 'value_a'})
