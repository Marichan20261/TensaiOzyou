import discord
import os
import google.generativeai as genai
from dotenv import load_dotenv
import threading
from flask import Flask

# .env 読み込み（最初に実行！）
load_dotenv()

# Discordトークン
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN is None:
    raise ValueError("DISCORD_BOT_TOKEN is not set in the .env file")

# Google Gemini APIキー
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY is None:
    raise ValueError("GOOGLE_API_KEY is not set in the .env file")

# キャラ設定ファイルを読み込む
with open("character.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# Google Geminiの設定
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

# Flaskサーバー（Render無料プラン対策）
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# Discordクライアント設定（intentsを有効に）
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Geminiの応答生成関数
async def generate_gemini_reply(user_input, user_name):
    full_prompt = (
        f"{SYSTEM_PROMPT}\n"
        f"参考程度にメッセージをくれた人の名前は「{user_name}」です。\n"
        f"彼に話しかけるときは『{user_name}さん、何かご用ですの？』のように、優雅に名前を呼びかけてから応答を始めてください。\n"
        f"{user_input}"
    )
    response = model.generate_content(full_prompt)
    return response.text

# 起動時イベント
@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")

# メッセージ受信時イベント
@client.event
async def on_message(message):
    if message.author.bot:
        return
    if client.user in message.mentions:
        user_input = message.content.replace(f"<@{client.user.id}>", "").strip()
        user_name = message.author.display_name  # 表示名で取得
        await message.channel.typing()
        reply = await generate_gemini_reply(user_input, user_name)
        await message.channel.send(reply)

# メイン処理
if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    client.run(TOKEN)
