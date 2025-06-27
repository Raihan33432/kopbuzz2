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

@app.route('/')
def home():
    return "Telegram bot is running!"

user_data = {}

# তোমার হ্যান্ডলার কোড (start, handle_button, handle_numbers) আগের মতোই থাকবে

async def run_bot():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    print("BOT_TOKEN:", BOT_TOKEN)
    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(handle_button))
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_numbers))

    # এই লাইনেই run_polling চালাবে কিন্তু ইভেন্ট লুপ বন্ধ করবে না
    await app_telegram.initialize()
    await app_telegram.start()
    await app_telegram.updater.start_polling()
    # এখানে intentionally অপেক্ষা করবে বট চলাকালীন
    # ইভেন্ট লুপ বন্ধ করবে না, কারণ Flask ও চলবে
    # await asyncio.Event().wait() দিয়ে অপেক্ষা করানো যায়
    await asyncio.Event().wait()

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Flask আলাদা থ্রেডে চালাও
    threading.Thread(target=run_flask).start()

    # বিদ্যমান ইভেন্ট লুপে টাস্ক চালাও
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    loop.run_forever()
