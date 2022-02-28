from logging import raiseExceptions
import os
import importlib.machinery
import subprocess
import tempfile
import json
import requests

from pathlib import Path, PosixPath
from unittest import TestCase, mock, main as unittest_main

smcLoader = importlib.machinery.SourceFileLoader(
    'create', os.path.dirname(Path(__file__).absolute()) + '/../src/create')
create = smcLoader.load_module()


class TestCreateFunction(TestCase):

    def test_check_env_var_without_url(self):
        with self.assertRaises(create.EnvException):
            create.get_env_var()

    @mock.patch.dict(os.environ, {"OSP_BOX_URL": "test"})
    def test_check_env_var_with_bad_type(self):
        create.get_env_var()

    @mock.patch.dict(os.environ, {"DISK_COUNT": "2", "DISK_0_PATH": "p0","DISK_1_PATH": "p1"})
    def test_ganeti_disks(self):
        self.assertListEqual(create.ganeti_disks(), 
            [ "p0", "p1"]
        )

    def test_box_disks_with_empty_metadata(self):
        self.assertListEqual(
            list(create.box_disks({})),
            ['box.img']
        )

    def test_box_disks_with_3_disks(self):
        self.assertListEqual(
            list(create.box_disks(
                {'disks': [{'path':'p0'}, {}, {'path':'p2'}]})
            ),
            ['p0', 'box_1.img', 'p2']
        )

    def test_extract_box_disks_with_empty_metadata(self):
        self.assertListEqual(
            list(create.extract_box_disks({}, '/tmp')),
            [PosixPath('/tmp/box.img')]
        )

    @mock.patch.dict(os.environ, {"DISK_COUNT": "2"})
    def test_check_disks_count_when_have_not_same_count(self):
        with self.assertRaises(create.NbDiskException):
            create.check_disks_count(
                {'disks': [{'path':'p0'}, {}, {'path':'p2'}]}
            )

tmp_test_dir = '/tmp/unittest_os_ganeti'
tmp_test_dir_for_main = '/tmp/unittest_os_ganeti_main'


def fake_mkdtemp(*_):
    return tmp_test_dir_for_main  # remove via TemporaryDirectory


fake_environ = {"DISK_COUNT": "2", "DISK_0_PATH": f'{tmp_test_dir}/disk0.raw',
                "DISK_1_PATH": f'{tmp_test_dir}/disk1.raw'}


@mock.patch.dict(os.environ, fake_environ)
class TestCreateMain(TestCase):
    def setUp(self) -> None:
        test_box = f'{tmp_test_dir}/test.box'
        relative_img_paths = ['box_0.img', 'box_1.img']
        img_files = [f'{tmp_test_dir}/{f}' for f in relative_img_paths]
        relative_metadata = 'metadata.json'
        metadata_file = f'{tmp_test_dir}/{relative_metadata}'
        self.tmp_test_files = [*img_files, test_box, metadata_file]
        os.makedirs(tmp_test_dir, exist_ok=True)
        os.makedirs(tmp_test_dir_for_main, exist_ok=True)
        with open(metadata_file, 'w') as f:
            f.write(json.dumps(
                {'disks': [
                    {
                        'name': 'disk0'
                    },
                    {
                        'name': 'disk1'
                    }
                ]}
            ))

        subprocess.run(['touch', *img_files], check=True)
        subprocess.run(['tar', '-cf', test_box, '-C',
                       tmp_test_dir, relative_metadata, *relative_img_paths], check=True)
    def tearDown(self) -> None:
        for f in self.tmp_test_files:
            os.remove(f)
        os.removedirs(tmp_test_dir)

    def test_main_with_error(self):
        with self.assertRaises(requests.exceptions.MissingSchema):
            create.main('test')

    @mock.patch('subprocess.run')
    @mock.patch('tempfile.mkdtemp', fake_mkdtemp)
    def test_main_with_box(self, mock_run):
        create.main(f'file://{tmp_test_dir}/test.box')
        self.assertTrue(mock_run.called)
        call_args = [
            mock.call(['/usr/bin/qemu-img', 'convert', '-f', 'qcow2', '-O', 'raw', PosixPath(
                f'{tmp_test_dir_for_main}/box_0.img'), '/tmp/unittest_os_ganeti/disk0.raw'], check=True),
            mock.call(['/usr/bin/qemu-img', 'convert', '-f', 'qcow2', '-O', 'raw', PosixPath(
                f'{tmp_test_dir_for_main}/box_1.img'), '/tmp/unittest_os_ganeti/disk1.raw'], check=True)
        ]
        mock_run.assert_has_calls(call_args, any_order=True)
        self.assertFalse(os.path.exists(tmp_test_dir_for_main))

if __name__ == '__main__':
    unittest_main()
