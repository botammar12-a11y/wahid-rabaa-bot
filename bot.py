import telebot
from telebot import types
from datetime import datetime
import sqlite3
import os

# إعدادات نظام شركة راما - وحيد ربعه 🦅
TOKEN = "8691027108:AAE9_0t4Xko8qAO7NGs9OjlOnna90jX7_bw"
ADMIN_ID = 8297381026
bot = telebot.TeleBot(TOKEN)
start_work_time = datetime.now().strftime("%Y-%m-%d %H:%M")

# إنشاء قاعدة بيانات شركة راما
def init_db():
    conn = sqlite3.connect('rama_system.db', check_same_thread=False)
    cursor = conn.cursor()
    # الجدول: النوع، العامل، المسؤول، اللوحة/المهمة، الوقت
    cursor.execute('''CREATE TABLE IF NOT EXISTS rama_logs 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, worker TEXT, boss TEXT, details TEXT, time TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

# لوحة التحكم الرئيسية (أزرار وحيد ربعه)
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('👷 سجل العمال والأوامر', '🏗 تسجيل حركة (أمر شغل)')
    markup.add('🚛 جرد (شركة راما)', '🚜 جرد (مستأجر)')
    markup.add('🏁 تصدير كشف شركة راما', '📊 عرض الجرد')
    markup.add('🗑 مسح السجل', '🔙 حذف آخر إدخال')
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.from_user.id == ADMIN_ID:
        msg = (f"يا هلا بالقائد وحيد ربعه! 🦅🔥\n\n"
               f"نظام شركة راما للرقابة الميدانية جاهز.\n"
               f"وقت بدء الشفت: {start_work_time}\n"
               f"سأقوم بتنظيم الكشوفات وإصدارها في ملفات رسمية.")
        bot.send_message(message.chat.id, msg, reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: True)
def handle_operations(message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text
    now = datetime.now().strftime("%H:%M")
    cursor = db_conn.cursor()

    if text == '👷 سجل العمال والأوامر':
        bot.reply_to(message, "تسجيل مرافق 👷\nأرسل: اسم العامل - اسم المسؤول - المهمة")

    elif text == '🏗 تسجيل حركة (أمر شغل)':
        bot.reply_to(message, "أمر شغل ⚙️\nأرسل: اللوحة - المكان - اسم المسؤول")

    elif text == '🏁 تصدير كشف شركة راما':
        cursor.execute("SELECT * FROM rama_logs")
        rows = cursor.fetchall()
        if not rows: return bot.reply_to(message, "لا توجد بيانات لتصدير الكشف.")
        
        # ترويسة الملف الرسمي
        content = f"--- كشف تشغيل يومي - شركة راما ---\n"
        content += f"إشراف الميدان: وحيد ربعه\n"
        content += f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}\n"
        content += f"وقت البداية: {start_work_time}\n"
        content += "="*35 + "\n\n"
        
        for r in rows:
            if r[1] == 'عمال':
                content += f"👷 [عامل] {r[2]} | [بأمر] {r[3]} | {r[4]} | 🕒 {r[5]}\n"
            elif r[1] == 'حركة':
                content += f"⚙️ [أمر شغل] لوحة {r[4]} | [مسؤول] {r[3]} | 🕒 {r[5]}\n"
            elif r[1] == 'جرد':
                content += f"🚛 [جرد] {r[4]} | 🕒 {r[5]}\n"
        
        file_name = f"Rama_Report_{datetime.now().strftime('%d_%m')}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)
        
        with open(file_name, "rb") as f:
            bot.send_document(message.chat.id, f, caption=f"📄 تفضل يا وحيد ربعه، كشف شركة راما جاهز للرفع.")
        os.remove(file_name)

    elif text == '🗑 مسح السجل':
        cursor.execute("DELETE FROM rama_logs")
        db_conn.commit()
        bot.reply_to(message, "🗑 تم تصفير الكشوفات. شفت جديد موفق!")

    elif text == '🔙 حذف آخر إدخال':
        cursor.execute("DELETE FROM rama_logs WHERE id = (SELECT MAX(id) FROM rama_logs)")
        db_conn.commit()
        bot.reply_to(message, "✅ تم حذف آخر عملية مسجلة.")

    # معالجة وحفظ البيانات مع (-)
    else:
        if '-' in text:
            parts = text.split('-')
            if len(parts) == 3: # عمال أو أوامر شغل
                if any(word in text for word in ['موقع', 'كسارة', 'شغل']):
                    cursor.execute("INSERT INTO rama_logs (type, boss, details, time) VALUES (?,?,?,?)", 
                                   ('حركة', parts[2].strip(), parts[0].strip(), now))
                else:
                    cursor.execute("INSERT INTO rama_logs (type, worker, boss, details, time) VALUES (?,?,?,?,?)", 
                                   ('عمال', parts[0].strip(), parts[1].strip(), parts[2].strip(), now))
            elif len(parts) == 2: # جرد
                comp = "شركة راما" if "مستأجر" not in text else "مستأجر"
                cursor.execute("INSERT INTO rama_logs (type, details, time) VALUES (?,?,?)", 
                               ('جرد', f"[{comp}] {text}", now))
            db_conn.commit()
            bot.reply_to(message, "✅ تم الحفظ في الكشف.")
        else:
            bot.reply_to(message, "⚠️ يرجى استخدام العلامة (-) بين البيانات للتنظيم.")

bot.polling(none_stop=True)
