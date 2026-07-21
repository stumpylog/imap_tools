import unittest
from unittest.mock import patch

from tests.utils import get_test_mailbox_config


class GetTestMailboxConfigSkipTest(unittest.TestCase):
    def test_skips_when_credentials_file_missing(self):
        with patch('os.path.exists', return_value=False):
            with self.assertRaises(unittest.SkipTest):
                get_test_mailbox_config('YANDEX')


if __name__ == "__main__":
    unittest.main()
