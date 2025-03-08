import telebot
import json
import sqlite3
import pandas as pd
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from database import create_db, save_user
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests

# 🔹 BOT SOZLAMALARI
TOKEN = "5113714089:AAG3rgqFd_nfZI_pKv_bTjzoZURo3z2Xjng"
ADMIN_ID = 769482566  # 🔹 Admin ID
CHANNELS = ["@shoxruxxudoynazarov", "@monoqmahalla"]
# Guruh va kanal ID larini qo'shing
GROUP_ID = "@monoqmahalla"  # Guruh ID sini yozing
CHANNEL_ID = "@shoxruxxudoynazarov"  # Kanal username ni yozing

bot = telebot.TeleBot(TOKEN)
user_data = {}

# 🔹 JSON-dan mahallalarni yuklash
with open("mahalla.json", "r", encoding="utf-8") as file:
    data = json.load(file)

mahallalar = data["Xorazm viloyati"]["Shovot tumani"]

# 🔹 Tugmalarni yaratish
def get_mahalla_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for mahalla in mahallalar:
        markup.add(KeyboardButton(mahalla))
    return markup

survey_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
survey_keyboard.add(KeyboardButton("📋 So‘rovnoma boshlash"))

gender_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
gender_keyboard.add(KeyboardButton("Erkak"), KeyboardButton("Ayol"))

tuman_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
tuman_keyboard.add(KeyboardButton("Shovot tuman"))

purpose_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
purpose_keyboard.add(KeyboardButton("Ishlash"), KeyboardButton("O‘qish"), KeyboardButton("Yashash"))

salary_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
salary_keyboard.add(KeyboardButton("500$ dan kam"), KeyboardButton("500-1000$"), KeyboardButton("1000-2000$"))

location_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
location_keyboard.add(KeyboardButton("📍 Joriy joylashuvni yuborish", request_location=True))

phone_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
phone_keyboard.add(KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))

back_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
back_keyboard.add(KeyboardButton("🔙 Orqaga"))


# 🔹 Start handler
@bot.message_handler(commands=["start"])
def start_command(message):
    bot.send_message(message.chat.id,"Assalomu alaykum! Botga xush kelibsiz.")
    markup = InlineKeyboardMarkup()
    # Har bir kanal uchun tugma qo‘shamiz
    for channel in CHANNELS:
        btn = InlineKeyboardButton(f"📢 {channel[1:]}", url=f"https://t.me/{channel[1:]}")
        markup.add(btn)
    # Tekshirish tugmasi
    check_btn = InlineKeyboardButton("✅ Tekshirish", callback_data="check")
    markup.add(check_btn)
    bot.send_message(message.chat.id, "Quyidagi kanallarga a'zo bo‘ling va 'Tekshirish' tugmasini bosing!",reply_markup=markup)

# A’zolikni tekshirish uchun funksiya
def check_subscription(user_id):
    for channel in CHANNELS:
        response = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={channel}&user_id={user_id}").json()
        status = response.get("result", {}).get("status", "")

        if status not in ["member", "administrator", "creator"]:
            return False
    return True

# Inline tugmalar bosilganda ishlaydigan funksiya
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check(call):
    user_id = call.from_user.id
    if check_subscription(user_id):
        bot.send_message(call.message.chat.id, "🎉 Tabriklaymiz! Siz barcha kanallarga a’zo bo‘ldingiz.",reply_markup=survey_keyboard)
    else:
        bot.send_message(call.message.chat.id,
                         "❌ Siz hali barcha kanallarga a’zo bo‘lmadingiz. Iltimos, tekshirib qayta urining!")

# So'rovnomani boshlaymiz
@bot.message_handler(func=lambda message: message.text == "📋 So‘rovnoma boshlash")
def ask_survey(message):
    bot.send_message(message.chat.id, "So‘rovnoma boshlanmoqda... 📝\n\nTo‘liq ismingizni kiriting:")
    bot.register_next_step_handler(message, ask_gender)

# 🔹 Jinsni tanlash
def ask_gender(message):
    bot.send_message(message.chat.id, "Jinsingizni tanlang:", reply_markup=gender_keyboard)
    user_data[message.chat.id]={"full_name": message.text}
    bot.register_next_step_handler(message, ask_birth_date)

# 🔹 Tug‘ilgan sana (DD-MM-YYYY formatida)
def ask_birth_date(message):
    user_data[message.chat.id]["gender"] = message.text
    bot.send_message(message.chat.id, "Tug‘ilgan sanangizni kiriting (DD-MM-YYYY):")
    bot.register_next_step_handler(message, ask_passport)

# 🔹 Pasport seriyasi va raqami
def ask_passport(message):
    user_data[message.chat.id]["birth_date"] = message.text
    bot.send_message(message.chat.id, "Pasport seriyasi va raqamini kiriting:")
    bot.register_next_step_handler(message, ask_address)

# 🔹 Yashash manzili
def ask_address(message):
    user_data[message.chat.id]["passport"] = message.text
    bot.send_message(message.chat.id, "O‘zbekistondagi yashash manzilingizni kiriting:\n\nTuman nomi kiriting:",reply_markup=tuman_keyboard)
    bot.register_next_step_handler(message, ask_mahalla)

