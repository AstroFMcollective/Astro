import discord
from typing import List



class PaginatorView(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed], button_views: List[discord.ui.View]):
        super().__init__(timeout = 600)
        self._embeds = embeds
        self._button_views = button_views
        self._len = len(embeds)
        self._current_page = 0

        # Add page indicator field to each embed
        for idx, embed in enumerate(self._embeds):
            embed.add_field(
                name="Paginated view",
                value=f"{idx + 1} of {self._len}, use controls below",
                inline=False
            )

        # Add paginator buttons to this view
        self.previous_button = discord.ui.Button(emoji = '⏪', style = discord.ButtonStyle.secondary)
        self.next_button = discord.ui.Button(emoji = '⏩', style = discord.ButtonStyle.secondary)
        self.previous_button.callback = self.previous
        self.next_button.callback = self.next
        self.add_item(self.previous_button)
        self.add_item(self.next_button)

        # Add initial embed-specific buttons
        self._add_embed_buttons(0)

    async def interaction_check(self, _interaction: discord.Interaction) -> bool:
        return True

    async def on_timeout(self):
        # Disable paginator buttons
        self.previous_button.disabled = True
        self.next_button.disabled = True

        # Update the "Paginated view" field in the current embed
        embed = self._embeds[self._current_page]
        for field in embed.fields:
            if field.name == 'Paginated view':
                embed.set_field_at(
                    embed.fields.index(field),
                    name = 'Paginated view',
                    value = 'This paginated view has expired! If you wish to get the links of the other media, re-run the command!',
                    inline = False
                )
                break

        await self.message.edit(embed = embed, view = self)

    def _add_embed_buttons(self, page_index: int):
        paginator_buttons = [self.previous_button, self.next_button]
        self.clear_items()
        for btn in paginator_buttons:
            self.add_item(btn)
        for item in self._button_views[page_index].children:
            self.add_item(item)

    async def handle_page_change(self, interaction: discord.Interaction):
        embed = self._embeds[self._current_page]
        self._add_embed_buttons(self._current_page)
        await interaction.response.edit_message(embed = embed, view = self)

    async def previous(self, interaction: discord.Interaction):
        self._current_page = (self._current_page - 1) % self._len
        await self.handle_page_change(interaction)

    async def next(self, interaction: discord.Interaction):
        self._current_page = (self._current_page + 1) % self._len
        await self.handle_page_change(interaction)

    @property
    def initial_embed(self):
        return self._embeds[0]

    @property
    def initial_buttons(self):
        return self._button_views[0]