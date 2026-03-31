import logging
import threading
from flask import Flask
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- ১. Flask সার্ভার (বটকে ২৪ ঘণ্টা সচল রাখতে) ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app_flask.run(host='0.0.0.0', port=10000)

# --- ২. লগিং সেটআপ ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- ৩. কনফিগারেশন ---
TOKEN = '8754840504:AAFBXSY-qGFB7H2OqnoMl-pZtPTEf8Geyic' 
ADMIN_ID = 8699821136 
BIKASH_NUMBER = "01757851152" 
GROUP_LINK = "https://t.me/+oe_rcewUi142ZmNl" 
VIDEO_REVIEW_LINK = "https://youtu.be/eNCs0b-Xfj0?si=BOryS05oSm5AcyqH"

# --- ৪. স্টার্ট কমান্ড ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear() 
    main_menu_keyboard = [['🏠 মূল মেন্যু']]
    reply_markup_main = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
    
    welcome_text = (
        "🔥 **নিউ হলগ্রাম লোকেশন প্যানেল মেইল আইডি 100% save no ban main ID plus ড্রাগ হেড শট প্যানেল**\n\n"
        f"📺 **রিভিউ ভিডিও:** {VIDEO_REVIEW_LINK}\n\n"
        "নিচের বাটন থেকে একটি প্ল্যান সিলেক্ট করুন:"
    )
    
    keyboard = [
        [InlineKeyboardButton("💎 ১ মাস - ২০০ টাকা", callback_data="plan1")],
        [InlineKeyboardButton("💎 ২ মাস - ২০০ টাকা", callback_data="plan2")],
        [InlineKeyboardButton("💎 ৩ মাস - ২৫০ টাকা", callback_data="plan3")]
    ]
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup_main)
    await update.message.reply_text("প্ল্যান সিলেক্ট করুন:", reply_markup=InlineKeyboardMarkup(keyboard))

# --- ৫. বাটন ক্লিক হ্যান্ডলার ---
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    plans = {"plan1": "১ মাস (২০০ টাকা)", "plan2": "২ মাস (২০০ টাকা)", "plan3": "৩ মাস (২৫০ টাকা)"}
    
    if query.data in plans:
        context.user_data['selected'] = plans[query.data]
        context.user_data['state'] = 'WAITING_FOR_PAYMENT' 
        
        pay_msg = (
            f"✅ আপনি **{plans[query.data]}** বেছে নিয়েছেন।\n\n"
            f"📱 বিকাশ নাম্বার: `{BIKASH_NUMBER}` (Personal)\n\n"
            "⚠️ **পেমেন্ট তথ্য দেওয়ার নিয়ম (উদাহরণ):**\n"
            "Last number : 2863\n"
            "TrxID : AR3HK67S\n\n"
            "এভাবে আপনার তথ্য লিখে এখানে পাঠান।"
        )
        await query.edit_message_text(pay_msg, parse_mode='Markdown')
    
    elif query.data.startswith("aprv_"):
        uid = query.data.split("_")[1]
        success_msg = "🎉 **পেমেন্ট সফল!**\n\nনিচের বাটনে ক্লিক করে গ্রুপে জয়েন করুন।"
        btn = [[InlineKeyboardButton("👥 গ্রুপে জয়েন", url=GROUP_LINK)]]
        await context.bot.send_message(chat_id=int(uid), text=success_msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(btn))
        await query.edit_message_text("✅ অনুমোদিত হয়েছে Boss!")

# --- ৬. মেসেজ হ্যান্ডলার (আপনার দেওয়া উদাহরণের ভিত্তিতে শক্তিশালী ফিল্টার) ---
async def get_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    
    if text == '🏠 মূল মেন্যু':
        await start(update, context)
        return

    selected = context.user_data.get('selected')
    state = context.user_data.get('state')

    if not selected:
        await update.message.reply_text("❌ **দয়া করে আগে একটি প্ল্যান সিলেক্ট করুন।**", parse_mode='Markdown')
        return

    if state == 'WAITING_FOR_PAYMENT':
        # Boss, এখানে চেক করা হচ্ছে টেক্সটে 'Last' এবং 'TrxID' কথাগুলো আছে কি না
        # এবং ইউজার সঠিকভাবে বড় কোনো মেসেজ দিয়েছে কি না
        valid_keywords = ["Last", "number", "TrxID", "trxid"]
        is_valid_format = any(word in text for word in valid_keywords) and len(text) > 12

        if not is_valid_format:
            error_msg = (
                "❌ **ভুল তথ্য!**\n\n"
                "দয়া করে নিচের ফরম্যাটে সঠিক পেমেন্ট তথ্য দিন:\n"
                "Last number : 2863\n"
                "TrxID : AR3HK67S"
            )
            await update.message.reply_text(error_msg, parse_mode='Markdown')
            return

        # সব ঠিক থাকলে অ্যাডমিনকে জানানো
        await update.message.reply_text("⌛ আপনার পেমেন্ট তথ্য জমা হয়েছে। এডমিন চেক করছে...")
        
        admin_text = f"🔔 <b>নতুন পেমেন্ট রিকোয়েস্ট!</b>\n👤 নাম: {user.first_name}\n🆔 আইডি: <code>{user.id}</code>\n📦 প্ল্যান: {selected}\n📝 তথ্য:\n{text}"
        btn = [[InlineKeyboardButton("Approve ✅", callback_data=f"aprv_{user.id}")]]
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(btn))
        
        context.user_data['selected'] = None
        context.user_data['state'] = None

# --- ৭. মেইন ফাংশন ---
if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), get_msg))
    
    print("Boss, কড়া সিকিউরিটি ফিল্টারসহ বট সচল হয়েছে! 🚀")
    app.run_polling(drop_pending_updates=True)
    
