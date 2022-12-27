import os
import importlib.machinery
import tempfile

from pathlib import Path, PosixPath
from unittest import TestCase, mock, main as unittest_main

smcLoader = importlib.machinery.SourceFileLoader(
    'export', os.path.dirname(Path(__file__).absolute()) + '/../src/export')
export = smcLoader.load_module("export")
diskUtilsLoader = importlib.machinery.SourceFileLoader(
    'disk_utils', os.path.dirname(Path(__file__).absolute()) + '/../src/disk_utils.py')
diskUtils = diskUtilsLoader.load_module('disk_utils')

def mock_named_temporary_file(tmpname):
    class MockNamedTemporaryFile(object):
        def __init__(self, *args, **kwargs):
            self.name = tmpname

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            pass

    return MockNamedTemporaryFile()



class TestExportMain(TestCase):

    @mock.patch('export.send_data')
    @mock.patch.object(tempfile, 'NamedTemporaryFile')
    @mock.patch('subprocess.run')
    @mock.patch.dict(os.environ, {'OSP_EXPORT_COMPRESS':'TRUE', 'EXPORT_DEVICE': '/export/test'})
    def test_main_with_compress(self, mock_run, mock_tempfile, mock_send_data):
        mock_tmpfile_enter = mock_named_temporary_file('/tmp/export-test')
        mock_tempfile.return_value = mock_tmpfile_enter
        export.main()
        self.assertTrue(mock_run.called)
        self.assertTrue(mock_tempfile.called)
        self.assertTrue(mock_send_data.called)
        mock_run.assert_has_calls([
            mock.call(['/usr/bin/qemu-img', 'convert', '-c', '-f', 'raw', '-O', 'vmdk', '/export/test', mock_tmpfile_enter.name], check=True),
        ])
        mock_send_data.assert_has_calls([
            mock.call(mock_tmpfile_enter)
        ])

    @mock.patch('export.send_data')
    @mock.patch.object(tempfile, 'NamedTemporaryFile')
    @mock.patch('subprocess.run')
    @mock.patch.dict(os.environ, {'OSP_EXPORT_IMPORT_FORMAT':'qcow2', 'EXPORT_DEVICE': '/export/test'})
    def test_main_with_qcow2_format(self, mock_run, mock_tempfile, mock_send_data):
        mock_tmpfile_enter = mock_named_temporary_file('/tmp/export-test')
        mock_tempfile.return_value = mock_tmpfile_enter
        export.main()
        self.assertTrue(mock_run.called)
        self.assertTrue(mock_tempfile.called)
        self.assertTrue(mock_send_data.called)
        mock_run.assert_has_calls([
            mock.call(['/usr/bin/qemu-img', 'convert', '-f', 'raw', '-O', 'qcow2', '/export/test', mock_tmpfile_enter.name], check=True),
        ])
        mock_send_data.assert_has_calls([
            mock.call(mock_tmpfile_enter)
        ])


    @mock.patch('export.send_data')
    @mock.patch('subprocess.run')
    @mock.patch.dict(os.environ, {'OSP_EXPORT_IMPORT_FORMAT':'test', 'EXPORT_DEVICE': '/export/test'})
    def test_main_with_unsupported_format(self, mock_run, mock_send_data):
        with self.assertRaises(diskUtils.UnsupportedDiskFormat):
          export.main()
        self.assertTrue(mock_run.not_called)
        self.assertTrue(mock_send_data.not_called)

    @mock.patch('export.send_data')
    @mock.patch.object(tempfile, 'NamedTemporaryFile')
    @mock.patch('subprocess.run')
    @mock.patch.dict(os.environ, {'OSP_EXPORT_IMPORT_PREFIX_TEMPORARY_FILE':'/test/', 'EXPORT_DEVICE': '/export/test'})
    def test_main_with_spooled_option(self, mock_run, mock_tempfile_named, mock_send_data):
        mock_tempfile_named_enter = mock_named_temporary_file('/tmp/export-test')
        mock_tempfile_named.return_value = mock_tempfile_named_enter
        export.main()
        self.assertTrue(mock_tempfile_named.called)
        mock_tempfile_named.assert_has_calls([
            mock.call(mode='rb', prefix='/test/'),
        ])

if __name__ == '__main__':
    unittest_main()
