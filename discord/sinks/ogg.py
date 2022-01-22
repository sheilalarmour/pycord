"""
The MIT License (MIT)

Copyright (c) 2021-present Pycord Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
import os
import subprocess

from .core import CREATE_NO_WINDOW, Filters, Sink, default_filters
from .errors import OGGSinkError


class OGGSink(Sink):
    """A Sink "stores" all the audio data.
    
    Used for .ogg files.
    
    .. versionadded:: 2.1
    
    Parameters
    ----------
    output_path: :class:`string`
        A path to where the audio files should be output.
    
    Raises
    ------
    ClientException
        An invalid encoding type was specified.
        Audio may only be formatted after recording is finished.
    """

    def __init__(self, *, output_path="", filters=None):
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)

        self.encoding = "ogg"
        self.file_path = output_path
        self.vc = None
        self.audio_data = {}

    def format_audio(self, audio):
        if self.vc.recording:
            raise OGGSinkError(
                "Audio may only be formatted after recording is finished."
            )
        ogg_file = audio.file.split(".")[0] + ".ogg"
        args = [
            "ffmpeg",
            "-f",
            "s16le",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-i",
            audio.file,
            ogg_file,
        ]
        process = None
        if os.path.exists(ogg_file):
            os.remove(
                ogg_file
            )  # process will get stuck asking whether or not to overwrite, if file already exists.
        try:
            process = subprocess.Popen(args, creationflags=CREATE_NO_WINDOW)
        except FileNotFoundError:
            raise OGGSinkError("ffmpeg was not found.") from None
        except subprocess.SubprocessError as exc:
            raise OGGSinkError(
                "Popen failed: {0.__class__.__name__}: {0}".format(exc)
            ) from exc

        process.wait()

        os.remove(audio.file)
        audio.on_format(self.encoding)