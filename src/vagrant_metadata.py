import requests
import json

from typing import List
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from packaging import version as packagingVersion
@dataclass_json
@dataclass(eq=True, order=True)
class Provider:
  name: str
  url: str
  checksum_type: str = field(default="")
  checksum: str = field(default="")

@dataclass_json
@dataclass(eq=True, order=True)
class Version:
  version: str = field(compare=True)
  status: str = field(compare=False, default="active")
  description_html: str = field(compare=False, default="")
  description_markdown: str = field(compare=False, default="")
  providers: List[Provider] = field(default_factory=list, compare=False)
  _version: str = field(init=False, default='', compare=False)

  def have_provider(self, provider: str) -> bool:
    return any(filter(lambda p:p.name == provider, self.providers))

  def provider(self, provider: str) -> Provider:
    for p in self.providers:
      if p.name == provider:
        return p
    return None

  @property
  def version(self):
    return self._version

  @version.setter
  def version(self, v):
    self._version = packagingVersion.Version(v)

@dataclass_json
@dataclass
class Metadata:
  name: str
  description: str = field(compare=False, default="")
  short_description: str = field(compare=False, default="")
  versions: List[Version] = field(default_factory=list)

  def versions_as_dict(self) -> dict:
    return {e.version: e for e in self.versions}

  def versions_with_provider(self, provider: str) -> dict:
    return {e.version: e for e in filter(lambda v: v.have_provider(provider), self.versions)}

  def __getitem__(self, v):
    if isinstance(v, packagingVersion.Version):
      return self.versions_as_dict()[v]
    return self.versions_as_dict()[packagingVersion.Version(v)]

def fetch(url: str) -> Metadata:
  r = requests.session().get(url)
  return Metadata.from_json(r.content)


def fetch_version(versions: dict, version: str) -> packagingVersion.Version:
  if version is not None:
    return packagingVersion.Version(version)
  return sorted(
      versions.keys(),
      reverse=True)[0]

def url_box(metadata: Metadata, version: str = None, provider: str  = "libvirt") -> str:
  versions = metadata.versions_with_provider(provider)
  version = fetch_version(versions, version)
  try:
    return versions[version].provider(provider).url
  except KeyError:
    raise Exception(f"Version '{version}' don't found in metadata")

def forge_metadata_url(box_name: str) -> str:
  if not '/' in box_name:
    raise Exception(f'box_name must contains "/" : {box_name}')
  return 'https://app.vagrantup.com/{}/boxes/{}'.format(*box_name.split('/'))

def fetch_box_url(name: str = None, metadata_url: str = None, version :str = None) -> str:
  if not name and not metadata_url:
    raise Exception('name or metadata_url must be set')

  if not metadata_url and name:
    metadata_url = forge_metadata_url(name)

  return url_box(fetch(metadata_url), version)

