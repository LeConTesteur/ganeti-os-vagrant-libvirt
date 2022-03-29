"""
Utils function for qemu convert
"""
import subprocess


# see doc https://docs.ganeti.org/docs/ganeti/2.6/man/ganeti-os-interface.html

class CopyDisk:  # pylint: disable=too-few-public-methods
    """
    Class for convert disk format
    """

    def __init__(self, format_in: str, format_out: str) -> None:
        self.format_in = format_in
        self.format_out = format_out

    def copy(self, src: str, dst: str) -> None:
        """
        Run qemu-img command for convert disk format
        """
        subprocess.run(
            ['/usr/bin/qemu-img', 'convert', '-f',
                self.format_in, '-O', self.format_out, src, dst],
            check=True
        )


class VmdkToRaw(CopyDisk):  # pylint: disable=too-few-public-methods
    """
    qemu convert vmdk to raw
    """

    def __init__(self) -> None:
        super().__init__('vmdk', 'raw')


class RawToVmdk(CopyDisk):  # pylint: disable=too-few-public-methods
    """
    qemu convert raw to vmdk
    """

    def __init__(self) -> None:
        super().__init__('raw', 'vmdk')


class Qcow2ToRaw(CopyDisk):  # pylint: disable=too-few-public-methods
    """
    qemu convert qcow2 to raw
    """

    def __init__(self) -> None:
        super().__init__('qcow2', 'raw')


class RawToQcow2(CopyDisk):  # pylint: disable=too-few-public-methods
    """
    qemu convert raw to qcow2
    """

    def __init__(self) -> None:
        super().__init__('raw', 'qcow2')


format_to_raw = {
    'vmdk': VmdkToRaw(),
    'qcow2': Qcow2ToRaw()
}


def to_raw(disk_format: str) -> CopyDisk:
    """
    Get class for convert format
    """
    return format_to_raw[disk_format]
