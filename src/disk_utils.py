"""
Utils function for qemu convert
"""
import subprocess
import tempfile
from functools import partial

# see doc https://docs.ganeti.org/docs/ganeti/2.6/man/ganeti-os-interface.html

class UnsupportedDiskFormat(Exception):
    """
    Exception for UnsupportedFiskFormat
    """
    def __init__(self, disk_format):
        super().__init__(f'Format "{disk_format}" is not supported')

supported_disk_format = ["raw", "vmdk", "qcow2"]

def is_supported_disk_format(disk_format: str):
    """
    Test if disk format is supported.
    The supported format is "raw", "vmdk", "qcow2".
    """
    return disk_format in supported_disk_format

def raise_if_unsupported_disk_format(disk_format: str) -> None:
    """
    Raise UnsupportedDiskFormat if disk format is not supported
    """
    if not is_supported_disk_format(disk_format):
        raise UnsupportedDiskFormat(disk_format)

def copy_disk(src: str, dst: str, format_in: str, format_out: str, compress: bool = False) -> None:
    """
    Run qemu-img command for convert disk format
    """
    raise_if_unsupported_disk_format(format_in)
    raise_if_unsupported_disk_format(format_out)
    compress_options = ['-c'] if compress else []
    subprocess.run(
        ['/usr/bin/qemu-img', 'convert', *compress_options, '-f',
            format_in, '-O', format_out, src, dst],
        check=True
    )

copy_vmdk_to_raw = partial(copy_disk, format_in='vmdk', format_out='raw')
copy_raw_to_vmdk = partial(copy_disk, format_in='raw', format_out='vmdk')
copy_qcow2_to_raw = partial(copy_disk, format_in='qcow2', format_out='raw')
copy_raw_to_qcow2 = partial(copy_disk, format_in='raw', format_out='qcow2')

def from_raw_to(disk_format:str) -> copy_disk:
    """
    convert from raw to specify format
    """
    return partial(copy_disk, format_in='raw', format_out=disk_format)

def to_raw_from(disk_format: str) -> copy_disk:
    """
    convert to raw
    """
    return partial(copy_disk, format_in=disk_format, format_out='raw')

def get_context_manager_tmp_file(is_spooled_temp_file, mode):
    """
    If is_spooled_temp_file is True, return SpooledTemporaryFile
    If is_spooled_temp_file is False, return NamedTemporaryFile
    """
    if is_spooled_temp_file:
        return tempfile.SpooledTemporaryFile(mode=mode)
    return tempfile.NamedTemporaryFile(mode=mode)
