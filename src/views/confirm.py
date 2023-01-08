# -*- coding: utf-8 -*-

"""
The MIT License (MIT)
Copyright (c) 2022-Present Lia Marie
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
import random
import itertools

from typing import TYPE_CHECKING, Coroutine, Tuple

import discord

if TYPE_CHECKING:
    from src.classes import Context


__all__ = ("ConfirmView",)


class AcceptButton(discord.ui.Button):
    def __init__(self, label: str | None, emoji: str | None, button_style: discord.ButtonStyle) -> None:
        super().__init__(label=label, emoji=emoji, style=button_style)

    async def callback(self, interaction: discord.Interaction) -> Coroutine:
        view: ConfirmView = self.view
        view.value = True
        view.stop()

        return await interaction.response.edit_message(view=view)


class DeclineButton(discord.ui.Button):
    def __init__(self, label: str | None, emoji: str | None, button_style: discord.ButtonStyle) -> None:
        super().__init__(label=label, emoji=emoji, style=button_style)

    async def callback(self, interaction: discord.Interaction) -> Coroutine:
        view: ConfirmView = self.view
        view.value = False
        view.stop()

        return await interaction.response.edit_message(view=view)


class ConfirmView(discord.ui.View):
    def __init__(
        self,
        ctx: Context,
        buttons: Tuple[
            Tuple[str | None, str | None, discord.ButtonStyle],
            Tuple[str | None, str | None, discord.ButtonStyle],
        ],
        timeout: float = 60.0,
        owner: discord.User | discord.Member | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self.message = None
        self.value = None
        self.ctx = ctx
        self.owner = owner or ctx.author
        self.add_item(
            AcceptButton(
                label=buttons[0][0],
                emoji=buttons[0][1],
                button_style=buttons[0][2],
            )
        )
        self.add_item(
            DeclineButton(
                label=buttons[1][0],
                emoji=buttons[1][1],
                button_style=buttons[1][2],
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        allowed_ids = list(itertools.chain([self.owner.id], [self.ctx.bot.owner_ids]))
        if interaction.user.id in allowed_ids:
            return True

        messages = [
            "Sowwy, **%s**! This component doesn't belong to you." % interaction.user,
            "Please don't touch other people's buttons, **%s**." % interaction.user,
            "You can't touch this, **%s**." % interaction.user,
            "Please stop touching other people's buttons, **%s**." % interaction.user,
        ]
        await interaction.response.send_message(random.choice(messages), ephemeral=True)
        return False
