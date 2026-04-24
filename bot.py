import telebot
from telebot import types
from datetime import datetime
import sqlite3

# إعدادات النظام الملكي لـ (وحيد ربعه)
TOKEN = "8691027108:AAE9_0t4Xko8qAO7NGs9OjlOnna90jX7_bw"
ADMIN_ID = 8297381026
bot = telebot.TeleBot(TOKEN)
start_work_time = datetime.now().strftime("%Y-%m-%d %H:%M")

# تجهيز قاعدة البيانات
def init_db():
    conn = sqlite3.connect('wahid_work.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS daily_log 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, plate TEXT, driver TEXT, details TEXT, time TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

# لوحة التحكم الرئيسية (الأزرار)
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🚛 تسجيل جرد', '🛠 تسجيل صيانة')
    markup.add('📝 إضافة ملاحظة', '📊 عرض الجرد اليومي')
    markup.add('🏁 تقرير نهاية الدوام', '⏰ وقت بداية العمل')
    markup.add('🗑 مسح سجل اليوم', '🔙 حذف آخر إدخال')
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.from_user.id == ADMIN_ID:
        msg = (f"يا هلا بـ وحيد ربعه! 🦅🔥\n\n"
               f"نظامك المتكامل جاهز لخدمتك في الميدان.\n"
               f"استخدم الأزرار بالأسفل للإدارة، وللتعديل أرسل:\n"
               f"(تعديل اللوحة القديمة - اللوحة الجديدة - الاسم)")
        bot.send_message(message.chat.id, msg, reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text
    now = datetime.now().strftime("%H:%M")
    cursor = db_conn.cursor()

    if text == '🚛 تسجيل جرد':
        bot.reply_to(message, "أرسل البيانات كالتالي:\nاللوحة - اسم السائق\nمثال: 1234 - محمد")
    
    elif text == '🛠 تسجيل صيانة':
        bot.reply_to(message, "أرسل بيانات الصيانة:\nصيانة - اللوحة - نوع العطل\nمثال: صيانة - 5566 - تغيير زيت")

    elif text == '⏰ وقت بداية العمل':
        bot.reply_to(message, f"🚀 بدأ العمل اليوم الساعة: {start_work_time}")

    elif text == '🗑 مسح سجل اليوم':
        cursor.execute("DELETE FROM daily_log")
        db_conn.commit()
        bot.reply_to(message, "⚠️ تم تصفير سجل اليوم بنجاح يا وحيد ربعه.")

    elif text == '🔙 حذف آخر إدخال':
        cursor.execute("DELETE FROM daily_log WHERE id = (SELECT MAX(id) FROM daily_log)")
        db_conn.commit()
        bot.reply_to(message, "✅ تم حذف آخر عملية سجلتها.")

    elif text == '📊 عرض الجرد اليومي':
        cursor.execute("SELECT * FROM daily_log WHERE type='جرد'")
        rows = cursor.fetchall()
        if not rows: bot.reply_to(message, "الجرد فارغ حالياً.")
        else:
            res = "📋 **جرد الشاحنات الحالي:**\n"
            for r in rows: res += f"🚛 {r[2]} | 👤 {r[3]} | 🕒 {r[5]}\n"
            bot.send_message(message.chat.id, res)

    elif text == '🏁 تقرير نهاية الدوام':
        cursor.execute("SELECT * FROM daily_log")
        rows = cursor.fetchall()
        if not rows: bot.reply_to(message, "لا توجد بيانات لتقرير اليوم.")
        else:
            report = f"📜 **تقرير نهاية الدوام لـ وحيد ربعه**\n"
            report += f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}\n------------------\n"
            for r in rows:
                report += f"🔹 [{r[1]}] {r[2]} {r[3]} {r[4]} | {r[5]}\n"
            report += "------------------\n✅ تم العمل بحمد الله."
            bot.send_message(message.chat.id, report)

    # ميزة التعديل الذكي
    elif text.startswith('تعديل'):
        try:
            parts = text.split('-')
            old_p = parts[0].replace('تعديل', '').strip()
            new_p = parts[1].strip()
            new_d = parts[2].strip()
            cursor.execute("UPDATE daily_log SET plate=?, driver=? WHERE plate=? AND type='جرد'", (new_p, new_d, old_p))
            db_conn.commit()
            bot.reply_to(message, f"✅ تم التعديل بنجاح!\nمن: {old_p}\nإلى: {new_p} - {new_d}")
        except:
            bot.reply_to(message, "⚠️ خطأ! اكتب: تعديل اللوحة القديمة - اللوحة الجديدة - الاسم")

    # التسجيل والحفظ
    else:
        if '-' in text:
            p = text.split('-')
            if 'صيانة' in text:
                cursor.execute("INSERT INTO daily_log (type, plate, driver, details, time) VALUES (?,?,?,?,?)", ('صيانة', p[1].strip(), '', p[2].strip(), now))
            else:
                cursor.execute("INSERT INTO daily_log (type, plate, driver, details, time) VALUES (?,?,?,?,?)", ('جرد', p[0].strip(), p[1].strip(), '', now))
            bot.reply_to(message, "✅ تم التسجيل بنجاح.")
        else:
            cursor.execute("INSERT INTO daily_log (type, plate, driver, details, time) VALUES (?,?,?,?,?)", ('ملاحظة', '', '', text, now))
            bot.reply_to(message, "✅ تم حفظ الملاحظة.")
        db_conn.commit()

bot.polling(none_stop=True)
