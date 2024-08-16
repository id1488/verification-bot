import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
from database import log_verification_request
import os

def load_config():
    config = {}
    with open('setup.txt', 'r') as file:
        for line in file:
            key, value = line.strip().split('=', 1)
            config[key] = value
    return config

config = load_config()
TOKEN = config.get('TOKEN')
role_id = int(config.get('role_id'))
logs_id = int(config.get('logs_id'))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="me.", intents=intents)

# Команда для начала верификации
@bot.command(name="start")
async def start_verification(ctx):
    embed = discord.Embed(title="Верификация", description="Нажмите на кнопку ниже, чтобы подать заявку на верификацию.", color=0x808080)
    view = VerificationForm(bot)
    message = await ctx.send(embed=embed, view=view)
    
    # Сохранение ID сообщения
    with open('setup.txt', 'a') as file:
        file.write(f"message_id={message.id}\n")

# Форма для верификации
class VerificationForm(View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @discord.ui.button(label="Подать заявку", style=discord.ButtonStyle.secondary)
    async def open_form(self, interaction: discord.Interaction, button: discord.ui.Button):
        log_verification_request(interaction.user.id, interaction.channel.id, interaction.guild.id)
        await interaction.response.send_modal(VerificationModal(bot=self.bot, user_id=interaction.user.id, server_id=interaction.guild.id))

class VerificationModal(Modal):
    def __init__(self, bot, user_id, server_id):
        super().__init__(title="Форма верификации")
        self.bot = bot
        self.user_id = user_id
        self.server_id = server_id

        self.add_item(TextInput(label="Ваш возраст", placeholder="Введите ваш возраст", required=True))
        self.add_item(TextInput(label="Как вы узнали о нашем сервере", placeholder="Расскажите, как вы узнали о нас", required=True))
        self.add_item(TextInput(label="Кратко о вас", placeholder="Расскажите о себе", required=True, style=discord.TextStyle.paragraph))

    async def on_submit(self, interaction: discord.Interaction):
        age = self.children[0].value
        found_us = self.children[1].value
        about_you = self.children[2].value

        log_channel = self.bot.get_channel(logs_id)

        if log_channel is None:
            await interaction.response.send_message("Ошибка: Канал для логов не найден.", ephemeral=True)
            return

        embed = discord.Embed(title="Новая заявка на верификацию", color=0x808080)
        embed.add_field(name="Пользователь", value=f"<@{self.user_id}>", inline=False)
        embed.add_field(name="Возраст", value=age, inline=False)
        embed.add_field(name="Как узнал о сервере", value=found_us, inline=False)
        embed.add_field(name="О себе", value=about_you, inline=False)

        view = VerificationResponseView(self.bot, user_id=self.user_id)

        await log_channel.send(embed=embed, view=view)
        await interaction.response.send_message("Ваша заявка отправлена на рассмотрение!", ephemeral=True)

class VerificationResponseView(View):
    def __init__(self, bot, user_id):
        super().__init__()
        self.bot = bot
        self.user_id = user_id

    @discord.ui.button(label="Принять", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(role_id)
        user = interaction.guild.get_member(self.user_id)

        if role is None:
            await interaction.response.send_message("Ошибка: Роль не найдена.", ephemeral=True)
            return

        if user is None:
            await interaction.response.send_message("Ошибка: Пользователь не найден на сервере.", ephemeral=True)
            return

        try:
            await user.add_roles(role)
            await user.send(f"Ваша заявка на верификацию была одобрена на сервере {interaction.guild.name}!")
            await interaction.message.delete()  # Удаление сообщения с логом
            await interaction.response.send_message(f"Пользователь {user.mention} был верифицирован и получил роль.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Не удалось добавить роль или отправить сообщение пользователю. Возможно, у бота недостаточно прав.", ephemeral=True)

    @discord.ui.button(label="Отклонить", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RejectionModal(bot=self.bot, user_id=self.user_id))

class RejectionModal(Modal):
    def __init__(self, bot, user_id):
        super().__init__(title="Причина отказа")
        self.bot = bot
        self.user_id = user_id

        self.add_item(TextInput(label="Причина отказа", placeholder="Введите причину отказа", required=True))

    async def on_submit(self, interaction: discord.Interaction):
        reason = self.children[0].value
        user = self.bot.get_user(self.user_id)

        if user is None:
            await interaction.response.send_message("Ошибка: Пользователь не найден.", ephemeral=True)
            return

        try:
            await user.send(f"Ваша заявка на верификацию была отклонена на сервере {interaction.guild.name}.\nПричина отказа: {reason}")
            await interaction.message.delete()  # Удаление сообщения с логом
            await interaction.response.send_message(f"Пользователю {user.mention} было отправлено сообщение с причиной отказа.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(f"Заявка пользователя {user.mention} была отклонена, так как у него закрыты ЛС.", ephemeral=True)
            await interaction.message.delete()  # Удаление сообщения с логом

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    # Загрузка ID сообщения из файла
    try:
        with open('setup.txt', 'r') as file:
            for line in file:
                if line.startswith('message_id='):
                    start_message_id = int(line.strip().split('=', 1)[1])
                    channel_id = int(config.get('CHANNEL_ID')) 
                    
                    channel = bot.get_channel(channel_id)
                    if channel:
                        message = await channel.fetch_message(start_message_id)
                        if message:
                            embed = discord.Embed(title="Верификация", description="Нажмите на кнопку ниже, чтобы подать заявку на верификацию.", color=0x808080)
                            view = VerificationForm(bot)
                            await message.edit(embed=embed, view=view)
    except FileNotFoundError:
        print("Файл setup.txt не найден.")
    except Exception as e:
        print(f"Ошибка при загрузке сообщения: {e}")

bot.run(TOKEN)