# 🔹 Mahallani tanlash
def ask_mahalla(message):
    user_data[message.chat.id]["address"] = message.text
    bot.send_message(message.chat.id, "Iltimos, mahallangizni tanlang:", reply_markup=get_mahalla_keyboard())
    bot.register_next_step_handler(message, ask_location)

# 🔹 Joriy joylashuv
def ask_location(message):
    user_data[message.chat.id]["mahalla"] = message.text
    bot.send_message(message.chat.id, "📍 Joriy joylashuvingizni yuboring:", reply_markup=location_keyboard)
    bot.register_next_step_handler(message, process_location)  # Lokatsiyani qayta ishlashga yo‘naltiramiz

def get_address_from_location(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {"User-Agent": "Mozilla/5.0"}  # Ba'zan API User-Agent talab qiladi
        response = requests.get(url, headers=headers).json()
        address = response.get("display_name", "Manzil topilmadi")
        return address
    except Exception as e:(
        print(f"Xatolik: {e}"))
    return "Manzil topilmadi"

def process_location(message):
    user_id = message.chat.id  # Telegram ID

    if message.location:  # Agar foydalanuvchi lokatsiya yuborgan bo‘lsa
        lat = message.location.latitude
        lon = message.location.longitude

        # Koordinatalarni matnga aylantiramiz
        location_text = get_address_from_location(lat, lon)

        user_data[user_id]["location"] = location_text  # ✅ TO‘G‘RI SAQLASH
        bot.send_message(user_id, f"📍 Sizning manzilingiz: {location_text}")

    else:  # Agar foydalanuvchi lokatsiya yubormasa
        user_data[user_id]["location"] = "Noma'lum"  # ✅ "Noma'lum" deb saqlaymiz
        bot.send_message(user_id, "❌ Siz lokatsiya yubormadingiz.")

    # 🔹 Keyingi bosqichga o‘tamiz
    bot.send_message(user_id, "Chet elga chiqishdan maqsadingizni tanlang:", reply_markup=purpose_keyboard)
    bot.register_next_step_handler(message, ask_purpose)

# 🔹 Chet elga chiqish maqsadi
def ask_purpose(message):
    user_data[message.chat.id]["purpose"] = message.text
    bot.send_message(message.chat.id, "Chet eldagi ish yoki o'qish joyingiz nomi!")
    bot.register_next_step_handler(message, ask_job)

# 🔹 Faoliyat turi
def ask_job(message):
    user_data[message.chat.id]["job"] = message.text
    bot.send_message(message.chat.id, "Oylik daromadingiz qancha:", reply_markup=salary_keyboard)
    bot.register_next_step_handler(message, ask_salary)

# 🔹 Oylik daromad
def ask_salary(message):
    user_data[message.chat.id]["salary"] = message.text
    bot.send_message(message.chat.id, "Taklif va muammoingizni yozing:")
    bot.register_next_step_handler(message, ask_feedback)

# 🔹 Taklif va muammo
def ask_feedback(message):
    user_data[message.chat.id]["feedback"] = message.text
    bot.send_message(message.chat.id, "📞 Telefon raqamingizni yuboring:", reply_markup=phone_keyboard)
    bot.register_next_step_handler(message, ask_phone)

# 🔹 Telefon raqami
def ask_phone(message):
    if message.contact and message.contact.phone_number:
        user_data[message.chat.id]["phone"] = message.contact.phone_number
    else:
        user_data[message.chat.id]["phone"] = message.text
    bot.send_message(message.chat.id, "✅ So‘rovnoma yakunlandi!")
    bot.register_next_step_handler(message, complete_survey)

# 🔹 So‘rovnomani yakunlash
def complete_survey(message):
    user_id = message.chat.id  # Telegram ID
    data = user_data.pop(user_id)
    save_user((user_id, data["full_name"], data["gender"], data["birth_date"], data["passport"],
        data["address"], data["mahalla"], data.get("location", "None"), data["purpose"], data["job"], data["salary"], data["feedback"], data["phone"]))
    bot.send_message(user_id, "✅ So‘rovnoma yakunlandi!", reply_markup=survey_keyboard)

@bot.message_handler(commands=["download"])
def download_excel(message):
    if message.chat.id == ADMIN_ID:
        conn = sqlite3.connect("users.db")
        df = pd.read_sql("SELECT * FROM users", conn)
        conn.close()

        file_path = "users.xlsx"
        df.to_excel(file_path, index=False)

        with open(file_path, "rb") as file:
            bot.send_document(ADMIN_ID, file)
    else:
        bot.send_message(message.chat.id, "❌ Sizda bu huquq yo‘q!")

@bot.message_handler(func=lambda message: message.text and message.from_user.id == ADMIN_ID and not message.text.startswith("/"))
def forward_admin_message(message):
    try:
        bot.send_message(GROUP_ID, message.text)  # Xabarni guruhga yuborish
        bot.send_message(CHANNEL_ID, message.text)  # Xabarni kanalga yuborish
        bot.reply_to(message, "Xabaringiz guruh va kanalga yuborildi!")
    except Exception as e:
        bot.reply_to(message, f"Xatolik yuz berdi: {str(e)}")

# 🔹 Botni ishga tushirish
if __name__ == "__main__":
    create_db()
    print("Bot ishga tushdi...")
    bot.polling(none_stop=True)
