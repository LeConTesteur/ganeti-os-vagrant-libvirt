import os
import importlib
import requests_mock
import packaging


from pathlib import Path
from unittest import TestCase, mock, main as unittest_main
from packaging import version as packagingVersion

metadataLoader = importlib.machinery.SourceFileLoader(
    'metadata', os.path.dirname(Path(__file__).absolute()) + '/../src/vagrant_metadata.py')
metadata = metadataLoader.load_module()

class TestVagrantMetadataClass(TestCase):

    def test_version_have_provider(self):
        version = metadata.Version('1.0.0', providers=[
            metadata.Provider("libvirt", "", "", ""), 
            metadata.Provider("virtualbox", "", "", "")
        ])
        self.assertTrue(version.have_provider('libvirt'))
        self.assertFalse(version.have_provider('hyperV'))

    def test_version_empty_provider(self):
        version = metadata.Version('1.0.0')
        self.assertFalse(version.have_provider('libvirt'))
        self.assertEqual(version.provider('libvirt'), None)

    def test_version_provider(self):
        p = metadata.Provider("libvirt", "", "", "")
        version = metadata.Version('1.0.0', providers=[
            p,
            metadata.Provider("virtualbox", "", "", "")
        ])
        self.assertEqual(version.provider('libvirt'), p)
        
    def test_version_compare_attribut_version(self):
        version = metadata.Version('1.0.0')
        self.assertFalse(version.version < metadata.Version('0.0.1').version)
        self.assertFalse(version.version > metadata.Version('1.0.1').version)
        self.assertTrue(version.version == metadata.Version('1.0.0').version)

    def test_version_compare(self):
        version = metadata.Version('1.0.0', [])
        self.assertFalse(version < metadata.Version('0.0.1'))
        self.assertFalse(version > metadata.Version('1.0.1'))
        self.assertTrue(version == metadata.Version('1.0.0'))

    def test_metadata_versions_with_provider(self):
        meta = metadata.Metadata('test', versions=[
            metadata.Version('1.1.0', providers=[
                metadata.Provider("libvirt", "", "", ""), 
                metadata.Provider("virtualbox", "", "", "")
            ]),
            metadata.Version('1.0.0', providers=[
                metadata.Provider("libvirt", "", "", ""), 
                metadata.Provider("virtualbox", "", "", "")
            ]),
            metadata.Version('1.2.0', providers=[
                metadata.Provider("virtualbox", "", "", "")
            ])
        ])
        versions = meta.versions_with_provider('libvirt')
        self.assertEqual(len(versions),2)
        self.assertListEqual(list(versions.keys()), [
            metadata.Version("1.1.0").version,
            metadata.Version("1.0.0").version
        ])
        versions = meta.versions_with_provider('virtualbox')
        self.assertEqual(len(versions),3)
        self.assertListEqual(list(sorted(versions.keys())), [
            metadata.Version("1.0.0").version,
            metadata.Version("1.1.0").version,
            metadata.Version("1.2.0").version
        ])
        versions = meta.versions_with_provider('hyperV')
        self.assertEqual(len(versions),0)
        self.assertListEqual(list(versions.keys()), [])

