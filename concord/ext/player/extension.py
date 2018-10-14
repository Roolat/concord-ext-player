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

from typing import Sequence

from concord.constants import EventType
from concord.ext.base import (
    BotFilter,
    ChannelTypeFilter,
    Command,
    EventNormalization,
    EventTypeFilter,
)
from concord.extension import Extension
from concord.middleware import Middleware, MiddlewareState, chain_of

from concord.ext.player.middleware import (
    Pause,
    Play,
    Resume,
    Skip,
    Stop,
    Volume,
)
from concord.ext.player.state import State
from concord.ext.player.version import version


class PlayerExtension(Extension):
    NAME = "Player"
    DESCRIPTION = "Player extension (music-related functionality) for Concord"
    VERSION = version

    def __init__(self) -> None:
        super().__init__()

        self._state = State()
        self._extension_middleware = [
            chain_of(
                [
                    Play(),
                    MiddlewareState(self._state),
                    Command("play", rest_pattern="(?P<url>.+)?"),
                    Command("player"),
                    ChannelTypeFilter(guild=True),
                    BotFilter(authored_by_bot=False),
                    EventTypeFilter(EventType.MESSAGE),
                    EventNormalization(),
                ]
            ),
            chain_of(
                [
                    Pause(),
                    MiddlewareState(self._state),
                    Command("pause"),
                    Command("player"),
                    ChannelTypeFilter(guild=True),
                    BotFilter(authored_by_bot=False),
                    EventTypeFilter(EventType.MESSAGE),
                    EventNormalization(),
                ]
            ),
            chain_of(
                [
                    Resume(),
                    MiddlewareState(self._state),
                    Command("resume"),
                    Command("player"),
                    ChannelTypeFilter(guild=True),
                    BotFilter(authored_by_bot=False),
                    EventTypeFilter(EventType.MESSAGE),
                    EventNormalization(),
                ]
            ),
            chain_of(
                [
                    Stop(),
                    MiddlewareState(self._state),
                    Command("stop"),
                    Command("player"),
                    ChannelTypeFilter(guild=True),
                    BotFilter(authored_by_bot=False),
                    EventTypeFilter(EventType.MESSAGE),
                    EventNormalization(),
                ]
            ),
            chain_of(
                [
                    Skip(),
                    MiddlewareState(self._state),
                    Command("skip"),
                    Command("player"),
                    ChannelTypeFilter(guild=True),
                    BotFilter(authored_by_bot=False),
                    EventTypeFilter(EventType.MESSAGE),
                    EventNormalization(),
                ]
            ),
            chain_of(
                [
                    Volume(),
                    MiddlewareState(self._state),
                    Command("volume", rest_pattern="(?P<volume>.+)?"),
                    Command("player"),
                    ChannelTypeFilter(guild=True),
                    BotFilter(authored_by_bot=False),
                    EventTypeFilter(EventType.MESSAGE),
                    EventNormalization(),
                ]
            ),
        ]

    @property
    def extension_middleware(self) -> Sequence[Middleware]:
        return self._extension_middleware
