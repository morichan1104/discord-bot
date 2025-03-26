import os
import discord
from discord.ext import commands
from server import server_thread  # ← FastAPIを並列起動

# 環境変数の取得
TOKEN = os.environ.get("TOKEN")
TARGET_CHANNEL_ID = os.environ.get("TARGET_CHANNEL_ID")
TARGET_ROLE_IDS = [int(x) for x in os.getenv("TARGET_ROLE_IDS", "").split(",") if x.strip().isdigit()]

if TOKEN is None or TARGET_CHANNEL_ID is None or TARGET_ROLE_IDS is None:
    print("環境変数が設定されていません。")
    exit(1)

TARGET_CHANNEL_ID = int(TARGET_CHANNEL_ID)

# Intent設定
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

    # メンションフィルター
    mention_hit = False
    if any(role.id in TARGET_ROLE_IDS for role in message.role_mentions):
        mention_hit = True
        
    if not mention_hit:
        print("対象のメンションがされていないため、転送しません")
        return

    target_channel = message.guild.get_channel(TARGET_CHANNEL_ID)
    if target_channel is None or message.channel.id == TARGET_CHANNEL_ID:
        return

    base_channel = message.channel
    if isinstance(message.channel, discord.Thread):
        base_channel = message.channel.parent

    everyone_role = message.guild.default_role
    try:
        overwrites = base_channel.overwrites_for(everyone_role)
        if overwrites.read_messages is False:
            print("プライベートチャンネルなので無視")
            return
    except AttributeError:
        print("チャンネル権限取得に失敗")
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

# Webサーバー起動（Koyebの無料プラン維持のため）
server_thread()

# Bot起動
bot.run(TOKEN)
