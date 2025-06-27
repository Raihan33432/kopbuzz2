import os
import threading
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

app = Flask(__name__)

# ওয়েব সার্ভার রুট (Render পোর্ট detect করার জন্য)
@app.route('/')
def home():
    return "Telegram bot is running!"

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"/start called by user {update.message.from_user.id}")
    buttons = [[
        InlineKeyboardButton("✅ চেক করুন", callback_data="check"),
        InlineKeyboardButton("❌ ক্যান্সেল", callback_data="cancel")
    ]]
    await update.message.reply_text(
        "👋 স্বাগতম! নিচের বাটনে ক্লিক করে নাম্বার যাচাই করুন।",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Button clicked: {update.callback_query.data} by user {update.callback_query.from_user.id}")
    query = update.callback_query
    await query.answer()
    if query.data == "check":
        user_data[query.from_user.id] = []
        await query.message.reply_text("📥 দয়া করে নাম্বারগুলো দিন (প্রতি লাইনে একটি করে):")
    elif query.data == "cancel":
        await query.message.reply_text("❌ অপারেশন বাতিল করা হয়েছে।")

async def handle_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Numbers received from {update.message.from_user.id}: {update.message.text}")
    user_id = update.message.from_user.id
    if user_id not in user_data:
        return
    text = update.message.text.strip()
    numbers = [n.strip() for n in text.split("\n") if n.strip()]
    grouped = [numbers[i:i+5] for i in range(0, len(numbers), 5)]
    all_found = []
    # এখানে তোমার check_numbers ফাংশন দিয়ে চেক করো
    # এখন ডেমো হিসেবে আমরা সব নাম্বারই Not Found দেখাবো
    for idx, group in enumerate(grouped, start=1):
        # result = await check_numbers(group)  # তোমার চেক ফাংশন কল করো
        result = {num: False for num in group}  # ডেমো
        formatted = f"📊 Group {idx}:\n"
        for num, status in result.items():
            mark = "✅ Telegram Account" if status else "❌ Not Found"
            formatted += f"{num} – {mark}\n"
            if status:
                all_found.append(num)
        await update.message.reply_text(formatted)
    if all_found:
        await update.message.reply_text("📋 Telegram পাওয়া নাম্বার:\n" + "\n".join(all_found))
    else:
        await update.message.reply_text("❌ কোনো টেলিগ্রাম অ্যাকাউন্ট পাওয়া যায়নি।")
    del user_data[user_id]

async def run_bot():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    print("BOT_TOKEN:", BOT_TOKEN)  # Debug: টোকেন লোগে দেখাবে
    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(handle_button))
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_numbers))
    await app_telegram.run_polling()

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()

    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    loop.run_forever()
