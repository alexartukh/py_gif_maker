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

    def check_make_gif(self, generator_type):
        generator = gen_f.FGenerator(generator_type)
        result = generator.make_gif(self.digest, TEST_UID)

        # make_gif returns a URL path like /static/0/<name>.gif
        self.assertTrue(result.startswith("/static/0/"), "unexpected path: " + result)
        self.assertTrue(result.endswith(".gif"), "unexpected path: " + result)

        full_path = PROJECT_DIR + result
        self.created_files.append(full_path)

        self.assertTrue(os.path.isfile(full_path), "file was not created: " + full_path)
        self.assertGreater(os.path.getsize(full_path), 0, "file is empty: " + full_path)

    # unittest считает тестом только метод, имя которого начинается с test
    
    def test_make_gif_type_1(self):
        self.check_make_gif(1)

    def test_make_gif_type_2(self):
        self.check_make_gif(2)

    def test_make_gif_type_3(self):
        self.check_make_gif(3)

    def test_make_gif_type_4(self):
        self.check_make_gif(4)

    def test_make_gif_type_5(self):
        self.check_make_gif(5)

    # unknown type : constructor must raise ValueError
    def test_make_gif_type_99(self):
        with self.assertRaises(ValueError):
            self.check_make_gif(99)

    def test_make_gif_type_qq(self):
        with self.assertRaises(ValueError):
            self.check_make_gif('qq')

if __name__ == "__main__":
    unittest.main()
