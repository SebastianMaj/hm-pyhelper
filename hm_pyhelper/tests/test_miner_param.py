from hm_pyhelper.miner_param import retry_get_region, await_spi_available, REGION_OVERRIDE_KEY
import unittest
from unittest.mock import mock_open, patch
import os


class TestMinerParam(unittest.TestCase):
    def test_get_region_from_override(self):
        os.environ[REGION_OVERRIDE_KEY] = 'foo'
        self.assertEqual(retry_get_region("foo/"), 'foo')

    @patch("builtins.open", new_callable=mock_open, read_data="ZZ111\n")
    def test_get_region_from_miner(self, _):
        os.environ[REGION_OVERRIDE_KEY] = ''
        self.assertEqual(retry_get_region("foo/"), 'ZZ111')

    @patch("os.path.exists", return_value=True)
    def test_is_spi_available(self, _):
        self.assertTrue(await_spi_available("spiXY.Z"))
