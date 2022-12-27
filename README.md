# ganeti-os-vagrant-libvirt


## Prerequisites

*ganeti-os-vagrant-libvirt* depends on python packages. Run follows command for install them :

```sh
pip install packaging dataclasses-json requests python-vagrant-metadata
```
## Installation 

For install *ganeti-os-vagrant-libvirt*, build it for the source and use follows the command on the server :

```sh
dpkg -i ganeti-os-vagrant-libvirt_X.X-X_amd64.deb
```

The installation folder is */usr/share/ganeti/os/*
## Utilisation

When you create a instance with *ganeti-os-vagrant-libvirt*, the OS download the box, decompress them and copy the disk into ganeti disk.
*ganeti-os-vagrant-libvirt* have 4 options :
  - **box_url**: the url of box
  - **box_name**: name of box
  - **box_version**: version of box
  - **box_metadata_url**: the url of metadata json for find the url box
  - **export_import_format**: the format of disk into ganeti backup
  - **export_compress**: compress the disk into ganeti backup
  - **export_import_memory_temporary_file**: Folder for temporary disk during generating ganeti backup

If **box_url** is set, *ganeti-os-vagrant-libvirt* download directly the box.
If **box_url** is not set, *ganeti-os-vagrant-libvirt* download the metadata json file and search the box url. If **box_version** is not set *ganeti-os-vagrant-libvirt* use the last version.
When **box_metadata_url** is not set, **box_metadata_url** is calculate with **box_name**.
The supported format for **export_import_format** are *raw*, *qcow2*, *vmdk*. By default, is *vmdk*.
Set **export_compress** at *True* for actived compression. For disable compression, not set parameters. By default, the compression is disable.
Set path in **export_import_memory_temporary_file** for change directory of temporary files. Example: */dev/shm*. By default is */tmp/*.

It likes with ganeti command :

```sh
gnt-install add -O 'box_name=debian/bullseye64' ...
```

## Development and testing

### Launch tests :

```sh 
make test
```

### Build debian package :

```sh
make dist
```