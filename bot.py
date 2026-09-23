import os
import discord
from discord import app_commands
import requests

# Configuration
AREA_ID = '0502'
DEVICE_TYPE = 'fcu'
SYSTEM_ID = 'q05'
DEVICE_ID = f'{AREA_ID}_{DEVICE_TYPE}_{SYSTEM_ID}'
NO = '1-1-05'

class ACController:
    def __init__(self):
        self.session = requests.Session()
        self.authenticated = False

    def authenticate(self):
        try:
            self.session.cookies.clear()
            res1 = self.session.get(f'http://163.13.178.184/EMSystem/Account/Login?qr={DEVICE_ID}&no={NO}', timeout=10)
            res2 = self.session.get(f'http://163.13.178.184/EMSystem/Home/QRCODE?device={DEVICE_ID}&no={NO}', timeout=10)
            self.authenticated = True
            return True
        except Exception as e:
            print(f"Authentication error: {e}")
            self.authenticated = False
            return False

    def set_temperature(self, temp: str, power: str = "1"):
        if not self.authenticated:
            if not self.authenticate():
                return False, "Failed to authenticate with AC system."

        data = {
            'AreaId': AREA_ID,
            'DeviceId': DEVICE_TYPE,
            'SystemId': SYSTEM_ID,
            'TagValue[DValues][0][Tag]': 'en',
            'TagValue[DValues][0][Value]': '1',
            'TagValue[DValues][1][Tag]': 'emss',
            'TagValue[DValues][1][Value]': str(power), # 1 for on, 0 for off
            'TagValue[AValues][0][Tag]': 'tss',
            'TagValue[AValues][0][Value]': str(temp),
        }

        try:
            res_set = self.session.post('http://163.13.178.184/EMSystem/SCADA/SetSingleDevice', data=data, timeout=10)
            res_release = self.session.post('http://163.13.178.184/EMSystem/Home/ReleaseLock', timeout=10)
            status_str = "ON" if str(power) == "1" else "OFF"
            return True, f"Successfully set AC to {status_str} with temperature {temp}°C"
        except Exception as e:
            self.authenticated = False
            return False, f"Error communicating with AC system: {e}"

ac_controller = ACController()

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync slash commands with Discord
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

client = MyClient()

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

@client.tree.command(name="ac", description="Control the SG144 Air Conditioner power and temperature")
@app_commands.describe(
    temperature="The target temperature (e.g., 18, 19, 22, 26)",
    power="Power state of the AC"
)
@app_commands.choices(power=[
    app_commands.Choice(name="On", value="1"),
    app_commands.Choice(name="Off", value="0")
])
async def ac_command(interaction: discord.Interaction, temperature: str, power: app_commands.Choice[str] = None):
    await interaction.response.defer(thinking=True)
    
    power_val = power.value if power else "1"
    success, message = ac_controller.set_temperature(temperature, power=power_val)
    
    if success:
        embed = discord.Embed(
            title="❄️ AC Control Success",
            description=message,
            color=discord.Color.blue()
        )
        embed.add_field(name="Room", value="SG144", inline=True)
        embed.add_field(name="Power", value="ON" if power_val == "1" else "OFF", inline=True)
        embed.add_field(name="Target Temperature", value=f"{temperature}°C", inline=True)
        await interaction.followup.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ AC Control Failed",
            description=message,
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

@client.tree.command(name="ping", description="Check if the bot is alive")
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓 AC Bot is online.", ephemeral=True)

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("Error: DISCORD_TOKEN environment variable is not set.")
        print("Please set your token using: export DISCORD_TOKEN='your_bot_token'")
        exit(1)
    client.run(TOKEN)
