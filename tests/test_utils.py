import os
import importlib.machinery

from pathlib import Path
from unittest import TestCase, mock, main as unittest_main

utilsLoader = importlib.machinery.SourceFileLoader(
    'utils', os.path.dirname(Path(__file__).absolute()) + '/../src/utils.py')
utils = utilsLoader.load_module("utils")


class Testutils(TestCase):
    @mock.patch('subprocess.run')
    def test_copy_disk_vmdk2raw(self, mock_run):
        utils.VmdkToRaw().copy('/tmp/src', '/tmp/dst')
        self.assertTrue(mock_run.called)
        mock_run.assert_called_once_with(
            ['/usr/bin/qemu-img', 'convert', '-f', 'vmdk', '-O', 'raw', '/tmp/src', '/tmp/dst'], check=True)

    @mock.patch('subprocess.run')
    def test_copy_disk_raw2vmdk(self, mock_run):
        utils.RawToVmdk().copy('/tmp/src', '/tmp/dst')
        self.assertTrue(mock_run.called)
        mock_run.assert_called_once_with(
            ['/usr/bin/qemu-img', 'convert', '-f', 'raw', '-O', 'vmdk', '/tmp/src', '/tmp/dst'], check=True)

    @mock.patch('subprocess.run')
    def test_copy_disk_qcow2toraw(self, mock_run):
        utils.to_raw('qcow2').copy('/tmp/src', '/tmp/dst')
        self.assertTrue(mock_run.called)
        mock_run.assert_called_once_with(
            ['/usr/bin/qemu-img', 'convert', '-f', 'qcow2', '-O', 'raw', '/tmp/src', '/tmp/dst'], check=True)

    @mock.patch('subprocess.run')
    def test_copy_disk_rawtoqcow2(self, mock_run):
        utils.RawToQcow2().copy('/tmp/src', '/tmp/dst')
        self.assertTrue(mock_run.called)
        mock_run.assert_called_once_with(
            ['/usr/bin/qemu-img', 'convert', '-f', 'raw', '-O', 'qcow2', '/tmp/src', '/tmp/dst'], check=True)


if __name__ == '__main__':
    unittest_main()
