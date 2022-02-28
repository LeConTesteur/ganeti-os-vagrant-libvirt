import subprocess

from pathlib import Path

# see doc https://docs.ganeti.org/docs/ganeti/2.6/man/ganeti-os-interface.html

class CopyDisk:
    def __init__(self, format_in, format_out) -> None:
        self.format_in = format_in
        self.format_out = format_out

    def copy(self, src, dst):
        subprocess.run(
            ['/usr/bin/qemu-img', 'convert', '-f',
                self.format_in, '-O', self.format_out, src, dst],
            check=True
        )


class VmdkToRaw(CopyDisk):
    def __init__(self) -> None:
        super().__init__('vmdk', 'raw')


class RawToVmdk(CopyDisk):
    def __init__(self) -> None:
        super().__init__('raw', 'vmdk')


class Qcow2ToRaw(CopyDisk):
    def __init__(self) -> None:
        super().__init__('qcow2', 'raw')


class RawToQcow2(CopyDisk):
    def __init__(self) -> None:
        super().__init__('raw', 'qcow2')


format_to_raw = {
    'vmdk': VmdkToRaw(),
    'qcow2': Qcow2ToRaw()
}


def toRaw(format):
    return format_to_raw[format]
