import telebot
from telebot import types
import datetime
import http.server
import socketserver
import threading

# التوكن والمعرف الخاص بك
TOKEN = '8866021518:AAGZ2cvpnRDh5oiYx_-AoiRfoNSGuhw73eo'
ADMIN_ID = 8297381026 

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

RIGHTS = "\n\n— — — — — — — — — —\n© جميع الحقوق محفوظة لـ: وحيد ربعه 🦅"

# خادم وهمي لمنع Render من إغلاق السيرفر تلقائياً
def run_dummy_server():
    PORT = 8080
    Handler = socketserver.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton('🚨 رفع بلاغ استخباراتي'))
    
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton("👨‍💻 انضم للطاقم (تواصل مباشر)", url="https://t.me/Uhiied"))
    
    w_text = "👑 مرحباً بك في مركز عمليات وحدة الصقر\n\nهل تعرضت للنصب من متجر إلكتروني؟ أو تود الإبلاغ عن حساب مخترق، رقم واتساب مشبوه أو موقع زائف؟\nنحن هنا لحماية الفضاء الرقمي وتطهيره. اضغط على الزر أدناه لبدء رصد الهدف واختيار نوع بلاغك." + RIGHTS
    bot.send_message(message.chat.id, w_text, reply_markup=markup, parse_mode='Markdown')
    
    inst_text = "💡 للانضمام إلى طاقم العمل تحت قيادة وحيد ربعه ومحاربة الفساد الرقمي, اضغط على الزر أدناه للتوجه للمكتب مباشرة:"
    bot.send_message(message.chat.id, inst_text, reply_markup=inline_markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '🚨 رفع بلاغ استخباراتي')
def report_type(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🏪 متجر إلكتروني نصاب", callback_data="scam_shop"),
        types.InlineKeyboardButton("💬 واتساب مشبوه", callback_data="whatsapp"),
        types.InlineKeyboardButton("📸 انستقرام", callback_data="insta"),
        types.InlineKeyboardButton("🎥 تيك توك", callback_data="tiktok"),
        types.InlineKeyboardButton("🌐 موقع زائف", callback_data="scam_web")
    )
    bot.send_message(message.chat.id, "🎯 حدد نوع الهدف المراد رصده والتعامل معه:" + RIGHTS, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data in ["scam_shop", "whatsapp", "insta", "tiktok", "scam_web"])
def callback_inline(call):
    type_map = {"scam_shop": "متجر إلكتروني نصاب", "whatsapp": "واتساب", "insta": "انستقرام", "tiktok": "تيك توك", "scam_web": "موقع زائف"}
    target_type = type_map.get(call.data)
    msg = bot.send_message(call.message.chat.id, f"📝 أرسل الآن رابط أو رقم الـ {target_type} المراد الإبلاغ عنه:")
    bot.register_next_step_handler(msg, lambda m: ask_for_details(m, target_type))

def ask_for_details(message, target_type):
    target_link = message.text
    msg = bot.send_message(message.chat.id, "ℹ️ ما هي تفاصيل الشكوى وما نوع الضرر؟\n(سيتم رفعها مباشرة لمكتب القائد وحيد ربعه):")
    bot.register_next_step_handler(msg, lambda m: process_final_report(m, target_type, target_link))

