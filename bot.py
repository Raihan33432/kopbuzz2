import os
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from check import check_numbers  # তোমার Telethon চেকার

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(BOT_TOKEN)

# Dispatcher without start_polling
dispatcher = Dispatcher(bot, None, workers=0)

user_data = {}

# ——— Handlers —————————————————————
def start(update: Update, context):
    buttons = [[
        InlineKeyboardButton("✅ চেক করুন", callback_data="check"),
        InlineKeyboardButton("❌ ক্যান্সেল", callback_data="cancel")
    ]]
    update.message.reply_text(
        "👋 স্বাগতম! নিচের বাটনে ক্লিক করে নাম্বার যাচাই করুন।",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def handle_button(update: Update, context):
    query = update.callback_query
    query.answer()
    uid = query.from_user.id
    if query.data == "check":
        user_data[uid] = []
        query.message.reply_text("📥 দয়া করে নাম্বারগুলো দিন (প্রতি লাইনে একটি করে):")
    else:
        query.message.reply_text("❌ অপারেশন বাতিল করা হয়েছে।")

def handle_numbers(update: Update, context):
    uid = update.message.from_user.id
    if uid not in user_data:
        return
    numbers = [n.strip() for n in update.message.text.split("\n") if n.strip()]
    grouped = [numbers[i:i+5] for i in range(0, len(numbers), 5)]
    found = []
    for idx, grp in enumerate(grouped, start=1):
        result = context.bot.loop.run_until_complete(check_numbers(grp))
        text = f"📊 Group {idx}:\n"
        for num, ok in result.items():
            mark = "✅ Telegram Account" if ok else "❌ Not Found"
            text += f"{num} – {mark}\n"
            if ok: found.append(num)
        update.message.reply_text(text)
    if found:
        update.message.reply_text("📋 Telegram পাওয়া নাম্বার:\n" + "\n".join(found))
    else:
        update.message.reply_text("❌ কোনো টেলিগ্রাম অ্যাকাউন্ট পাওয়া যায়নি।")
    del user_data[uid]
# ——————————————————————————————

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(handle_button))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_numbers))

# Webhook endpoint
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.json, bot)
    dispatcher.process_update(update)
    return "OK"

# Root just to check
@app.route("/")
def home():
    return "Bot is alive"

if __name__ == "__main__":
    # Set webhook at startup
    url = os.getenv("APP_URL")  # e.g. https://your-app.onrender.com
    bot.set_webhook(f"{url}/webhook/{BOT_TOKEN}")
    # Run Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
