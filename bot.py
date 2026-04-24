import telebot
from telebot import types
from datetime import datetime
import sqlite3

# بيانات وحيد ربعه
TOKEN = "8691027108:AAE9_0t4Xko8qAO7NGs9OjlOnna90jX7_bw"
ADMIN_ID = 8297381026
bot = telebot.TeleBot(TOKEN)
start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def init_db():
    conn = sqlite3.connect('work_log.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS daily_log 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, plate TEXT, driver TEXT, details TEXT, time TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🚛 تسجيل جرد', '🛠 تسجيل صيانة')
    markup.add('📝 إضافة ملاحظة', '📊 عرض الجرد')
    markup.add('🏁 تقرير نهاية الدوام', '⏰ وقت البدء')
    markup.add('🗑 مسح سجل اليوم', '🔙 حذف آخر إدخال')
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.from_user.id == ADMIN_ID:
        msg = f"أهلاً بسيد الرجال، وحيد ربعه! 🦅🔥\nنظامك المتكامل جاهز ومزود بخيارات التعديل الذكي."
        bot.send_message(message.chat.id, msg, reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: True)
def handle_ops(message):
    if message.from_user.id != ADMIN_ID: return
    t = message.text
    now = datetime.now().strftime("%H:%M")
    cursor = db_conn.cursor()

    # خيارات الأزرار الثابتة
    if t == '🚛 تسجيل جرد':
        bot.reply_to(message, "أرسل: اللوحة - اسم السائق")
    elif t == '🛠 تسجيل صيانة':
        bot.reply_to(message, "أرسل: صيانة - اللوحة - العطل")
    elif t == '🗑 مسح سجل اليوم':
        cursor.execute("DELETE FROM daily_log")
        db_conn.commit()
        bot.reply_to(message, "⚠️ تم تصفير سجل اليوم بنجاح.")
    elif t == '🔙 حذف آخر إدخال':
        cursor.execute("DELETE FROM daily_log WHERE id = (SELECT MAX(id) FROM daily_log)")
        db_conn.commit()
        bot.reply_to(message, "✅ تم حذف آخر عملية سجلتها.")
    elif t == '📊 عرض الجرد':
        cursor.execute("SELECT * FROM daily_log WHERE type='جرد'")
        rows = cursor.fetchall()
        res = "📋 **الجرد الحالي:**\n" + "\n".join([f"🚛 {r[2]} | 👤 {r[3]} | 🕒 {r[5]}" for r in rows])
        bot.send_message(message.chat.id, res if rows else "الجرد فارغ.")
    elif t == '🏁 تقرير نهاية الدوام':
        cursor.execute("SELECT * FROM daily_log")
        rows = cursor.fetchall()
        if not rows: return bot.reply_to(message, "لا توجد بيانات.")
        rep = f"📜 **حصاد اليوم لـ وحيد ربعه**\n------------------\n"
        for r in rows: rep += f"🔹 [{r[1]}] {r[2]} {r[3]} {r[4]} | {r[5]}\n"
        rep += f"------------------\n✅ تم بحمد الله."
        bot.send_message(message.chat.id, rep)

    # ميزة التعديل الذكي
    elif t.startswith('تعديل'):
        try:
            new_data = t.replace('تعديل', '').strip()
            if '-' in new_data:
                p, d = new_data.split('-')
                cursor.execute("UPDATE daily_log SET plate=?, driver=? WHERE id=(SELECT MAX(id) FROM daily_log AND type='جرد')", (p.strip(), d.strip()))
                db_conn.commit()
                bot.reply_to(message, f"✅ تم تعديل آخر سجل إلى: {p.strip()} - {d.strip()}")
            else:
                bot.reply_to(message, "أرسل التعديل بهذا الشكل: تعديل لوحة - اسم")
        except:
            bot.reply_to(message, "حدث خطأ في التعديل.")

    # التسجيل العادي
    else:
        if '-' in t:
            parts = t.split('-')
            if 'صيانة' in t:
                cursor.execute("INSERT INTO daily_log (type, plate, driver, details, time) VALUES (?,?,?,?,?)", ('صيانة', parts[1].strip(), '', parts[2].strip(), now))
            else:
                cursor.execute("INSERT INTO daily_log (type, plate, driver, details, time) VALUES (?,?,?,?,?)", ('جرد', parts[0].strip(), parts[1].strip(), '', now))
            bot.reply_to(message, "✅ تم الحفظ.")
        else:
            cursor.execute("INSERT INTO daily_log (type, plate, driver, details, time) VALUES (?,?,?,?,?)", ('ملاحظة', '', '', t, now))
            bot.reply_to(message, "✅ تم حفظ الملاحظة.")
        db_conn.commit()

bot.polling(none_stop=True)
