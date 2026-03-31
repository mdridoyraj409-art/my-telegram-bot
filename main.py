import logging
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Flask সার্ভার সেটআপ (বটকে জাগিয়ে রাখার জন্য)
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app_flask.run(host='0.0.0.0', port=10000)

# লগিং সেটআপ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = '8534423965:AAEqWz25jEVmtY_VVxMfFpGE89QXV1aXgxs'
ADMIN_ID = 8699821136 
BIKASH_NUMBER = "01757851152" 
GROUP_LINK = "https://t.me/+oe_rcewUi142ZmNl" 
VIDEO_REVIEW_LINK = "https://youtu.be/eNCs0b-Xfj0?si=BOryS05oSm5AcyqH"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    main_menu_keyboard = [['🏠 মূল মেন্যু']]
    reply_markup_main = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
    welcome_text = (
        "🔥 **নিউ হলগ্রাম লোকেশন প্যানেল মেইল আইডি 100% save no ban main ID plus ড্রাগ হেড শট প্যানেল**\n\n"
        f"📺 **রিভিউ ভিডিও:** {VIDEO_REVIEW_LINK}\n\n"
        "নিচের বাটন থেকে একটি প্ল্যান সিলেক্ট করুন:"
    )
    keyboard = [[InlineKeyboardButton("💎 ১ মাস - ২০০ টাকা", callback_data="plan1")],
                [InlineKeyboardButton("💎 ২ মাস - ২০০ টাকা", callback_data="plan2")],
                [InlineKeyboardButton("💎 ৩ মাস - ২৫০ টাকা", callback_data="plan3")]]
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup_main)
    await update.message.reply_text("প্ল্যান সিলেক্ট করুন:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plans = {"plan1": "১ মাস (২০০ টাকা)", "plan2": "২ মাস (২০০ টাকা)", "plan3": "৩ মাস (২৫০ টাকা)"}
    if query.data in plans:
        context.user_data['selected'] = plans[query.data]
        await query.edit_message_text(f"✅ **{plans[query.data]}** সিলেক্ট করেছেন।\n\n📱 বিকাশ: `{BIKASH_NUMBER}`\n\n⚠️ **সঠিকভাবে পেমেন্ট তথ্য দিন:**\nআপনার নাম্বারের শেষ ৪ ডিজিট এবং সঠিক TrxID লিখে পাঠান।", parse_mode='Markdown')
    elif query.data.startswith("aprv_"):
        uid = query.data.split("_")[1]
        await context.bot.send_message(chat_id=int(uid), text="🎉 **পেমেন্ট সফল!**\nনিচের লিংকে জয়েন করুন:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👥 গ্রুপে জয়েন", url=GROUP_LINK)]]))
        await query.edit_message_text("✅ অনুমোদিত হয়েছে Boss!")

async def get_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    if text == '🏠 মূল মেন্যু':
        await start(update, context)
        return
    selected = context.user_data.get('selected')
    if selected:
        # Simple validation: checks if length is ok and has some numbers/letters
        is_valid = len(text) >= 6 
        if not is_valid:
            await update.message.reply_text("❌ **দয়া করে সঠিক পেমেন্ট তথ্য দিন**", parse_mode='Markdown')
            return
        await update.message.reply_text("⌛ আপনার পেমেন্ট তথ্য জমা হয়েছে। এডমিন চেক করছে...")
        admin_text = f"🔔 **নতুন পেমেন্ট!**\n👤: {user.first_name}\n🆔: `{user.id}`\n📦: {selected}\n📝: {text}"
        btn = [[InlineKeyboardButton("Approve ✅", callback_data=f"aprv_{user.id}")]]
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=InlineKeyboardMarkup(btn))
        context.user_data['selected'] = None
    else:
        await update.message.reply_text("❌ আগে একটি প্ল্যান সিলেক্ট করুন।")

if __name__ == '__main__':
    # Flask সার্ভারটি আলাদা একটি থ্রেডে চালানো যাতে বটের কাজে বাধা না দেয়
    threading.Thread(target=run_flask, daemon=True).start()
    
    # টেলিগ্রাম বট রান করা
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), get_msg))
    app.run_polling(drop_pending_updates=True)
    
