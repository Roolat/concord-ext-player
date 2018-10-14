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

from typing import Optional, Sequence, Type

from concord.ext.audio import AudioState

from concord.ext.player.extractor import (
    Extractor,
    StreamlinkExtractor,
    YouTubeDLExtractor,
)
from concord.ext.player.player import Player


class State:
    """State class for extension related information.

    Contains different extractors' instances and current guilds' players.

    Args:
        extractors: Extractors to initialize.

    Attributes:
        players: Map guild.id -> guild player object with current playlist,
            custom options and other info, related for that guild.
        extractors: Initialized extractors (with aliases).
    """

    def __init__(self, extractors: Optional[Sequence[Type[Extractor]]] = None):
        self.extractors = {}
        self._players = {}

        if extractors is None:
            extractors = [YouTubeDLExtractor, StreamlinkExtractor]

        for extractor in extractors:
            instance = extractor()

            for alias in extractor.ALIASES:
                self.extractors[alias] = instance

    def get_player(self, audio_state: AudioState) -> Player:
        """Returns player for given audio state.

        Player will be created, if isn't created yet.

        Args:
            audio_state: The audio state, by which player can be found.

        Returns:
            Player instance.
        """
        player = self._players.get(audio_state)
        if player is None:
            player = self._players[audio_state] = Player(audio_state)

        return player
