import unittest
import os

class TestMain(unittest.TestCase):
    def test_main(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_dir = os.path.join(os.path.dirname(current_dir), "fairy_tale")
        script_path = os.path.join(script_dir, "fairy_tale.py")
        os.system(f'python {script_path} -topics cat')
        self.assertTrue(os.path.exists(os.path.join(script_dir, "Fairy tales.pdf")))


if __name__ == '__main__':
    unittest.main()