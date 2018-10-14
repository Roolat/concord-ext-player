"""
The MIT License (MIT)

Copyright (c) 2017-2018 Nariman Safiulin

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import asyncio
from typing import Dict, Optional

from concord.ext.player.exceptions import PlayerExtensionError


class Entry:
    def __init__(
        self,
        *,
        source_url: Optional[str] = None,
        extractor: Optional["Extractor"] = None,
    ):
        self.source_url = source_url
        self.extractor = extractor

    def is_source(self) -> bool:
        return self.source_url is not None

    def has_extractor(self) -> bool:
        return self.extractor is not None

    def resolve(self, loop: asyncio.AbstractEventLoop) -> str:
        if self.has_extractor():
            return self.extractor.resolve(self, loop)
        raise PlayerExtensionError("Extractor not found")


class StreamlinkEntry(Entry):
    def __init__(
        self,
        *,
        source_url: Optional[str] = None,
        extractor: Optional["Extractor"] = None,
    ):
        super().__init__(source_url=source_url, extractor=extractor)


class YouTubeDLEntry(Entry):
    def __init__(
        self,
        metadata: Dict,
        *,
        source_url: Optional[str] = None,
        extractor: Optional["Extractor"] = None,
    ):
        super().__init__(source_url=source_url, extractor=extractor)
        self.metadata = metadata


class Playlist:
    def __init__(self, *, source_url: Optional[str] = None):
        self.source_url = source_url
        self.entries = []

    def is_source(self) -> bool:
        return self.source_url is not None
