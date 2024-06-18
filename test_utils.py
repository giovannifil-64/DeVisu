import unittest
from unittest.mock import patch, MagicMock
from app import release_camera, initialize_camera, delete_all_images, reset_captured_image_path, get_user_by_otp, delete_user_by_otp

class TestUtilsFunctions(unittest.TestCase):

    @patch('app.camera')
    def test_release_camera(self, mock_camera):
        release_camera()
        mock_camera.camera.release.assert_called_once()

    @patch('app.VideoCamera')
    def test_initialize_camera_success(self, mock_video_camera):
        mock_instance = MagicMock()
        mock_video_camera.return_value = mock_instance
        mock_instance.camera_status = "Success"
        result = initialize_camera()
        self.assertEqual(result, "(app.initialize_camera)Camera initialized successfully.")

    @patch('app.VideoCamera')
    def test_initialize_camera_error(self, mock_video_camera):
        mock_instance = MagicMock()
        mock_video_camera.return_value = mock_instance
        mock_instance.camera_status = "Error"
        result = initialize_camera()
        self.assertEqual(result, "(app.initialize_camera)Error: Failed to open the camera.")

    # @patch('os.listdir', return_value=['image1.jpg', 'image2.jpg', 'file.txt'])
    # @patch('os.remove')
    # def test_delete_all_images(self, mock_remove, mock_listdir):
    #     delete_all_images()
    #     mock_remove.assert_any_call('image1.jpg')
    #     mock_remove.assert_any_call('image2.jpg')
    #     self.assertEqual(mock_remove.call_count, 2)

if __name__ == '__main__':
    unittest.main()