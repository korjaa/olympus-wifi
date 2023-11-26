import os
import pathlib
import tempfile
import subprocess

class RtpReceiver:
    def __init__(self, port: int):
        self.port = port
        self._file = None
        self.rtp_pid = None
        # https://github.com/irtlab/rtptools
        self.rtpdump = pathlib.Path(
            "~/workspace/rtptools/rtpdump").expanduser()

    @property
    def file(self) -> pathlib.Path:
        return str(self._file)

    def __enter__(self):
        # Create FIFO file
        with tempfile.NamedTemporaryFile(suffix=".rtpdump") as fid:
            self._file = pathlib.Path(fid.name)
        os.mkfifo(self._file)

        # Launch RTP receiver
        self.rtp_pid = subprocess.Popen(
            [self.rtpdump, "-F", "payload", f"0.0.0.0/{self.port}", "-o", self._file])

        return self

    def __exit__(self, *args, **kwargs):
        self.rtp_pid.kill()

    def __del__(self):
        # Reliable cleanup
        if self._file.exists():
            self._file.unlink()
