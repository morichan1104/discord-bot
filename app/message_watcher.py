import os
import discord
from discord.ext import commands
from server import server_thread  # ← FastAPIを並列起動

# 環境変数の取得
TOKEN = os.environ.get("TOKEN")
TARGET_CHANNEL_ID = os.environ.get("TARGET_CHANNEL_ID")
TARGET_CHANNEL_ID_SECRET = os.environ.get("TARGET_CHANNEL_ID_SECRET")

if TOKEN is None or TARGET_CHANNEL_ID is None or TARGET_CHANNEL_ID_SECRET is None:
    print("環境変数が設定されていません。")
    exit(1)

TARGET_CHANNEL_ID = int(TARGET_CHANNEL_ID)
TARGET_CHANNEL_ID_SECRET = int(TARGET_CHANNEL_ID_SECRET)

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
    
    # デバッグ開始
    print("DEBUG ids:",
      "TARGET_CHANNEL_ID=", TARGET_CHANNEL_ID, type(TARGET_CHANNEL_ID),
      "TARGET_CHANNEL_ID_SECRET=", TARGET_CHANNEL_ID_SECRET, type(TARGET_CHANNEL_ID_SECRET))

    target_channel = message.guild.get_channel(TARGET_CHANNEL_ID_SECRET)
    print("DEBUG target_channel:", target_channel)

    if target_channel is None:
        print("SKIP: target_channel is None (id mismatch / cache / permission)")
        return

    if message.channel.id == TARGET_CHANNEL_ID_SECRET:
        print("SKIP: message is in target channel")
        return

    print("DEBUG role_mentions:", [r.id for r in message.role_mentions])
    # デバッグ終了
    
    if message.author.bot:
        return

    base_channel = message.channel
    if isinstance(message.channel, discord.Thread):
        base_channel = message.channel.parent
        
    everyone_role = message.guild.default_role
    
    # プライベートフィルター
    try:
        overwrites = base_channel.overwrites_for(everyone_role)
        if overwrites.read_messages is False:
            print("プライベートチャンネルのため、マル㊙️チャンネルに転送します")
            target_channel = message.guild.get_channel(TARGET_CHANNEL_ID_SECRET)
        else:
            print("通常チャンネルに転送します")
            target_channel = message.guild.get_channel(TARGET_CHANNEL_ID)
    except AttributeError:
        print("チャンネル権限取得に失敗")
        return
    
    if target_channel is None or message.channel.id == TARGET_CHANNEL_ID:
        return

    category_name = base_channel.category.name if base_channel.category else "カテゴリなし"
    channel_name = base_channel.name
    author_name = message.author.display_name
    
    content = message.content
    for user in message.mentions:
        content = content.replace(f"<@{user.id}>", f"@{user.display_name}")
        content = content.replace(f"<@!{user.id}>", f"@{user.display_name}")
    for role in message.role_mentions:
        content = content.replace(f"<@&{role.id}>", f"@{role.name}")
    content_snippet = content[:50] + ("..." if len(content) > 50 else "")
    
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
