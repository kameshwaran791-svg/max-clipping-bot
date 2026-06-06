import discord
from discord.ext import commands
from discord import app_commands
import json
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DB_FILE = "users.json"

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

class RegisterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Register", style=discord.ButtonStyle.green)
    async def register(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Clipper")

        if role:
            await interaction.user.add_roles(role)

        db = load_db()

        if str(interaction.user.id) not in db:
            db[str(interaction.user.id)] = {
                "accounts": [],
                "payments": {}
            }
            save_db(db)

        await interaction.response.send_message(
            "✅ Successfully Registered as Clipper",
            ephemeral=True
        )

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.tree.command(name="registerpanel", description="Create Register Panel")
async def registerpanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Clipper Registration",
        description="Click the button below to register.",
        color=discord.Color.green()
    )

    await interaction.channel.send(
        embed=embed,
        view=RegisterView()
    )

    await interaction.response.send_message(
        "✅ Register panel created",
        ephemeral=True
    )

@bot.tree.command(name="add_account", description="Add Social Account")
@app_commands.describe(platform="tiktok/instagram/youtube", username="Username")
async def add_account(interaction: discord.Interaction, platform: str, username: str):

    db = load_db()

    user_id = str(interaction.user.id)

    if user_id not in db:
        db[user_id] = {
            "accounts": [],
            "payments": {}
        }

    db[user_id]["accounts"].append({
        "platform": platform,
        "username": username
    })

    save_db(db)

    await interaction.response.send_message(
        f"✅ Added {platform}: {username}",
        ephemeral=True
    )

@bot.tree.command(name="add_payment", description="Add Payment Method")
@app_commands.describe(method="paypal/usdt/usdc/eth", value="Address or Email")
async def add_payment(interaction: discord.Interaction, method: str, value: str):

    db = load_db()

    user_id = str(interaction.user.id)

    if user_id not in db:
        db[user_id] = {
            "accounts": [],
            "payments": {}
        }

    db[user_id]["payments"][method] = value

    save_db(db)

    await interaction.response.send_message(
        f"✅ Saved {method}",
        ephemeral=True
    )

@bot.tree.command(name="account_info", description="View Account Information")
async def account_info(interaction: discord.Interaction):

    db = load_db()

    user_id = str(interaction.user.id)

    if user_id not in db:
        await interaction.response.send_message(
            "No data found.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=f"{interaction.user.name} Account Info",
        color=discord.Color.blurple()
    )

    accounts = db[user_id]["accounts"]

    if accounts:
        text = "\n".join(
            [f"{a['platform']} - {a['username']}" for a in accounts]
        )
        embed.add_field(
            name="Accounts",
            value=text,
            inline=False
        )

    payments = db[user_id]["payments"]

    if payments:
        text = "\n".join(
            [f"{k}: {v}" for k, v in payments.items()]
        )
        embed.add_field(
            name="Payments",
            value=text,
            inline=False
        )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )

bot.run(TOKEN)
