from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from check import check_numbers
import os

user_data = {}
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[
        InlineKeyboardButton("✅ চেক করুন", callback_data="check"),
        InlineKeyboardButton("❌ ক্যান্সেল", callback_data="cancel")
    ]]
    await update.message.reply_text(
        "👋 স্বাগতম! নিচের বাটনে ক্লিক করে নাম্বার যাচাই করুন।",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "check":
        user_data[query.from_user.id] = []
        await query.message.reply_text("📥 দয়া করে নাম্বারগুলো দিন (প্রতি লাইনে একটি করে):")
    elif query.data == "cancel":
        await query.message.reply_text("❌ অপারেশন বাতিল করা হয়েছে।")

async def handle_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        return
    text = update.message.text.strip()
    numbers = [n.strip() for n in text.split("\n") if n.strip()]
    grouped = [numbers[i:i+5] for i in range(0, len(numbers), 5)]
    all_found = []
    for idx, group in enumerate(grouped, start=1):
        result = await check_numbers(group)
        formatted = f"📊 Group {idx}:\n
"
        for num, status in result.items():
            mark = "✅ Telegram Account" if status else "❌ Not Found"
            formatted += f"{num} – {mark}\n"
            if status:
                all_found.append(num)
        await update.message.reply_text(formatted)
    if all_found:
        await update.message.reply_text("📋 Telegram পাওয়া নাম্বার:
" + "\n".join(all_found))
    else:
        await update.message.reply_text("❌ কোনো টেলিগ্রাম অ্যাকাউন্ট পাওয়া যায়নি।")
    del user_data[user_id]

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_numbers))
    app.run_polling()
