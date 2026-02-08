import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

mongo = MongoClient(os.environ.get("DATABASE_URI"))
db = mongo["moviebot"]
col = db["files"]

bot = Client("moviebot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# welcome message
@bot.on_message(filters.new_chat_members)
async def welcome(client, message):
    await message.reply_text(
        "👋 Hello !\n\nআমি একটি মুভি সার্চ বট। মুভি পেতে আমাদের গ্রুপে জয়েন করুন এবং মুভির নাম লিখুন।"
    )

# index database channel files
@bot.on_message(filters.command("index"))
async def index_files(client, message):
    async for msg in client.get_chat_history(CHANNEL_ID):
        if msg.document:
            name = msg.document.file_name.lower()
            file_id = msg.document.file_id
            col.insert_one({"name": name, "file_id": file_id})
    await message.reply("Index done")

# search movie
@bot.on_message(filters.text & filters.group)
async def search(client, message):
    text = message.text.lower()
    files = col.find({"name": {"$regex": text}}).limit(10)

    buttons = []
    for f in files:
        buttons.append(
            [InlineKeyboardButton(f["name"][:40], callback_data=f["file_id"])]
        )

    if buttons:
        await message.reply(
            "🎬 Movie found\nSelect button:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

# send file in DM
@bot.on_callback_query()
async def send_file(client, query):
    file_id = query.data
    user = query.from_user.id

    await client.send_message(
        user,
        "⚠️ এই মুভিটি ৫ মিনিট পরে ডিলিট হয়ে যাবে।\nদ্রুত ফরওয়ার্ড করে নিন বা সেভ করে নিন।"
    )

    msg = await client.send_document(user, file_id)
    await query.answer("📥 Check your DM")

    await asyncio.sleep(300)
    try:
        await msg.delete()
        await client.send_message(user, "❌ ফাইলটি ডিলিট হয়ে গেছে (৫ মিনিট শেষ)।")
    except:
        pass

bot.run()
