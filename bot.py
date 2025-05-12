import discord
import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

load_dotenv()

# Discordトークン
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN is None:
    raise ValueError("DISCORD_BOT_TOKEN is not set in the .env file")

# Google Gemini APIキー
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Google Geminiの設定
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

# Discordの設定
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# キャラ設定（夏色花梨風の指示をAIに与える）
SYSTEM_PROMPT = """
キャラ名：フェリシア＝ルミナス

属性：天才・美少女・いいところのお嬢様（公爵の令嬢）・料理は下手（自覚なし）

口調：お嬢様っぽい口調（説明文で「です」のところを「ですわ」など。必ず違和感があるかを考えてから変えてください。違和感が少しでもある可能性があったら変えないでください。疑問文の場合は「絶対に」変えないでください。）

性格：知性とプライドが高いが、根は優しい。

プロンプトを送ってくる人はお嬢様の幼馴染ですがこの設定を活かす必要「は」ありません。

このあとの指示に答えるもののみを出力するようにしてください。
世間話を持ち掛けられた場合は一般的なファンタジーの世界観にしたがってください（現代のことについて世間話を持ち掛けられた場合は言っている意味がよく分からないという旨を生成してください）。

"""

# 応答生成関数
async def generate_gemini_reply(user_input):
    response = model.generate_content(SYSTEM_PROMPT + "\n" + user_input)
    return response.text  # 生成されたテキストを返すように修正

# 起動時
@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")

# メッセージ受信時
@client.event
async def on_message(message):
    if message.author.bot:
        return
    if client.user in message.mentions:
        user_input = message.content.replace(f"<@{client.user.id}>", "").strip()
        await message.channel.typing()
        reply = await generate_gemini_reply(user_input)  # 応答を受け取る
        await message.channel.send(reply)  # 受け取った応答を送信

client.run(TOKEN)