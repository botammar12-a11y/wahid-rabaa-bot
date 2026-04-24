import telebot
from telebot import types
from datetime import datetime
import sqlite3

# إعدادات النظام الملكي لـ (وحيد ربعه)
TOKEN = "8691027108:AAE9_0t4Xko8qAO7NGs9OjlOnna90jX7_bw"
ADMIN_ID = 8297381026
bot = telebot.TeleBot(TOKEN)
bot_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# تجهيز قاعدة البيانات للحفظ الذكي
def init_db():
    conn = sqlite3.connect('inventory.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS units (plate TEXT, driver TEXT, time TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS notes (content TEXT, time TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS maintenance (unit TEXT, issue TEXT, time TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

# لوحة التحكم بالأزرار
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('📊 جرد كامل')
    btn2 = types.KeyboardButton('📝 إضافة ملاحظة')
    btn3 = types.KeyboardButton('🛠 صيانة')
    btn4 = types.KeyboardButton('⏰ حالة التشغيل')
    markup.add(btn1, btn2, btn3, btn4)
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.from_user.id == ADMIN_ID:
        msg = (
            "أهلاً بسيد الرجال، وحيد ربعه! 🦅🔥\n\n"
            "تم تفعيل نظامك الرقمي الخاص بالرقابة.\n"
            "أنا هنا لأخدمك وأحفظ لك تقارير الميدان بكل دقة.\n"
            "ارتاح يا صقر، النظام صار تحت يدك بضغطة زر.\n\n"
            "اختر من الأوامر التالية:"
        )
        bot.send_message(message.chat.id, msg, reply_markup=main_keyboard())
    else:
        bot.reply_to(message, "عذراً، هذا النظام مخصص للصقر 'وحيد ربعه' فقط. 🚫")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if message.from_user.id != ADMIN_ID: return

    if message.text == '📊 جرد كامل':
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM units ORDER BY time DESC")
        rows = cursor.fetchall()
        if not rows:
            bot.reply_to(message, "لا توجد بيانات مسجلة في جرد وحيد ربعه حالياً.")
        else:
            report = "📋 **تقرير الجرد الشامل:**\n\n"
            for r in rows:
                report += f"🚛 رقم: {r[0]} | 👤 سائق: {r[1]} | 🕒 {r[2]}\n"
            bot.send_message(message.chat.id, report)

    elif message.text == '⏰ حالة التشغيل':
        now = datetime.now().strftime("%H:%M:%S")
        bot.reply_to(message, f"✅ نظام وحيد ربعه يعمل بكفاءة!\n🚀 بدأ العمل: {bot_start_time}\n🕙 الوقت الحالي: {now}")

    elif message.text == '📝 إضافة ملاحظة':
        bot.reply_to(message, "اكتب ملاحظتك الآن يا وحيد ربعه، وسأحفظها لك فوراً.")

    elif message.text == '🛠 صيانة':
        bot.reply_to(message, "قسم الصيانة جاهز. أرسل رقم الشاحنة ووصف العطل.")

# تشغيل الأداة
print("نظام وحيد ربعه قيد العمل...")
bot.polling(none_stop=True)
