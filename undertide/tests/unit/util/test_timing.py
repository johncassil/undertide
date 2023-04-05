import unittest
from src.timing import log_timing
import time


class TestTiming(unittest.TestCase):
    def test_log_timing_decorator(self):
        @log_timing
        def sample_function():
            time.sleep(1)
            return "test"

        result = sample_function()
        self.assertEqual(result, "test")


if __name__ == "__main__":
    unittest.main()
