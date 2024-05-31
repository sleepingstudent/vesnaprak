"""Test module."""
import unittest
import unittest.mock as mock

from mood.client import main
from io import StringIO


class TestClient(unittest.TestCase):
    """Test client."""

    def test_0(self):
        """Zero test."""
        cmd = "addmon tux\nright\nleft\nattack tux"
        with (
                mock.patch('sys.stdin', StringIO(cmd)),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('mood.client.recieve', return_value=True)
             ):
            main()
            snd_all = socket_mock.mock_calls[8].args[0].decode()
            self.assertEqual(snd_all, 'addmon tux\n')
            snd_all = socket_mock.mock_calls[9].args[0].decode()
            self.assertEqual(snd_all, 'move 1 0\n')
            snd_all = socket_mock.mock_calls[10].args[0].decode()
            self.assertEqual(snd_all, 'move -1 0\n')
            snd_all = socket_mock.mock_calls[11].args[0].decode()
            self.assertEqual(snd_all, 'attack tux\n')

    def test_1(self):
        """First test."""
        cmd = "attack tux with axe\nattack tux with spear\nattack tux with sword\n"
        with (
                mock.patch('sys.stdin', StringIO(cmd)),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('mood.client.recieve', return_value=True)
             ):
            main()
            snd_all = socket_mock.mock_calls[8].args[0].decode()
            self.assertEqual(snd_all, 'attack tux with axe\n')
            snd_all = socket_mock.mock_calls[9].args[0].decode()
            self.assertEqual(snd_all, 'attack tux with spear\n')
            snd_all = socket_mock.mock_calls[10].args[0].decode()
            self.assertEqual(snd_all, 'attack tux with sword\n')

    def test_2(self):
        """Second test."""
        cmd = "movemonsters out\n"
        with (
                mock.patch('sys.stdin', StringIO(cmd)),
                mock.patch('builtins.print', autospec=True) as output_mock,
                mock.patch('socket.socket', autospec=True),
                mock.patch('mood.client.recieve', return_value=True)
             ):
            main()
            output_call = output_mock.mock_calls[1].args[0]
            self.assertEqual(output_call, 'Invalid command.')
