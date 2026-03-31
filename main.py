import logging
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ১. Flask সার্ভার সেটআপ (বটকে ২৪ ঘণ্টা জাগিয়ে রাখার জন্য)
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    # রেন্ডার (Render) এর জন্য পোর্ট ১০০০০ ব্যবহার করা হয়েছে
    app_flask.run(host='0.0.0.0', port=10000)

# ২. লগিং সেটআপ (বটের কার্যক্রম ট্র্যাকিং করার জন্য)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ৩. বটের প্রয়োজনীয় তথ্যসমূহ (Configuration)
TOKEN = '8534423965:AAEqWz25jEVmtY_VVxMfFpGE89QXV1aXgxs'
ADMIN_ID = 8699821136 
BIKASH_NUMBER = "01757851152" 
GROUP_LINK = "https://t.me/+oe_rcewUi142ZmNl" 
VIDEO_REVIEW_LINK = "https://youtu.be/eNCs0b-Xfj0?si=BOryS05oSm5AcyqH"

# ৪. স্টার্ট কমান্ড হ্যান্ডলার (স্বাগতম জানানো ও মেন্যু দেখানো)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear() # ইউজার ডেটা ফ্রেশ করা হলো
    
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

# ৫. বাটন ক্লিক হ্যান্ডলার (প্ল্যান সিলেক্ট ও অ্যাডমিন অ্যাপ্রুভাল)
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    plans = {"plan1": "১ মাস (২০০ টাকা)", "plan2": "২ মাস (২০০ টাকা)", "plan3": "৩ মাস (২৫০ টাকা)"}
    
    if query.data in plans:
        context.user_data['selected'] = plans[query.data]
        context.user_data['state'] = 'WAITING_FOR_PAYMENT' # স্টেট ট্র্যাকিং
        
        await query.edit_message_text(
            f"✅ **{plans[query.data]}** সিলেক্ট করেছেন।\n\n"
            f"📱 বিকাশ: `{BIKASH_NUMBER}`\n\n"
            "⚠️ **পেমেন্ট করার পর:**\nআপনার নাম্বারের শেষ ৪ ডিজিট এবং সঠিক TrxID লিখে পাঠান।", 
            parse_mode='Markdown'
        )
    elif query.data.startswith("aprv_"):
        uid = query.data.split("_")[1]
        await context.bot.send_message(
            chat_id=int(uid), 
            text="🎉 **পেমেন্ট সফল!**\nনিচের লিংকে জয়েন করুন:", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👥 গ্রুপে জয়েন", url=GROUP_LINK)]])
        )
        await query.edit_message_text("✅ অনুমোদিত হয়েছে Boss!")

# ৬. মেসেজ হ্যান্ডলার (ভেরিফিকেশন ও অ্যাডমিনকে তথ্য পাঠানো)
async def get_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    
    # মূল মেন্যু বাটন চেক
    if text == '🏠 মূল মেন্যু':
        await start(update, context)
        return

    selected_plan = context.user_data.get('selected')
    current_state = context.user_data.get('state')

    # [নতুন] যদি ইউজার কোনো প্ল্যান সিলেক্ট না করেই মেসেজ দেয়
    if not selected_plan:
        await update.message.reply_text("❌ **দয়া করে আগে একটি প্ল্যান সিলেক্ট করুন।**", parse_mode='Markdown')
        return

    # [নতুন] পেমেন্ট তথ্যের সত্যতা যাচাই
    if current_state == 'WAITING_FOR_PAYMENT':
        if len(text) < 8: # ট্রানজেকশন আইডি চেক
            await update.message.reply_text(
                "❌ **দয়া করে সঠিক ট্রানজেকশন আইডি ও শেষ ৪ ডিজিট নাম্বার লিখে পাঠান।**", 
                parse_mode='Markdown'
            )
            return
        
        # সব ঠিক থাকলে অ্যাডমিনকে (আপনাকে) জানানো হবে
        await update.message.reply_text("⌛ আপনার পেমেন্ট তথ্য জমা হয়েছে। অ্যাডমিন চেক করছে...")
        
        admin_text = (
            f"🔔 **নতুন পেমেন্ট!**\n"
            f"👤 নাম: {user.first_name}\n"
            f"🆔 আইডি: `{user.id}`\n"
            f"📦 প্ল্যান: {selected_plan}\n"
            f"📝 তথ্য: {text}"
        )
        btn = [[InlineKeyboardButton("Approve ✅", callback_data=f"aprv_{user.id}")]]
        
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(btn))
        
        # কাজ শেষে স্টেট রিসেট
        context.user_data['state'] = None
        context.user_data['selected'] = None

# ৭. মেইন ফাংশন (বট চালু করা)
if __name__ == '__main__':
    # Flask সার্ভারটি আলাদা থ্রেডে চালু করা হচ্ছে
    threading.Thread(target=run_flask, daemon=True).start()
    
    # টেলিগ্রাম অ্যাপ বিল্ড ও হ্যান্ডলার সেটআপ
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), get_msg))
    
    print("বট সফলভাবে সচল হয়েছে Boss! 🚀")
    app.run_polling(drop_pending_updates=True)
        
