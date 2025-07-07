import unittest
from unittest.mock import patch
import datetime
import io
import sys

# Import the functions and data from your script
from hello import main, get_random_joke, JOKES


class TestHello(unittest.TestCase):
    """Unit tests for hello.py."""

    @patch('hello.get_random_joke')
    @patch('hello.datetime')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_output(self, mock_stdout, mock_datetime, mock_get_joke):
        """
        Tests the main function's output by mocking the current time,
        the random joke selection, and capturing stdout.
        """
        # 1. Setup mocks
        mock_utc_now = datetime.datetime(2023, 10, 27, 10, 0, 0, tzinfo=datetime.timezone.utc)
        mock_datetime.datetime.now.return_value = mock_utc_now

        # Attach the real timezone and timedelta classes to the mock module.
        # This is crucial because the code under test needs these to create
        # timezone objects, and patching 'hello.datetime' replaces the whole module.
        mock_datetime.timezone = datetime.timezone
        mock_datetime.timedelta = datetime.timedelta

        # Configure the mock joke function to return a predictable joke
        test_joke = "\nMocked Joke\nMocked Punchline"
        mock_get_joke.return_value = test_joke

        # 2. Run the function
        main()

        # 3. Get the captured output and assert its contents
        output = mock_stdout.getvalue()

        # Expected output based on the mocked time (10:00 UTC is 12:00 UTC+2)
        self.assertIn("The current date and time in UTC+2 is: 2023-10-27 12:00:00 +0200", output)
        self.assertIn(test_joke, output)

    @patch('hello.random.choice')
    def test_get_random_joke(self, mock_random_choice):
        """
        Tests that get_random_joke correctly formats a joke returned by random.choice.
        """
        # 1. Setup the mock for random.choice
        # Have it return a specific, known joke from our list
        mock_joke_tuple = ("Why did the computer go to the doctor?", "Because it had a virus!")
        mock_random_choice.return_value = mock_joke_tuple

        # 2. Run the function
        result = get_random_joke(JOKES)

        # 3. Assert the output is correctly formatted
        expected_string = "\nWhy did the computer go to the doctor?\nBecause it had a virus!"
        self.assertEqual(result, expected_string)


if __name__ == "__main__":
    unittest.main()