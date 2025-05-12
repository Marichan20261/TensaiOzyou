import discord
import os
import google.generativeai as genai
from dotenv import load_dotenv
import threading
from flask import Flask

# .env 読み込み
load_dotenv()

# DiscordトークンとGemini APIキー
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if TOKEN is None or GOOGLE_API_KEY is None:
    raise ValueError("環境変数 DISCORD_BOT_TOKEN または GOOGLE_API_KEY が設定されていません")

# キャラ設定読み込み
with open("character.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# Gemini 設定
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

# Flaskサーバー（Render無料プラン維持）
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# Discordクライアント設定
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 表示名 → あだ名
NICKNAME_MAP = {
    "Yamada": "ヤマちん",
    "Aoi": "あおっち",
    "Sakura": "さくにゃん",
    # ここに追加
}

# Gemini 応答生成関数
async def generate_gemini_reply(user_input, display_name, nickname):
    full_prompt = (
        f"{SYSTEM_PROMPT}\n"
        f"話しかけてきた人の表示名は「{display_name}」、あだ名は「{nickname}」です。\n"
        f"{user_input}"
    )
    response = model.generate_content(full_prompt)
    return response.text

# Bot起動時
@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")

# メッセージ受信時
@client.event
async def on_message(message):
    if message.author.bot:
        return

    if client.user in message.mentions:
        display_name = message.author.display_name
        nickname = NICKNAME_MAP.get(display_name, display_name)
        user_input = message.content.replace(f"<@{client.user.id}>", "").strip()

        await message.channel.typing()

        if user_input == "":
            # メンションだけ → 定型文で応答
            await message.channel.send(f"{nickname}さん、何かご用ですの？")
        else:
            # 通常応答
            reply = await generate_gemini_reply(user_input, display_name, nickname)
            await message.channel.send(reply)

# 実行
if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    client.run(TOKEN)
