import json
import time
import urllib.request
import urllib.parse

BOT_TOKEN = "8112333867:AAGxyUmwP0P_5aIcs5zbIeqP6Tr4mqvrkuI"
ADMIN_ID = "8190368560"
USERS_FILE = "users.json"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# تحميل المستخدمين أو إنشاء جديد
try:
    with open(USERS_FILE, "r") as f:
        user_data = json.load(f)
except:
    user_data = {}

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(user_data, f)

# إرسال رسالة مع دعم Markdown
def send_message(chat_id, text):
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }).encode()
    urllib.request.urlopen(BASE_URL + "sendMessage", data=data)

# الحصول على التحديثات
def get_updates(offset=None):
    url = BASE_URL + "getUpdates"
    if offset:
        url += f"?offset={offset}"
    response = urllib.request.urlopen(url).read()
    return json.loads(response)

# التشغيل الرئيسي
def main():
    last_update_id = None
    print("🤖 Bot is running 24/7 in background...")
    while True:
        updates = get_updates(last_update_id)
        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1
            message = update.get("message")
            if not message:
                continue
            chat_id = str(message["chat"]["id"])
            text = message.get("text", "")

            # حفظ المستخدمين
            if chat_id not in user_data:
                user_data[chat_id] = True
                save_users()

            # أمر /start
            if text == "/start":
                welcome_text = (
                    "👋 Hello! Welcome to our amazing Telegram bot!\n"
                    "✨ This bot is super fast and shows your unique ID below."
                )
                # مسافة فارغة + ID ككود
                send_message(chat_id, f"{welcome_text}\n\n`{chat_id}`")

            # أمر /stats للمشرف
            elif text == "/stats" and chat_id == ADMIN_ID:
                total = len(user_data)
                latest = list(user_data.keys())[-10:]
                latest_str = ", ".join(latest) if latest else "No users yet"
                send_message(chat_id, f"📊 Total users: {total}\n🆕 Latest 10: {latest_str}")

            # أمر /broadcast للمشرف
            elif text.startswith("/broadcast") and chat_id == ADMIN_ID:
                parts = text.split(" ", 1)
                if len(parts) < 2:
                    send_message(chat_id, "⚠️ Usage: /broadcast Your message here")
                    continue
                msg = parts[1]
                count = 0
                for uid in user_data.keys():
                    try:
                        send_message(uid, msg)
                        count += 1
                    except:
                        continue
                send_message(chat_id, f"✅ Message sent to {count} users.")

        # تقليل وقت الانتظار لزيادة سرعة الاستجابة
        time.sleep(0.3)  # أسرع من 1 ثانية، لا يضغط كثير على Telegram API

if __name__ == "__main__":
    main()