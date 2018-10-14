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
import enum
from typing import Optional

import discord

from concord.ext.audio import AudioExtensionError, AudioState, AudioStatus

from concord.ext.player.entry import Playlist
from concord.ext.player.exceptions import PlayerError


class PlayerStatus(enum.Enum):
    PLAYING = enum.auto()
    PAUSED = enum.auto()
    STOPPED = enum.auto()


class Player:
    def __init__(
        self, audio_state: AudioState, *, playlist: Optional[Playlist] = None
    ):
        self._audio_state = audio_state
        self._loop = asyncio.get_running_loop()

        self._playlist = playlist or Playlist()
        self._audio_source = None

        self._status = PlayerStatus.STOPPED
        self._playlist_pos = 0

        self._volume = 1.0

    def set_playlist(self, playlist: Playlist):
        self._playlist = playlist
        self._playlist_pos = 0

    @property
    def playlist(self):
        return self._playlist

    def is_playing(self):
        return self._status == PlayerStatus.PLAYING

    def is_paused(self):
        return self._status == PlayerStatus.PAUSED

    def is_stopped(self):
        return self._status == PlayerStatus.STOPPED

    async def _play(self):
        if self._audio_source is None:
            entry = self._playlist.entries[self._playlist_pos]
            url = await entry.resolve(self._loop)
            self._audio_source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(url), volume=self.volume
            )

        try:
            self._audio_state.add_source(
                self._audio_source, finalizer=self._on_end_playing_listener
            )
            self._status = PlayerStatus.PLAYING
        except AudioExtensionError:
            self.stop()
            raise PlayerError()

    def play(self):
        self._loop.create_task(self._play())

    def skip(self):
        if self.is_stopped():
            return
        #
        self._playlist_pos += 1

        if self._playlist_pos >= len(self._playlist.entries):
            self.stop()
        else:
            if self._audio_source is not None:
                try:
                    self._audio_state.remove_source(self._audio_source)
                except KeyError:
                    pass
            self._audio_source = None
            if not self.is_paused():
                self.play()

    def pause(self):
        if self.is_playing():
            self._audio_state.remove_source(self._audio_source)
            self._status = PlayerStatus.PAUSED

    def resume(self):
        if self.is_paused():
            self.play()

    def stop(self):
        if self._audio_source is not None:
            try:
                self._audio_state.remove_source(self._audio_source)
            except KeyError:
                pass
        #
        self._audio_source = None
        self._playlist_pos = 0
        self._status = PlayerStatus.STOPPED

    def _on_end_playing_listener(self, audio_source, reason):
        # If listener is called due to external change in player state, don't do
        # anything.
        if reason == AudioStatus.SOURCE_ENDED:
            self.skip()

    @property
    def volume(self) -> float:
        """Volume of audio (float number from 0.0 to 2.0)."""
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = max(min(value, 2.0), 0.0)
        if self._audio_source is not None:
            self._audio_source.volume = self._volume
