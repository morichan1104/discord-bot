import os
import discord
from discord.ext import commands
from server import server_thread


TOKEN = os.environ.get("TOKEN")
TARGET_CHANNEL_ID = int(os.environ.get("TARGET_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'ログインしました: {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    target_channel = message.guild.get_channel(TARGET_CHANNEL_ID)
    if target_channel is None or message.channel.id == TARGET_CHANNEL_ID:
        return

    # スレッドなら親チャンネルを使う
    base_channel = message.channel
    if isinstance(message.channel, discord.Thread):
        base_channel = message.channel.parent

    # プライベートチャンネルなら無視
    everyone_role = message.guild.default_role
    try:
        overwrites = base_channel.overwrites_for(everyone_role)
        if overwrites.read_messages is False:
            print("プライベートチャンネルなので無視")
            return
    except AttributeError:
        print("チャンネル権限取得に失敗（対応していないチャンネルタイプ）")
        return

    category_name = base_channel.category.name if base_channel.category else "カテゴリなし"
    channel_name = base_channel.name
    author_name = message.author.display_name
    content_snippet = message.content[:50] + ("..." if len(message.content) > 50 else "")
    message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"

    log_message = (
        f"{author_name} | {message_link}\n"
        f"```{content_snippet}```\n"
    )

    try:
        await target_channel.send(log_message)
        print("転送成功")
    except Exception as e:
        print(f"転送失敗: {e}")

    await bot.process_commands(message)

# Koyeb用 サーバー立ち上げ
server_thread()

bot.run(TOKEN)
