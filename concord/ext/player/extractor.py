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

import abc
import asyncio
import functools

import streamlink
import youtube_dl

from concord.ext.player.entry import (
    Entry,
    Playlist,
    StreamlinkEntry,
    YouTubeDLEntry,
)
from concord.ext.player.exceptions import (
    EmptyStreamError,
    PlayerExtensionError,
    UnsupportedURLError,
)


class Extractor(abc.ABC):
    """Abstract extractor class.

    Attributes
    ----------
    ALIASES : list
        Alias names for extractor.
    """

    ALIASES = []

    @abc.abstractmethod
    async def extract(
        self, source_url: str, loop: asyncio.AbstractEventLoop
    ) -> Playlist:
        pass  # pragma: no cover

    async def resolve(
        self, entry: Entry, loop: asyncio.AbstractEventLoop
    ) -> str:
        pass


class YouTubeDLExtractor(Extractor):
    """Youtube-DL extractor.

    Attributes
    ----------
    ALIASES : list
        Alias names for extractor.
    OPTIONS : dict
        Youtube-DL extract options.
    session : :class:`youtube_dl.YoutubeDL`
        Youtube-DL session object.
    """

    ALIASES = ["youtube-dl", "youtubedl", "ytdl", "ydl"]

    OPTIONS = {
        "format": "bestaudio/best",
        "default_search": "auto",
        "ignoreerrors": True,
        "noplaylist": True,
        "skip_download": True,
        "quiet": True,
    }
    EXTRACT_OPTIONS = {**OPTIONS, "extract_flat": True}
    RESOLVE_OPTIONS = {**OPTIONS}

    def __init__(self):
        self.session_extractor = youtube_dl.YoutubeDL(
            params=self.EXTRACT_OPTIONS
        )
        self.session_resolver = youtube_dl.YoutubeDL(
            params=self.RESOLVE_OPTIONS
        )

    async def extract(
        self, url: str, loop: asyncio.AbstractEventLoop
    ) -> Playlist:  # noqa: D102
        try:
            info = await loop.run_in_executor(
                None,
                functools.partial(self.session_extractor.extract_info, url),
            )
        except Exception:
            raise PlayerExtensionError()
        #
        type = info.get("_type", "video")
        playlist = Playlist()

        if type == "video":
            playlist.entries.append(
                YouTubeDLEntry(info, source_url=url, extractor=self)
            )
        elif type == "playlist":
            playlist.source_url = url
            for entry in info["entries"]:
                playlist.entries.append(YouTubeDLEntry(entry, extractor=self))
        else:
            raise UnsupportedURLError()
        #
        return playlist

    async def resolve(
        self, entry: YouTubeDLEntry, loop: asyncio.AbstractEventLoop
    ) -> str:  # noqa: D102
        try:
            info = await loop.run_in_executor(
                None,
                functools.partial(
                    self.session_resolver.process_ie_result, entry.metadata
                ),
            )
        except Exception:
            raise PlayerExtensionError()

        type = info.get("_type", "video")
        if type == "video" and "url" in info:
            return info["url"]
        raise EmptyStreamError()


class StreamlinkExtractor(Extractor):
    """Streamlink extractor.

    Attributes
    ----------
    ALIASES : list
        Alias names for extractor.
    session : :class:`streamlink.Streamlink`
        Streamlink session object.
    """

    ALIASES = ["streamlink", "sl", "livestreamer", "ls"]

    def __init__(self):
        self.session = streamlink.Streamlink()

    async def _fetch(
        self, url: str, loop: asyncio.AbstractEventLoop
    ):  # noqa: D102
        try:
            streams = await loop.run_in_executor(
                None, functools.partial(self.session.streams, url)
            )
        except streamlink.NoPluginError:
            raise UnsupportedURLError()
        except streamlink.PluginError:
            raise PlayerExtensionError()
        #
        if not streams:
            raise EmptyStreamError()
        if "best" not in streams:
            raise EmptyStreamError()
        #
        return streams

    async def extract(
        self, url: str, loop: asyncio.AbstractEventLoop
    ) -> Playlist:  # noqa: D102
        _ = await self._fetch(url, loop)
        playlist = Playlist()
        playlist.entries.append(StreamlinkEntry(source_url=url, extractor=self))
        return playlist

    async def resolve(
        self, entry: StreamlinkEntry, loop: asyncio.AbstractEventLoop
    ) -> str:  # noqa: D102
        streams = await self._fetch(entry.source_url, loop)
        return streams["best"].url
