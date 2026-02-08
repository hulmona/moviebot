import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient

# --- CONFIGURATION ---
# Render Environment 
        file_id = message.text.split()[1].replace("file_", "")
        try:
            sent_msg = await client.send_cached_media(chat_id=message.chat.id, file_id=file_id)
            warning_msg = await message.reply_text(
                "⚠️ **এই ফাইলটি ৫ মিনিট পর ডিলিট হয়ে যাবে। তাই জলদি অন্য কোথাও ফরওয়ার্ড করে ext("⏳ মুভিগুলো ডাটাবেসে সেভ করা শুরু হচ্ছে... একটু অপেক্ষা করুন।")
    count = 0
    async for user_msg in client.get_chat_history(DB_CHANNEL_ID):
        file = user_msg.document or user_msg.video
        if file:
            await db.update_one(
                {"file_id": file.file_id},
                {"$set": {"file_name": file.file_name, "file_id": file.file_id}},
                upsert=True
            )
            count += 1
    await status.edit(f"✅ কাজ শেষ! মোট {count}টি ফাইল ডাটাবেসে সেভ হয়েছে।")

# --- GROUP SEARCH ---
@bot.on_message(filters.group & filters.text)
async def search(client, message):
    query = message.text
    if len(query) < 3: return
    
    files = db.find({"file_name": {"$regex": query, "$options": "i"}})
    buttons = []
    
    async for file in files.to_list(length=10):
        buttons.append([
            InlineKeyboardButton(
                text=f"🎬 {file['file_name']}", 
                url=f"https://t.me/{client.me.username}?start=file_{file['file_id']}"
            )
        ])

    if buttons:
        await message.reply_text(
            f"🔍 **আপনার সার্চ করা মুভি: {query}**\n\nনিচের বাটনে ক্লিক করে মুভিটি বট থেকে সংগ্রহ করুন।",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

print("Bot is running...")
bot.run()

