import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient

# --- CONFIGURATION (Apnar Deoya Tottho) ---
API_ID = 38438389
API_HASH = "327b2592682ff56d760110350e66425e"
BOT_TOKEN = "8539975629:AAEhIKsppQ1Jz_QWDYPzwuG0Pft9tLqemyw"
MONGO_URI = "mongodb+srv://moviebot:Movie%4012345@cluster0.3qgtiud.mongodb.net/?retryWrites=true&w=majority"
DB_CHANNEL_ID = -1003344239116  # Movie Database Channel
ADMIN_ID = 7445383921 # Nijer ID ekhane boshan (Udahoron deya holo)

bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client["Cluster0"]["files"]

# --- START MESSAGE (Welcome Message) ---
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if len(message.text.split()) == 1:
        await message.reply_text(
            "👋 **হ্যালো !**\n\n"
            "আমি একটি মুভি সার্চ বট। মুভি পেতে আমাদের গ্রুপে জয়েন করুন এবং মুভির নাম লিখে সার্চ করুন।"
        )
    else:
        # Movie pathano ebong 5 minute por delete kora
        file_id = message.text.split()[1].replace("file_", "")
        try:
            sent_msg = await client.send_cached_media(chat_id=message.chat.id, file_id=file_id)
            
            warning_msg = await message.reply_text(
                "⚠️ **এই ফাইলটি ৫ মিনিট পর ডিলিট হয়ে যাবে। তাই জলদি অন্য কোথাও ফরওয়ার্ড করে সেখান থেকে ডাউনলোড করে নিন।**"
            )
            
            # ৫ মিনিট (৩০০ সেকেন্ড) অপেক্ষা করে ডিলিট করবে
            await asyncio.sleep(300)
            await sent_msg.delete()
            await warning_msg.delete()
            
        except Exception as e:
            await message.reply_text(f"❌ সমস্যা হয়েছে: {e}")

# --- INDEXING (Channel theke sob file database-e neyar command) ---
@bot.on_message(filters.command("index") & filters.user(ADMIN_ID))
async def index_files(client, message):
    status = await message.reply_text("⏳ মুভিগুলো ডাটাবেসে সেভ করা শুরু হচ্ছে... একটু অপেক্ষা করুন।")
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

# --- GROUP SEARCH (Group-e movie khunje button deya) ---
@bot.on_message(filters.group & filters.text)
async def search(client, message):
    query = message.text
    if len(query) < 3:
        return 
    
    # Database-e movie khunja
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

print("বট সফলভাবে চালু হয়েছে...")
bot.run()
