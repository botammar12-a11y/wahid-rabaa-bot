import telebot
import sqlite3
from datetime import datetime
import os

# توكن البوت الخاص بك
TOKEN = "8691027108:AAE9_0t4Xko8qAO7NGs9OjlOnna90jX7_bw"
bot = telebot.TeleBot(TOKEN)

# --- إنشاء وتنظيم قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('wahid_rabaa.db', check_same_thread=False)
    c = conn.cursor()
    # جدول تسجيل الشاحنات (رقم اللوحة، السائق، التاريخ)
    c.execute('''CREATE TABLE IF NOT EXISTS fleet 
                 (plate_no TEXT, driver_name TEXT, entry_time TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

# --- أوامر البوت ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🦅 **مرحباً بك في نظام وحيد ربعه الملكي** 🦅\n\n"
        "يا هلا يا عماري، أنا جاهز لتنفيذ الأوامر.\n"
        "استخدم الأوامر التالية:\n"
        "1️⃣ لتسجيل شاحنة: أرسل (تسجيل رقم_اللوحة اسم_السائق)\n"
        "2️⃣ لعرض السجل: أرسل /report"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text.startswith('تسجيل'))
def register_truck(message):
    try:
        # تقسيم الرسالة: تسجيل 1234 محمد
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "⚠️ خطأ! اكتب: تسجيل [اللوحة] [الاسم]")
            return
            
        plate = parts[1]
        driver = parts[2]
        time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO fleet VALUES (?, ?, ?)", (plate, driver, time_now))
        db_conn.commit()
        
        bot.reply_to(message, f"✅ تم التسجيل بنجاح:\n🚛 اللوحة: {plate}\n👤 السائق: {driver}\n⏰ الوقت: {time_now}")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {str(e)}")

@bot.message_handler(commands=['report'])
def show_report(message):
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM fleet ORDER BY entry_time DESC LIMIT 10")
    rows = cursor.fetchall()
    
    if not rows:
        bot.reply_to(message, "📭 السجل فارغ حالياً.")
        return
        
    report = "📋 **آخر 10 شاحنات مسجلة:**\n\n"
    for row in rows:
        report += f"🔹 {row[0]} | {row[1]} | {row[2]}\n"
    
    bot.reply_to(message, report, parse_mode='Markdown')

# --- تشغيل البوت بذكاء (Infinity Polling) ---
print("🦅 نظام وحيد ربعه يعمل الآن في السحاب...")
bot.infinity_polling()
