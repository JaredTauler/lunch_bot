from nextcord.ui import Button, View
import nextcord
from cogs.lunch_order.menu import LunchMenu

# Anvil
from cogs.lunch_order.anvil_wrapper import lunch_to_server, auth as anvil_auth
from __main__ import CONFIG
anvil_auth(CONFIG["anvil-token"])

from __main__ import custom_id

VIEW_NAME = "LunchOrder"
class LunchOrder(nextcord.ui.View):
    def __init__(self, Count):
        super().__init__(timeout=None)
        self.Count = Count

    # Routine for ordering / announcing
    def orderview(self):
        async def place_order(interaction, milk):
            uid = interaction.user.id
            res = lunch_to_server(uid, milk)  # Make API call.

            if res == 1:  # Success
                await interaction.response.send_message("Ordered your lunch!", ephemeral=True)
                self.Count.another()  # Update status.

            elif res == 0:  # No ID yet.
                button = Button(label="Connect Discord with JRTI Lunch", url="https://lunch.jamesrumsey.com/#discord",
                                style=nextcord.ButtonStyle.blurple)
                view = View()
                view.add_item(button)
                txt = (
                    ":face_with_raised_eyebrow:\n"
                    "This Discord account is not linked to a user in our system.\n"
                )
                await interaction.response.send_message(txt, ephemeral=True, view=view)

            else:  # An error happened
                await interaction.response.send_message(f"Error: {res}", ephemeral=True)
        def white(view):
            async def click(interaction):
                await place_order(interaction, "White")

            button = Button(label="White", style=nextcord.ButtonStyle.blurple)
            button.callback = click
            view.add_item(button)

        def choc(view):
            async def click(interaction):
                await place_order(interaction, "Chocolate")

            button = Button(label="Chocolate", style=nextcord.ButtonStyle.blurple)
            button.callback = click
            view.add_item(button)

        view = View()
        white(view)
        choc(view)
        return view

    async def order_lunch(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        await interaction.response.send_message("Milk?", ephemeral=True, view=self.orderview())

    # Buttons
    @nextcord.ui.button(
        label="Order Lunch",
        custom_id = custom_id(VIEW_NAME, 21),
    )
    async def order_button(self, button, interaction):
        await self.order_lunch(button, interaction)


