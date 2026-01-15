from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ref = context.args[0] if context.args else None

    if user.id not in users:
        users[user.id] = {"balance": 0, "ref": 0}
        if ref and ref.isdigit():
            ref_id = int(ref)
            if ref_id in users and ref_id != user.id:
                users[ref_id]["ref"] += 1
                users[ref_id]["balance"] += 50

    keyboard = [
        [InlineKeyboardButton("📢 Refer", callback_data="refer")],
        [InlineKeyboardButton("🎬 Task", callback_data="task")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("🏧 Withdraw", callback_data="withdraw")]
    ]

    await update.message.reply_text(
        "👋 স্বাগতম!\nঘরে বসে ইনকাম করতে শুরু করো 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    user = users.get(uid)

    if query.data == "balance":
        await query.message.reply_text(
            f"💰 Balance: ৳{user['balance']}\n👥 Referrals: {user['ref']}"
        )

    elif query.data == "refer":
        link = f"https://t.me/ghore_income_bot?start={uid}"
        await query.message.reply_text(f"🔗 তোমার রেফার লিংক:\n{link}")

    elif query.data == "task":
        await query.message.reply_text(
            "🎬 Task:\nভিডিও দেখো / সাবস্ক্রাইব করো\nতারপর Screenshot পাঠাও\nReward: ৳60"
        )

    elif query.data == "withdraw":
        if user["ref"] < 15:
            await query.message.reply_text("❌ Withdraw locked\n15 referrals লাগবে")
        elif user["balance"] < 500:
            await query.message.reply_text("❌ Minimum withdraw ৳500")
        else:
            await query.message.reply_text("✅ Withdraw request sent")
            await context.bot.send_message(
                ADMIN_ID,
                f"Withdraw request\nUser: {uid}\nBalance: ৳{user['balance']}"
            )

async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📩 Screenshot received\nAdmin review করবে")
    await context.bot.send_photo(
        ADMIN_ID,
        update.message.photo[-1].file_id,
        caption=f"Proof from {update.message.from_user.id}"
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.PHOTO, screenshot))
app.run_polling()
