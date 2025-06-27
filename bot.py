import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from check import check_numbers

# Environment Variables
BOT_TOKEN    = os.getenv("BOT_TOKEN")
APP_URL      = os.getenv("APP_URL")    # e.g. https://your-service.onrender.com
PORT         = int(os.getenv("PORT", "5000"))
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL  = f"{APP_URL}{WEBHOOK_PATH}"

# Build the bot application
application = ApplicationBuilder().token(BOT_TOKEN).build()
user_data = {}

# Handlers
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
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    if q.data == "check":
        user_data[uid] = []
        await q.message.reply_text("📥 দয়া করে নাম্বারগুলো দিন (প্রতি লাইনে একটি করে):")
    else:
        await q.message.reply_text("❌ অপারেশন বাতিল করা হয়েছে।")

async def handle_numbers(update: Update, context):
    uid = update.message.from_user.id
    if uid not in user_data:
        return
    numbers = [n.strip() for n in update.message.text.split("\n") if n.strip()]
    groups = [numbers[i:i+5] for i in range(0, len(numbers), 5)]
    found = []
    for idx, grp in enumerate(groups, start=1):
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

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_button))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_numbers))

if __name__ == "__main__":
    # Set webhook properly
    print("Setting webhook to:", WEBHOOK_URL)
    # Await the coroutine
    asyncio.run(application.bot.set_webhook(WEBHOOK_URL))

    # Start webhook server using python-telegram-bot's built-in
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=WEBHOOK_URL,
        webserver_kwargs={"ssl_context": None}
    )
