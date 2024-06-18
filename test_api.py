import unittest
from unittest.mock import patch, MagicMock
from app import get_user_by_otp, delete_user_by_otp

class TestAPICalls(unittest.TestCase):

    @patch('app.requests.get')
    def test_get_user_by_otp_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 1, 'name': 'John Doe', 'otp': '123456', 'vector': 'base64vector'}
        mock_get.return_value = mock_response

        user = get_user_by_otp('123456')
        self.assertEqual(user, {'id': 1, 'name': 'John Doe', 'otp': '123456', 'vector': 'base64vector'})

    @patch('app.requests.get')
    def test_get_user_by_otp_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        user = get_user_by_otp('invalid_otp')
        self.assertIsNone(user)

    @patch('app.requests.get')
    @patch('app.requests.delete')
    def test_delete_user_by_otp_success(self, mock_delete, mock_get):
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {'id': 1, 'name': 'John Doe', 'otp': '123456', 'vector': 'base64vector'}
        mock_get.return_value = mock_get_response

        mock_delete_response = MagicMock()
        mock_delete_response.status_code = 200
        mock_delete.return_value = mock_delete_response

        delete_user_by_otp('123456')
        mock_delete.assert_called_once()
        
    # Test for delete_user_by_otp when user is not found
    @patch('app.requests.get')
    @patch('app.requests.delete')
    def test_delete_user_by_otp_not_found(self, mock_delete, mock_get):
        mock_get_response = MagicMock()
        mock_get_response.status_code = 404
        mock_get.return_value = mock_get_response

        delete_user_by_otp('invalid_otp')
        mock_delete.assert_not_called()
        
if __name__ == '__main__':
    unittest.main()