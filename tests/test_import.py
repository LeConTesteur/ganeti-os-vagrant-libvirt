import os
import importlib.machinery
import tempfile

from pathlib import Path, PosixPath
from unittest import TestCase, mock, main as unittest_main

smcLoader = importlib.machinery.SourceFileLoader(
    'import', os.path.dirname(Path(__file__).absolute()) + '/../src/import')
import_script = smcLoader.load_module("import")
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



class TestImportMain(TestCase):

    @mock.patch('import.read_data')
    @mock.patch.object(tempfile, 'NamedTemporaryFile')
    @mock.patch('subprocess.run')
    @mock.patch.dict(os.environ, {'IMPORT_DEVICE': '/import/test'})
    def test_main_with_compress(self, mock_run, mock_tempfile, mock_read_data):
        mock_tmpfile_enter = mock_named_temporary_file('/tmp/import-test')
        mock_tempfile.return_value = mock_tmpfile_enter
        import_script.main()
        self.assertTrue(mock_run.called)
        self.assertTrue(mock_tempfile.called)
        self.assertTrue(mock_read_data.called)
        mock_run.assert_has_calls([
            mock.call(['/usr/bin/qemu-img', 'convert', '-f', 'qcow2', '-O', 'raw', mock_tmpfile_enter.name, '/import/test'], check=True),
        ])
        mock_read_data.assert_has_calls([
            mock.call(mock_tmpfile_enter)
        ])

    @mock.patch('import.read_data')
    @mock.patch.object(tempfile, 'NamedTemporaryFile')
    @mock.patch('subprocess.run')
    @mock.patch.dict(os.environ, {'OSP_EXPORT_IMPORT_FORMAT': 'vmdk', 'IMPORT_DEVICE': '/import/test'})
    def test_main_with_qcow2_format(self, mock_run, mock_tempfile, mock_read_data):
        mock_tmpfile_enter = mock_named_temporary_file('/tmp/import-test')
        mock_tempfile.return_value = mock_tmpfile_enter
        import_script.main()
        self.assertTrue(mock_run.called)
        self.assertTrue(mock_tempfile.called)
        self.assertTrue(mock_read_data.called)
        mock_run.assert_has_calls([
            mock.call(['/usr/bin/qemu-img', 'convert', '-f', 'vmdk', '-O', 'raw', mock_tmpfile_enter.name, '/import/test'], check=True),
        ])
        mock_read_data.assert_has_calls([
            mock.call(mock_tmpfile_enter)
        ])

    @mock.patch('import.read_data')
    @mock.patch('subprocess.run')
    @mock.patch.dict(os.environ, {'OSP_EXPORT_IMPORT_FORMAT': 'test', 'IMPORT_DEVICE': '/import/test'})
    def test_main_with_unsupported_format(self, mock_run, mock_read_data):
        with self.assertRaises(diskUtils.UnsupportedDiskFormat):
          import_script.main()
        self.assertTrue(mock_run.not_called)
        self.assertTrue(mock_read_data.not_called)

    @mock.patch('import.read_data')
    @mock.patch.object(tempfile, 'NamedTemporaryFile')
    @mock.patch.object(tempfile, 'SpooledTemporaryFile')
    @mock.patch('subprocess.run')
    @mock.patch.dict(os.environ, {'OSP_EXPORT_IMPORT_MEMORY_TEMPORARY_DIR':'/test/', 'IMPORT_DEVICE': '/import/test'})
    def test_main_with_spooled_option(self, mock_run, mock_tempfile_spooled, mock_tempfile_named, mock_read_data):
        mock_tempfile_named_enter = mock_named_temporary_file('/tmp/export-test')
        mock_tempfile_named.return_value = mock_tempfile_named_enter
        import_script.main()
        self.assertTrue(mock_tempfile_named.called)
        mock_tempfile_named.assert_has_calls([
            mock.call(mode='wb', dir='/test/'),
        ])

if __name__ == '__main__':
    unittest_main()
