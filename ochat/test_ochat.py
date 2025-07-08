import unittest
from unittest.mock import patch, MagicMock
import io
import sys
import os
from ochat import chat_with_ollama, main

class TestOllamaChat(unittest.TestCase):
    """Unit tests for ochat.py."""

    @patch('ollama.chat')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_chat_with_ollama_text_only(self, mock_stdout, mock_ollama_chat):
        """
        Tests the chat_with_ollama function with a text-only message.
        """
        mock_response_chunk = {'message': {'content': 'Hello, this is a test response.'}}
        mock_ollama_chat.return_value = [mock_response_chunk]

        chat_with_ollama(model='gemma3', message='Hello')

        output = mock_stdout.getvalue()
        self.assertIn("--- Asking 'gemma3': Hello ---", output)
        self.assertIn('Hello, this is a test response.', output)
        self.assertIn('--- End of response ---', output)

    @patch('ollama.chat')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_chat_with_ollama_with_single_image(self, mock_stdout, mock_ollama_chat):
        """
        Tests the chat_with_ollama function with a single image.
        """
        mock_response_chunk = {'message': {'content': 'This image contains a cat.'}}
        mock_ollama_chat.return_value = [mock_response_chunk]
        
        dummy_image_data = [b'dummy_image_bytes']

        chat_with_ollama(model='llava', message='What is in this image?', images=dummy_image_data)

        output = mock_stdout.getvalue()
        self.assertIn("--- Asking 'llava' (with 1 image(s)): What is in this image? ---", output)
        self.assertIn('This image contains a cat.', output)
        self.assertIn('--- End of response ---', output)
        
        mock_ollama_chat.assert_called_once()
        _, called_kwargs = mock_ollama_chat.call_args
        self.assertEqual(called_kwargs['messages'][0]['images'], dummy_image_data)

    @patch('ollama.chat')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_chat_with_ollama_with_multiple_images(self, mock_stdout, mock_ollama_chat):
        """
        Tests the chat_with_ollama function with multiple images.
        """
        mock_response_chunk = {'message': {'content': 'These images contain a cat and a dog.'}}
        mock_ollama_chat.return_value = [mock_response_chunk]
        
        dummy_images_data = [b'dummy_image_bytes_1', b'dummy_image_bytes_2']

        chat_with_ollama(model='llava', message='What is in these images?', images=dummy_images_data)

        output = mock_stdout.getvalue()
        self.assertIn("--- Asking 'llava' (with 2 image(s)): What is in these images? ---", output)
        self.assertIn('These images contain a cat and a dog.', output)
        self.assertIn('--- End of response ---', output)
        
        mock_ollama_chat.assert_called_once()
        _, called_kwargs = mock_ollama_chat.call_args
        self.assertEqual(called_kwargs['messages'][0]['images'], dummy_images_data)

    @patch('sys.argv', ['ochat.py', 'Hello', 'from', 'command', 'line'])
    @patch('ochat.chat_with_ollama')
    def test_main_with_message_arg(self, mock_chat_func):
        """
        Tests that the main function correctly parses a command-line message.
        """
        main()
        mock_chat_func.assert_called_with(
            model='gemma3', 
            message='Hello from command line', 
            images=None
        )

    @patch('sys.argv', ['ochat.py', 'Custom', 'message', '--model', 'test_model'])
    @patch('ochat.chat_with_ollama')
    def test_main_with_model_and_message_args(self, mock_chat_func):
        """
        Tests that the main function correctly parses model and message arguments.
        """
        main()
        mock_chat_func.assert_called_with(
            model='test_model', 
            message='Custom message', 
            images=None
        )

    @patch('ochat.chat_with_ollama')
    def test_main_with_single_image_arg(self, mock_chat_func):
        """
        Tests that the main function correctly handles a single image argument.
        """
        with patch('sys.argv', ['ochat.py', 'What', 'is', 'this?', '--image', 'dummy_image.png']), \
             patch('os.path.exists', return_value=True), \
             patch('builtins.open', unittest.mock.mock_open(read_data=b'dummy_image_bytes')):
            main()
        
        mock_chat_func.assert_called_with(
            model='gemma3', 
            message='What is this?', 
            images=[b'dummy_image_bytes']
        )

    @patch('ochat.chat_with_ollama')
    def test_main_with_multiple_images_arg(self, mock_chat_func):
        """
        Tests that the main function correctly handles multiple image arguments.
        """
        image_paths = ['dummy1.png', 'dummy2.jpg']
        image_contents = {
            'dummy1.png': b'dummy_image_bytes_1',
            'dummy2.jpg': b'dummy_image_bytes_2'
        }
        
        def mock_open_side_effect(path, mode):
            # Use os.path.basename because the full path might be constructed differently
            content = image_contents.get(os.path.basename(path))
            if content is None:
                raise FileNotFoundError(f"Mock file not found: {path}")
            return unittest.mock.mock_open(read_data=content)()

        sys_argv_mock = ['ochat.py', 'What', 'are', 'these?', '--image'] + image_paths

        with patch('sys.argv', sys_argv_mock), \
             patch('os.path.exists', return_value=True), \
             patch('builtins.open', side_effect=mock_open_side_effect):
            main()
        
        mock_chat_func.assert_called_with(
            model='gemma3', 
            message='What are these?', 
            images=[b'dummy_image_bytes_1', b'dummy_image_bytes_2']
        )

    @patch('sys.argv', ['ochat.py'])
    @patch('ochat.chat_with_ollama')
    def test_main_with_no_message_defaults_to_joke(self, mock_chat_func):
        """
        Tests that the main function defaults to a joke when no message is provided.
        """
        main()
        mock_chat_func.assert_called_with(
            model='gemma3', 
            message='Tell me a funny joke.', 
            images=None
        )

if __name__ == '__main__':
    unittest.main()