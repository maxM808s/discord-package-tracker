import os

import discord
from discord import app_commands
from dotenv import load_dotenv

from tracking import get_tracking_info


# -----------------------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------------------

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")


# -----------------------------------------
# DISCORD BOT
# -----------------------------------------

class TrackingBot(discord.Client):

    def __init__(self):
        intents = discord.Intents.default()

        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):

        # Register slash commands in our test server
        guild = discord.Object(
            id=int(GUILD_ID)
        )

        self.tree.copy_global_to(
            guild=guild
        )

        await self.tree.sync(
            guild=guild
        )

        print("Slash commands registered!")

    async def on_ready(self):

        print("---------------------------")
        print(f"Logged in as {self.user}")
        print("Package Tracker is ONLINE!")
        print("---------------------------")


# -----------------------------------------
# CREATE BOT
# -----------------------------------------

bot = TrackingBot()


# -----------------------------------------
# /track COMMAND
# -----------------------------------------

@bot.tree.command(
    name="track",
    description="Track a shipping package"
)
@app_commands.describe(
    tracking_number="The package tracking number"
)
async def track(
    interaction: discord.Interaction,
    tracking_number: str
):

    # Tell Discord that the bot is processing
    await interaction.response.defer()

    # Clean tracking number
    tracking_number = tracking_number.strip()

    print(
        f"Tracking request: {tracking_number}"
    )

    # -----------------------------------------
    # GET TRACKING INFORMATION
    # -----------------------------------------

    tracking = await get_tracking_info(
        tracking_number
    )

    # -----------------------------------------
    # ERROR
    # -----------------------------------------

    if not tracking["success"]:

        await interaction.followup.send(
            "❌ I couldn't find tracking information "
            "for that package."
        )

        return

    # -----------------------------------------
    # CREATE EMBED
    # -----------------------------------------

    embed = discord.Embed(
        title="📦 Package Tracking",
        description=(
            f"**{tracking['tracking_number']}**"
        ),
        color=discord.Color.blue()
    )

    # -----------------------------------------
    # CARRIER
    # -----------------------------------------

    embed.add_field(
        name="🚚 Carrier",
        value=tracking.get(
            "carrier",
            "Unknown"
        ),
        inline=True
    )

    # -----------------------------------------
    # STATUS
    # -----------------------------------------

    embed.add_field(
        name="📦 Status",
        value=tracking.get(
            "status",
            "Unknown"
        ),
        inline=True
    )

    # -----------------------------------------
    # LOCATION
    # -----------------------------------------

    embed.add_field(
        name="📍 Location",
        value=tracking.get(
            "location",
            "Unknown"
        ),
        inline=True
    )

    # -----------------------------------------
    # ESTIMATED DELIVERY
    # -----------------------------------------

    embed.add_field(
        name="📅 Estimated Delivery",
        value=tracking.get(
            "estimated_delivery",
            "Not available"
        ),
        inline=True
    )

    # -----------------------------------------
    # TRACKING HISTORY
    # -----------------------------------------

    events = tracking.get(
        "events",
        []
    )

    if events:

        history = ""

        # Get the latest 5 tracking events
        latest_events = events[-5:]

        # Show newest first
        for event in reversed(latest_events):

            event_status = event.get(
                "status",
                "Tracking update"
            )

            event_location = event.get(
                "location"
            )

            event_date = event.get(
                "occurrenceDatetime"
            )

            # Add status
            history += (
                f"**{event_status}**\n"
            )

            # Add location if available
            if event_location:
                history += (
                    f"📍 {event_location}\n"
                )

            # Add date if available
            if event_date:
                history += (
                    f"🕐 {event_date}\n"
                )

            history += "\n"

        # Discord field limit is 1024 characters
        history = history[:1024]

        embed.add_field(
            name="📋 Tracking History",
            value=history,
            inline=False
        )

    # -----------------------------------------
    # FOOTER
    # -----------------------------------------

    embed.set_footer(
        text="Package Tracker"
    )

    # -----------------------------------------
    # SEND RESULT
    # -----------------------------------------

    await interaction.followup.send(
        embed=embed
    )


# -----------------------------------------
# CHECK ENVIRONMENT VARIABLES
# -----------------------------------------

if not TOKEN:

    raise ValueError(
        "DISCORD_TOKEN is missing from .env"
    )


if not GUILD_ID:

    raise ValueError(
        "GUILD_ID is missing from .env"
    )


# -----------------------------------------
# START BOT
# -----------------------------------------

bot.run(TOKEN)