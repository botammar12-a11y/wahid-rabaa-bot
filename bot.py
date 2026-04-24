import telebot
from telebot import types
from datetime import datetime
import sqlite3

# بيانات وحيد ربعه
TOKEN = "8691027108:AAE9_0t4Xko8qAO7NGs9OjlOnna90jX7_bw"
ADMIN_ID = 8297381026
bot = telebot.TeleBot(TOKEN)
start_work_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# إنشاء قاعدة بيانات متطورة
def init_db():
    conn = sqlite3.connect('work_log.db', check_same_thread=False)
    cursor = conn.cursor()
    # جدول العمليات (جرد، صيانة، ملاحظات)
    cursor.execute('''CREATE TABLE IF NOT EXISTS daily_log 
                      (type TEXT, plate TEXT, driver TEXT, details TEXT, time TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

# أزرار التحكم
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🚛 تسجيل جرد', '🛠 تسجيل صيانة', '📝 إضافة ملاحظة')
    markup.add('📊 عرض الجرد اليومي', '⏰ وقت بداية العمل')
    markup.add('🏁 تقرير نهاية الدوام')
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.from_user.id == ADMIN_ID:
        welcome_text = (
            f"مرحباً بالقائد وحيد ربعه! 🦅🔥\n\n"
            f"نظامك المتكامل جاهز للعمل.\n"
            f"بدأنا العمل في: {start_work_time}\n"
            "سأقوم بحفظ كل التفاصيل لك بكل دقة."
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: True)
def handle_operations(message):
    if message.from_user.id != ADMIN_ID: return

    if message.text == '🚛 تسجيل جرد':
        bot.reply_to(message, "أرسل البيانات كالتالي:\nلوحة - اسم السائق\n(مثال: 1234 - أحمد)")
    
    elif message.text == '🛠 تسجيل صيانة':
        bot.reply_to(message, "أرسل بيانات الصيانة كالتالي:\nصيانة - رقم اللوحة - نوع العطل")
    
    elif message.text == '📝 إضافة ملاحظة':
        bot.reply_to(message, "أرسل ملاحظتك مباشرة وسأقوم بحفظها.")

    elif message.text == '⏰ وقت بداية العمل':
        bot.reply_to(message, f"🚀 بدأ العمل اليوم الساعة: {start_work_time}")

    elif message.text == '📊 عرض الجرد اليومي':
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM daily_log WHERE type='جرد'")
        rows = cursor.fetchall()
        if not rows: bot.reply_to(message, "لا يوجد جرد مسجل حالياً.")
        else:
            res = "📋 **جرد الشاحنات الحالي:**\n"
            for r in rows: res += f"🚛 {r[1]} | 👤 {r[2]} | 🕒 {r[4]}\n"
            bot.send_message(message.chat.id, res)

    elif message.text == '🏁 تقرير نهاية الدوام':
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM daily_log")
        rows = cursor.fetchall()
        if not rows:
            bot.reply_to(message, "لا يوجد بيانات مسجلة لإصدار تقرير.")
        else:
            report = f"📜 **تقرير نهاية الدوام لـ وحيد ربعه**\n"
            report += f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}\n"
            report += f"🕒 بداية الدوام: {start_work_time}\n"
            report += "----------------------------\n"
            for r in rows:
                report += f"🔹 [{r[0]}] | {r[1]} {r[2]} {r[3]} | 🕒 {r[4]}\n"
            report += "----------------------------\n"
            report += "تم بحمد الله. يعطيك العافية يا وحيد ربعه! ✅"
            bot.send_message(message.chat.id, report)

    # معالجة النصوص المرسلة للحفظ
    else:
        time_now = datetime.now().strftime("%H:%M")
        cursor = db_conn.cursor()
        text = message.text
        if '-' in text:
            parts = text.split('-')
            if 'صيانة' in text:
                cursor.execute("INSERT INTO daily_log VALUES (?, ?, ?, ?, ?)", ('صيانة', parts[1].strip(), '', parts[2].strip(), time_now))
                bot.reply_to(message, "✅ تم تسجيل عملية الصيانة.")
            else:
                cursor.execute("INSERT INTO daily_log VALUES (?, ?, ?, ?, ?)", ('جرد', parts[0].strip(), parts[1].strip(), '', time_now))
                bot.reply_to(message, f"✅ تم جرد الشاحنة {parts[0].strip()}.")
        else:
            cursor.execute("INSERT INTO daily_log VALUES (?, ?, ?, ?, ?)", ('ملاحظة', '', '', text, time_now))
            bot.reply_to(message, "✅ تم حفظ الملاحظة.")
        db_conn.commit()

bot.polling(none_stop=True)
