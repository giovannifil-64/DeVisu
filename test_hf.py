import unittest
import numpy as np
from unittest.mock import patch, mock_open
import hf_vectorizer

class TestHFVectorizer(unittest.TestCase):

    def test_get_face_vector_valid_image(self):
        with patch('cv2.imread', return_value=np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)):
            with patch('face_recognition.face_locations', return_value=[(10, 30, 60, 20)]):
                with patch('face_recognition.face_encodings', return_value=[np.random.rand(128)]):
                    vector = hf_vectorizer.get_face_vector('test.jpeg')
                    self.assertIsInstance(vector, np.ndarray)
                    self.assertEqual(vector.shape, (128,))

    def test_get_face_vector_no_face(self):
        with patch('cv2.imread', return_value=np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)):
            with patch('face_recognition.face_locations', return_value=[]):
                vector = hf_vectorizer.get_face_vector('test.jpeg')
                self.assertIsNone(vector)

    def test_get_face_vector_invalid_path(self):
        with patch('cv2.imread', return_value=None):
            vector = hf_vectorizer.get_face_vector('invalid.jpeg')
            self.assertIsNone(vector)

    def test_compare_vectors_equal(self):
        vector1 = np.random.rand(128)
        vector2 = vector1.copy()
        result = hf_vectorizer.compare_vectors(vector1, vector2)
        self.assertTrue(result)

    def test_compare_vectors_different(self):
        vector1 = np.random.rand(128)
        vector2 = np.random.rand(128)
        result = hf_vectorizer.compare_vectors(vector1, vector2)
        self.assertFalse(result)

    def test_compare_vectors_none(self):
        vector1 = np.random.rand(128)
        result = hf_vectorizer.compare_vectors(vector1, None)
        self.assertFalse(result)

    def test_base64_encoder(self):
        vector = np.random.rand(128)
        base64_string = hf_vectorizer.base64_encoder(vector)
        self.assertIsInstance(base64_string, str)

    def test_base64_decoder(self):
        vector = np.random.rand(128)
        base64_string = hf_vectorizer.base64_encoder(vector)
        decoded_vector = hf_vectorizer.base64_decoder(base64_string)
        self.assertTrue(np.allclose(vector, decoded_vector))

    def test_base64_decoder_invalid_input(self):
        invalid_string = 'invalid_string'
        with self.assertRaises(ValueError):
            hf_vectorizer.base64_decoder(invalid_string)

    def test_get_face_vector_exception(self):
        with patch('cv2.imread', side_effect=Exception('Test exception')):
            vector = hf_vectorizer.get_face_vector('test.jpeg')
            self.assertIsNone(vector)

    def test_compare_vectors_empty(self):
        vector1 = np.array([])
        vector2 = np.random.rand(128)
        result = hf_vectorizer.compare_vectors(vector1, vector2)
        self.assertFalse(result)

    def test_base64_encoder_empty(self):
        vector = np.array([])
        base64_string = hf_vectorizer.base64_encoder(vector)
        self.assertEqual(base64_string, '')

if __name__ == '__main__':
    unittest.main()