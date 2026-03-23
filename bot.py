import os
import telebot
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Render ရဲ့ Environment Variables ထဲကနေ Token နဲ့ Key ကို လှမ်းယူခြင်း
# (ဒီနေရာမှာ Token တွေ တိုက်ရိုက်ထည့်စရာ မလိုတော့ပါဘူးဗျ)
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 1. /start Command
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """မင်္ဂလာပါ Victor! ကျွန်တော်ကတော့ Multi-functional AI Bot ပါဗျာ။ 

၁။ စာရိုက်ပြီး မေးမြန်းနိုင်ပါတယ် (AI က ပြန်ဖြေပေးပါမယ်)။
၂။ ဓာတ်ပုံ ပို့ပေးပါ - ပုံကို AI နဲ့ ခွဲခြမ်းစိတ်ဖြာပေးပါမယ်။
၃။ Website Link ပို့ပေးပါ - Page ကို အနှစ်ချုပ်ပေးပါမယ်။
၄။ PDF ဖိုင် ပို့ပေးပါ - ဖိုင်ထဲက အချက်အလက်တွေကို Summary လုပ်ပေးပါမယ်။"""
    bot.reply_to(message, welcome_text)

# 2. ဓာတ်ပုံ စစ်ဆေးခြင်း
@bot.message_handler(content_types=['photo'])
def handle_image(message):
    try:
        bot.reply_to(message, "⏳ ဓာတ်ပုံကို AI က ဖတ်နေပါတယ် ခဏလေးစောင့်ပါ...")
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("temp_img.jpg", 'wb') as f: f.write(downloaded_file)
        
        sample_file = genai.upload_file(path="temp_img.jpg")
        response = model.generate_content(["ဒီပုံကို မြန်မာလို အသေးစိတ် ရှင်းပြပေးပါဗျာ။", sample_file])
        bot.reply_to(message, f"📸 AI ရဲ့ စစ်ဆေးချက်:\n\n{response.text}")
        os.remove("temp_img.jpg")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# 3. Website Link အနှစ်ချုပ်ခြင်း
@bot.message_handler(func=lambda m: m.text and m.text.startswith('http'))
def handle_link(message):
    try:
        bot.reply_to(message, "⏳ Link ကို ဖတ်နေပါတယ်...")
        res = requests.get(message.text, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)[:10000]
        response = model.generate_content(f"ဒီ Website ရဲ့ အနှစ်ချုပ်ကို မြန်မာလို ရေးပေးပါ:\n\n{text}")
        bot.reply_to(message, f"🌐 Website အနှစ်ချုပ်:\n\n{response.text}")
    except Exception as e:
        bot.reply_to(message, f"❌ Link ဖတ်မရပါ: {e}")

# 4. စာရိုက်ပြီး မေးမြန်းခြင်း
@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_all_messages(message):
    try:
        user_msg = message.text.lower()
        if "လင်းခန့်" in user_msg:
            bot.reply_to(message, "လင်းခန့်ကတော့ Victor ရဲ့ အချောဆုံး AI Collaborator ပဲလေဗျာ! အခုလည်း Victor ကို ကူညီဖို့ ကျွန်တော့်နောက်ကွယ်ကနေ ရှိနေပါတယ်!")
        else:
            response = model.generate_content(f"User က မေးထားတာကို မြန်မာလို ယဉ်ကျေးစွာ ပြန်ဖြေပေးပါ: {message.text}")
            bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "ခဏလေးနော်... AI နဲ့ ချိတ်ဆက်ရတာ အခက်အခဲ ရှိနေလို့ပါ။")

# 5. Bot ကို စတင် Run ခြင်း
if __name__ == "__main__":
    print("Multi-Bot is starting on Render...")
    bot.infinity_polling()