class TestVagrantMetadata(TestCase):
    @requests_mock.Mocker()
    def test_fetch(self, mock):
        mock.get('http://test.com', text='''
{
  "description":"Test",
  "short_description":"description",
  "name":"test",
  "versions":[
     {
        "version":"1.0.1",
        "status":"active",
        "description_html":"<h1></h1>",
        "description_markdown":"",
        "providers":[
           {
              "name":"libvirt",
              "url":"https://test.com/test.box",
              "checksum":null,
              "checksum_type":null
           },
           {
              "name":"virtualbox",
              "url":"https://test.com/test.box",
              "checksum":null,
              "checksum_type":null
           }
        ]
     },
     {
        "version":"1.0.0",
        "status":"active",
        "description_html":"<h1></h1>",
        "description_markdown":"",
        "providers":[
           {
              "name":"libvirt",
              "url":"https://test.com/test.box",
              "checksum":null,
              "checksum_type":null
           },
           {
              "name":"virtualbox",
              "url":"https://test.com/test.box",
              "checksum":null,
              "checksum_type":null
           }
        ]
     }
  ]
}
        ''')
        meta = metadata.fetch('http://test.com')
        self.assertEqual(len(meta.versions_with_provider('libvirt')),2)
        self.assertEqual(len(meta.versions_with_provider('virtualbox')),2)
        self.assertEqual(meta.name, 'test')
        self.assertEqual(meta.description, 'Test')
        self.assertEqual(meta['1.0.0'].provider('libvirt').url, "https://test.com/test.box")

    def test_forge_metadata_url_error(self):
        with self.assertRaises(Exception):
            metadata.forge_metadata_url('toto')
        with self.assertRaises(Exception):
            metadata.forge_metadata_url()

    def test_forge_metadata_url_work(self):
        self.assertEqual(metadata.forge_metadata_url('name/box'), 'https://app.vagrantup.com/name/boxes/box')
        self.assertEqual(metadata.forge_metadata_url('name/box/toto'), 'https://app.vagrantup.com/name/boxes/box')

    def fetch_box_url_error(self):
        with self.assertRaises(Exception):
            metadata.fetch_box_url()

    @mock.patch('metadata.fetch')
    @mock.patch('metadata.url_box')
    @mock.patch('metadata.forge_metadata_url')
    def fetch_box_url_with_metadata_url(self, mock_fetch, mock_url_box, mock_forge):
        mock_fetch.return_value = 'fetch_return'
        mock_url_box.return_value = 'url_return'
        mock_forge.return_value = 'http://forge.com'
        self.assertEqual(metadata.fetch_box_url(metadata_url='http://test.com'), mock_url_box.return_value)
        mock_forge.assert_not_called()
        mock_fetch.assert_called_with('http://test.com')
        mock_url_box.assert_called_with(mock_fetch.return_value, None)

    @mock.patch('metadata.fetch')
    @mock.patch('metadata.url_box')
    @mock.patch('metadata.forge_metadata_url')
    def fetch_box_url_with_name_and_version(self, mock_fetch, mock_url_box, mock_forge):
        mock_fetch.return_value = 'fetch_return'
        mock_url_box.return_value = 'url_return'
        mock_forge.return_value = 'http://forge.com'
        self.assertEqual(metadata.fetch_box_url(name='name/box', version='1.1.1'), mock_url_box.return_value)
        mock_forge.assert_called_with('name/box')
        mock_fetch.assert_called_with(mock_forge.return_value)
        mock_url_box.assert_called_with(mock_fetch.return_value, '1.1.1')

    def test_fetch_version_with_specify_version(self):
        self.assertEqual(
            metadata.fetch_version(None, '1.1.1'),
            packagingVersion.Version('1.1.1')
        )


    def test_fetch_version_with_last_version(self):
        versions = {
            packagingVersion.Version('1.1.1'): metadata.Version('1.1.0', providers=[
                metadata.Provider("libvirt", "", "", ""), 
                metadata.Provider("virtualbox", "", "", "")
            ]),
            packagingVersion.Version('1.0.0'): metadata.Version('1.0.0', providers=[
                metadata.Provider("libvirt", "", "", ""), 
                metadata.Provider("virtualbox", "", "", "")
            ]),
            packagingVersion.Version('1.2.0'): metadata.Version('1.2.0', providers=[
                metadata.Provider("virtualbox", "", "", "")
            ])
        }
        self.assertEqual(
            metadata.fetch_version(versions, None),
            packagingVersion.Version('1.2.0')
        )

    def test_url_box_error(self):
        meta = metadata.Metadata('test', versions=[
            metadata.Version('1.1.0', providers=[
                metadata.Provider("libvirt", "", "", ""), 
                metadata.Provider("virtualbox", "", "", "")
            ])
        ])
        with self.assertRaises(Exception):
            metadata.url_box(meta, '0.0.1')

    def test_url_box_error(self):
        meta = metadata.Metadata('test', versions=[
            metadata.Version('1.1.0', providers=[
                metadata.Provider("libvirt", "http://libvirt.com", "", ""),
                metadata.Provider("virtualbox", "", "", "")
            ]),
            metadata.Version('1.0.0', providers=[
                metadata.Provider("libvirt", "", "", ""), 
                metadata.Provider("virtualbox", "", "", "")
            ]),
            metadata.Version('1.2.0', providers=[
                metadata.Provider("virtualbox", "http://virtualbox.com", "", "")
            ])
        ])
        self.assertEqual(
            metadata.url_box(meta, '1.1.0'),
            'http://libvirt.com'
        )
        self.assertEqual(
            metadata.url_box(meta,  provider='virtualbox'),
            'http://virtualbox.com'
        )
