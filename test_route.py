import unittest
from unittest.mock import patch, MagicMock
from app import app, reset_globals

class TestRoutes(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        reset_globals()

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_add_name_get(self):
        response = self.app.get('/add_name')
        self.assertEqual(response.status_code, 200)

    @patch('app.set_global_name')
    def test_add_name_post(self, mock_set_global_name):
        data = {'username': 'John Doe'}
        response = self.app.post('/add_name', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        mock_set_global_name.assert_called_once_with('John Doe')

if __name__ == '__main__':
    unittest.main()