def process_final_report(message, target_type, target_link):
    complaint_note = message.text
    user = message.from_user
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    admin_msg = f"📡 إشعار من رادار الاستخبارات\n— — — — — — — — — —\n🎯 النوع: {target_type}\n🔗 الرابط/الرقم: {target_link}\n📝 الشكوى: {complaint_note}\n\n👤 المصدر: @{user.username} (ID: {user.id})\n⏰ التوقيت: {time_now}\n— — — — — — — — — —\n⚡ القرار: بانتظار أوامر الصقر للرد والتنفيذ."
    
    admin_markup = types.InlineKeyboardMarkup(row_width=1)
    admin_markup.add(
        types.InlineKeyboardButton("🟢 تم الإغلاق بنجاح", callback_data=f"reply_success_{user.id}"),
        types.InlineKeyboardButton("🟡 الهدف تحت الرصد", callback_data=f"reply_tracking_{user.id}"),
        types.InlineKeyboardButton("🔴 بلاغ غير مكتمل", callback_data=f"reply_incomplete_{user.id}")
    )
    bot.send_message(ADMIN_ID, admin_msg, reply_markup=admin_markup, parse_mode='Markdown')
    
    user_markup = types.InlineKeyboardMarkup(row_width=2)
    user_markup.add(
        types.InlineKeyboardButton("⭐ 50 نجمة", callback_data="star_50"),
        types.InlineKeyboardButton("⭐ 250 نجمة", callback_data="star_250"),
        types.InlineKeyboardButton("⭐ 500 نجمة", callback_data="star_500"),
        types.InlineKeyboardButton("⭐ 1000 نجمة", callback_data="star_1000"),
        types.InlineKeyboardButton("⭐ 2500 نجمة", callback_data="star_2500"),
        types.InlineKeyboardButton("⭐ 5000 نجمة", callback_data="star_5000"),
        types.InlineKeyboardButton("⚙️ تخطي والإنهاء تلقائياً", callback_data="no_stars")
    )
    
    u_msg = "🎖️ تم تسجيل بلاغك بنجاح وسيتولى القائد وحيد ربعه وفريق الرصد مراجعة الهدف فوراً.\n\n💎 **تطوير الوحدة:** للمساهمة في تعزيز قدرات رادارات الصقر وتطوير أنظمة الحماية الرقمية المستقلة، يمكنك دعم المنصة عبر الخيارات الاختيارية أدناه:" + RIGHTS
    bot.send_message(message.chat.id, u_msg, reply_markup=user_markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_") or call.data in ["star_50", "star_250", "star_500", "star_1000", "star_2500", "star_5000", "no_stars"])
def handle_all_callbacks(call):
    if call.data.startswith("reply_"):
        data_parts = call.data.split("_")
        action = data_parts[1]
        target_user_id = data_parts[2]
        
        if action == "success":
            reply_text = "🛡️ إشعار رسمي من مكتب القائد:\n\nأبشرك، تم التعامل مع الهدف ورصده وإغلاقه بنجاح عبر رادارات وحيد ربعه. شكراً لحسك الأمني وجاهزيتك." + RIGHTS
            status_label = "🟢 تم الإغلاق بنجاح"
        elif action == "tracking":
            reply_text = "📡 إشعار رسمي من مكتب القائد:\n\nتم استلام بلاغك بعناية، والهدف الآن تحت الرصد المباشر وجاري تصفية نشاطه المشبوه." + RIGHTS
            status_label = "🟡 الهدف تحت الرصد"
        elif action == "incomplete":
            reply_text = "⚠️ إشعار رسمي من مكتب القائد:\n\nعذراً، الرابط أو الرقم المرسل في بلاغك غير مكتمل أو غير صحيح. يرجى إعادة إرسال البيانات بدقة لبدء الرصد." + RIGHTS
            status_label = "🔴 بلاغ غير مكتمل"
            
        try:
            bot.send_message(target_user_id, reply_text, parse_mode='Markdown')
            bot.answer_callback_query(call.id, "تم إرسال الرد")
            bot.edit_message_text(f"{call.message.text}\n\n✅ **حالة الإجراء:** {status_label}", call.message.chat.id, call.message.message_id)
        except Exception as e:
            bot.answer_callback_query(call.id, "فشل الإرسال")

    elif call.data in ["star_50", "star_250", "star_500", "star_1000", "star_2500", "star_5000", "no_stars"]:
        if call.data == "no_stars":
            bot.answer_callback_query(call.id, "تم حفظ البلاغ")
            bot.edit_message_text("🎖️ تم تسجيل بلاغك بنجاح ومتابعته جارية الآن من قبل فريق وحيد ربعه." + RIGHTS, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
        else:
            amount_map = {
                "star_50": 50, "star_250": 250, "star_500": 500, "star_1000": 1000, "star_2500": 2500, "star_5000": 5000
            }
            amount = amount_map.get(call.data)
            prices = [types.LabeledPrice(label="تطوير رادار الصقر", amount=amount)]
            try:
                bot.send_invoice(
                    call.message.chat.id, title="⭐ المساهمة في تطوير الوحدة", 
                    description=f"تخصيص مساهمة بقيمة {amount} نجمة لترقية الخوادم وتوسيع رادار رصد المخاطر الرقمية.", 
                    provider_token="", currency="XTR", prices=prices, 
                    start_parameter="support-stars", invoice_payload=f"payload_stars_{amount}"
                )
            except Exception as e:
                bot.answer_callback_query(call.id, "حدث خطأ أثناء معالجة النجوم")

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id, "❤️ نشكر لك مساهمتك القيمة وثقتك. تم استلام النجوم بنجاح وسنظل دائماً درعكم المرصود في الفضاء الرقمي." + RIGHTS, parse_mode='Markdown')
    bot.send_message(ADMIN_ID, f"🔔 **إشعار دعم جديد:**\nقام المستخدم @{message.from_user.username} بتقديم مساهمة لتطوير البوت تضامناً مع وحدة الصقر الاستخباراتية! 🔥")

if __name__ == '__main__':
    # تشغيل خادم وهمي لـ Render في الخلفية
    threading.Thread(target=run_dummy_server, daemon=True).start()
    print("🦅 رادار وحدة الصقر يعمل الآن على سيرفر Render العالمي...")
    bot.polling(non_stop=True)
