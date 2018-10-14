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

from typing import Callable, Optional

from concord.context import Context
from concord.ext import audio
from concord.middleware import Middleware, MiddlewareState

from concord.ext.player.exceptions import (
    EmptyStreamError,
    PlayerExtensionError,
    UnsupportedURLError,
)
from concord.ext.player.state import State


class Play(Middleware):
    """Middleware for playing provided audio's url in a user's voice channel."""

    async def run(
        self,
        *_,
        ctx: Context,
        next: Callable,
        url: Optional[str] = None,
        extractor: str = "youtube-dl",
        **kw,
    ):  # noqa: D102
        state = MiddlewareState.get_state(ctx, State)
        astate = MiddlewareState.get_state(ctx, audio.State)

        if state is None or astate is None:
            return

        channel = ctx.kwargs["message"].channel

        audio_state = astate.get_audio_state(channel.guild)
        player = state.get_player(audio_state)

        if url is None and len(player.playlist.entries) == 0:
            await channel.send("Provide URL to play.")
            return
        elif url:
            if extractor not in state.extractors:
                await channel.send("Extractor not found.")
                return
            #
            try:
                playlist = await state.extractors[extractor].extract(
                    url, ctx.client.loop
                )
                player.stop()
                player.set_playlist(playlist)
            except UnsupportedURLError:
                await channel.send("Provided URL is not supported.")
                return
            except EmptyStreamError:
                await channel.send("Nothing to play found by provided URL.")
                return
            except PlayerExtensionError:
                await channel.send("Error during resolving provided URL.")
                return
        #
        if audio_state.voice_client is None:
            await channel.send("I'm not connected to voice channel.")
            return
        #
        player.play()
        await channel.send("Playing...")


class Pause(Middleware):
    """Middleware for pausing currently playing audio."""

    async def run(self, *_, ctx: Context, next: Callable, **kw):  # noqa: D102
        state = MiddlewareState.get_state(ctx, State)
        astate = MiddlewareState.get_state(ctx, audio.State)

        if state is None or astate is None:
            return

        channel = ctx.kwargs["message"].channel

        audio_state = astate.get_audio_state(channel.guild)
        player = state.get_player(audio_state)

        if audio_state.voice_client is None:
            await channel.send("I'm not connected to voice channel.")
            return
        if player.is_stopped():
            await channel.send("I'm not playing audio.")
            return
        if player.is_paused():
            await channel.send("Already paused.")
            return
        #
        player.pause()
        await channel.send("Paused.")


class Resume(Middleware):
    """Middleware for resuming currently playing audio."""

    async def run(self, *_, ctx: Context, next: Callable, **kw):  # noqa: D102
        state = MiddlewareState.get_state(ctx, State)
        astate = MiddlewareState.get_state(ctx, audio.State)

        if state is None or astate is None:
            return

        channel = ctx.kwargs["message"].channel

        audio_state = astate.get_audio_state(channel.guild)
        player = state.get_player(audio_state)

        if audio_state.voice_client is None:
            await channel.send("I'm not connected to voice channel.")
            return
        if player.is_stopped():
            await channel.send("I'm not playing audio.")
            return
        if player.is_playing():
            await channel.send("Already playing.")
            return
        #
        player.resume()
        await channel.send("Resumed.")


class Stop(Middleware):
    """Middleware for stopping currently playing audio."""

    async def run(self, *_, ctx: Context, next: Callable, **kw):  # noqa: D102
        state = MiddlewareState.get_state(ctx, State)
        astate = MiddlewareState.get_state(ctx, audio.State)

        if state is None or astate is None:
            return

        channel = ctx.kwargs["message"].channel

        audio_state = astate.get_audio_state(channel.guild)
        player = state.get_player(audio_state)

        if audio_state.voice_client is None:
            await channel.send("I'm not connected to voice channel.")
            return
        if player.is_stopped():
            await channel.send("I'm not playing audio.")
            return
        #
        player.stop()
        await channel.send("Stopped.")


class Skip(Middleware):
    """Middleware for skipping currently playing audio."""

    async def run(self, *_, ctx: Context, next: Callable, **kw):  # noqa: D102
        state = MiddlewareState.get_state(ctx, State)
        astate = MiddlewareState.get_state(ctx, audio.State)

        if state is None or astate is None:
            return

        channel = ctx.kwargs["message"].channel

        audio_state = astate.get_audio_state(channel.guild)
        player = state.get_player(audio_state)

        if audio_state.voice_client is None:
            await channel.send("I'm not connected to voice channel.")
            return
        if player.is_stopped():
            await channel.send("I'm not playing audio.")
            return
        #
        player.skip()
        await channel.send("Skipped.")


class Volume(Middleware):
    """Middleware for change volume of audio player."""

    async def run(
        self,
        *_,
        ctx: Context,
        next: Callable,
        volume: Optional[str] = None,
        **kw,
    ):  # noqa: D102
        state = MiddlewareState.get_state(ctx, State)
        astate = MiddlewareState.get_state(ctx, audio.State)

        if state is None or astate is None:
            return

        channel = ctx.kwargs["message"].channel

        audio_state = astate.get_audio_state(channel.guild)
        player = state.get_player(audio_state)

        if volume is not None:
            try:
                player.volume = float(volume)
            except ValueError:
                await channel.send("Only float values are possible.")
                return
        #
        await channel.send(f"Player volume is set to {player.volume}")
