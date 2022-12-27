import os
import importlib.machinery

from pathlib import Path
from unittest import TestCase, mock, main as unittest_main

diskUtilsLoader = importlib.machinery.SourceFileLoader(
    'disk_utils', os.path.dirname(Path(__file__).absolute()) + '/../src/disk_utils.py')
diskUtils = diskUtilsLoader.load_module('disk_utils')


class Testutils(TestCase):
    @mock.patch('subprocess.run')
    def test_copy_disk_vmdk2raw(self, mock_run):
        diskUtils.copy_vmdk_to_raw('/tmp/src', '/tmp/dst')
        self.assertTrue(mock_run.called)
        mock_run.assert_called_once_with(
            ['/usr/bin/qemu-img', 'convert', '-f', 'vmdk', '-O', 'raw', '/tmp/src', '/tmp/dst'], check=True)

    @mock.patch('subprocess.run')
    def test_copy_disk_raw2vmdk(self, mock_run):
        diskUtils.copy_raw_to_vmdk('/tmp/src', '/tmp/dst')
        self.assertTrue(mock_run.called)
        mock_run.assert_called_once_with(
            ['/usr/bin/qemu-img', 'convert', '-f', 'raw', '-O', 'vmdk', '/tmp/src', '/tmp/dst'], check=True)

    @mock.patch('subprocess.run')
    def test_copy_disk_qcow2toraw(self, mock_run):
        diskUtils.to_raw_from('qcow2')('/tmp/src', '/tmp/dst')
        self.assertTrue(mock_run.called)
        mock_run.assert_called_once_with(
            ['/usr/bin/qemu-img', 'convert', '-f', 'qcow2', '-O', 'raw', '/tmp/src', '/tmp/dst'], check=True)

    @mock.patch('subprocess.run')
    def test_copy_disk_rawtoqcow2(self, mock_run):
        diskUtils.copy_raw_to_qcow2('/tmp/src', '/tmp/dst')
        self.assertTrue(mock_run.called)
        mock_run.assert_called_once_with(
            ['/usr/bin/qemu-img', 'convert', '-f', 'raw', '-O', 'qcow2', '/tmp/src', '/tmp/dst'], check=True)

    @mock.patch('subprocess.run')
    def test_copy_disk_rawtoqcow2_with_compress(self, mock_run):
        diskUtils.copy_raw_to_qcow2('/tmp/src', '/tmp/dst', compress=True)
        self.assertTrue(mock_run.called)
        mock_run.assert_called_once_with(
            ['/usr/bin/qemu-img', 'convert', '-c', '-f', 'raw', '-O', 'qcow2', '/tmp/src', '/tmp/dst'], check=True)

    def test_is_supported_disk_format(self):
        for good_format in ["raw", "qcow2", "vmdk"]:
            self.assertTrue(diskUtils.is_supported_disk_format(good_format))
        self.assertFalse(diskUtils.is_supported_disk_format("test"))

    def test_raise_if_unsupported_disk_format(self):
        for good_format in ["raw", "qcow2", "vmdk"]:
            self.assertIsNone(diskUtils.raise_if_unsupported_disk_format(good_format))
        with self.assertRaises(diskUtils.UnsupportedDiskFormat):
            self.assertFalse(diskUtils.raise_if_unsupported_disk_format("test"))


if __name__ == '__main__':
    unittest_main()
