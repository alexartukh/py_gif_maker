import os
import sys
import hashlib
import unittest

# make modules from the "src" folder importable
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(TESTS_DIR)
sys.path.insert(0, os.path.join(PROJECT_DIR, "src"))

import gen_f

# user id 0 : GIF files go to /static/0/
TEST_UID = 0

class TestFGenerator(unittest.TestCase):

    # перед каждым тестом
    def setUp(self):
        self.digest = hashlib.md5("TESTING".encode("utf-8")).digest()
        self.created_files = []

    # после каждого теста, даже если тест упал
    def tearDown(self):
        # remove GIF files created by the test
        for path in self.created_files:
            if os.path.exists(path):
                os.remove(path)

    # makes one GIF and returns its URL path and MD5 of its content
    # the hash is taken right away : a GIF with the same seed made in the same second
    # gets the same file name and overwrites this file
    def _make_gif_and_get_hash(self, seed):
        digest = hashlib.md5(seed.encode("utf-8")).digest()

        generator = gen_f.FGenerator()
        result = generator.make_gif(digest, TEST_UID)

        full_path = PROJECT_DIR + result
        self.created_files.append(full_path)
        self.assertTrue(os.path.isfile(full_path), "file was not created: " + full_path)

        with open(full_path, "rb") as f:
            content_hash = hashlib.md5(f.read()).hexdigest()

        return result, content_hash

    # same type, different seeds : GIF files must be different
    def test_make_2_different_gifs(self):
        result_a, content_hash_a = self._make_gif_and_get_hash("SEED A")
        result_b, content_hash_b = self._make_gif_and_get_hash("SEED B")

        self.assertNotEqual(result_a, result_b, "both GIFs have the same file name")
        self.assertNotEqual(content_hash_a, content_hash_b, "both GIFs have the same content: " + content_hash_a)

    # same type, same seed : GIF files must be identical
    def test_make_2_same_gifs(self):
        _, content_hash_a = self._make_gif_and_get_hash("SEED A")
        _, content_hash_b = self._make_gif_and_get_hash("SEED A")

        self.assertEqual(content_hash_a, content_hash_b, "GIFs with the same seed have different content")

if __name__ == "__main__":
    unittest.main()
