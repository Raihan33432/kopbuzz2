import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from check import check_numbers  # তোমার Telethon ভিত্তিক চেকার

# Flask অ্যাপ
app = Flask(__name__)

# Environment Variables
BOT_TOKEN    = os.getenv("BOT_TOKEN")
APP_URL      = os.getenv("APP_URL")      # e.g. https://kopbuzz2.onrender.com
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"

# Telegram Application তৈরির
application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .build()
)

# ইউজার ডাটা স্টোরেজ
user_data = {}

# ————— Handlers —————
async def start(update: Update, context):
    buttons = [[
        InlineKeyboardButton("✅ চেক করুন", callback_data="check"),
        InlineKeyboardButton("❌ ক্যান্সেল", callback_data="cancel")
    ]]
    await update.message.reply_text(
        "👋 স্বাগতম! নিচের বাটনে ক্লিক করে নাম্বার যাচাই করুন।",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_button(update: Update, context):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    if query.data == "check":
        user_data[uid] = []
        await query.message.reply_text("📥 দয়া করে নাম্বারগুলো দিন (প্রতি লাইনে একটি করে):")
    else:
        await query.message.reply_text("❌ অপারেশন বাতিল করা হয়েছে।")

async def handle_numbers(update: Update, context):
    uid = update.message.from_user.id
    if uid not in user_data:
        return
    numbers = [n.strip() for n in update.message.text.split("\n") if n.strip()]
    grouped = [numbers[i:i+5] for i in range(0, len(numbers), 5)]
    found = []
    for idx, grp in enumerate(grouped, start=1):
        result = await check_numbers(grp)
        text = f"📊 Group {idx}:\n"
        for num, ok in result.items():
            mark = "✅ Telegram Account" if ok else "❌ Not Found"
            text += f"{num} – {mark}\n"
            if ok:
                found.append(num)
        await update.message.reply_text(text)
    if found:
        await update.message.reply_text("📋 Telegram পাওয়া নাম্বার:\n" + "\n".join(found))
    else:
        await update.message.reply_text("❌ কোনো টেলিগ্রাম অ্যাকাউন্ট পাওয়া যায়নি।")
    del user_data[uid]
# ——————————————————

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_button))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_numbers))

# Webhook এন্ডপয়েন্ট
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    # প্রাপ্ত update-কে asyncio loop-এ process_update হিসেবে পাঠাও
    loop = asyncio.get_event_loop()
    loop.create_task(application.process_update(update))
    return "OK", 200

# Health-check রুট
@app.route("/")
def index():
    return "Bot is alive"

if __name__ == "__main__":
    # Webhook সেটআপ
    webhook_url = f"{APP_URL}{WEBHOOK_PATH}"
    print("Setting webhook to:", webhook_url)
    asyncio.run(application.bot.set_webhook(webhook_url))

    # Flask সার্ভার চালাও
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
