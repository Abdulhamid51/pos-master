import os
import sys
import django
import json
import requests
import datetime
import time
from django.contrib.humanize.templatetags.humanize import intcomma

# === 1️⃣ Django muhitini yuklaymiz ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# ⚠️ Loyihangiz nomini yozing (settings.py joylashgan papka)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'domstroy.settings')
django.setup()

from django.conf import settings
from api.models import Wallet, Debtor, Cart, Shop, Kirim, MOrder


# === 2️⃣ Asosiy funksiyalar ===

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print("Xabar yuborishda xatolik:", e)


def send_menu(chat_id):
    web_app_url = f"https://ecomaruf.kabinett.uz/bot/abot_index/{chat_id}"
    payload = {
        'keyboard': [
            [{'text': '💰 Balans'}, {'text': '📝 Buyurtmalar'}],
            [{
                'text': '🛒 Buyurtma berish',
                'web_app': {'url': web_app_url}
            }]
        ],
        'resize_keyboard': True,
        'one_time_keyboard': False
    }
    send_message(chat_id, "Asosiy menyu:", reply_markup=json.dumps(payload))


def send_order_period_menu(chat_id):
    payload = {
        'keyboard': [
            [{'text': '30 kun'}, {'text': '1 yil'}],
            [{'text': '🔙 Orqaga'}]
        ],
        'resize_keyboard': True,
        'one_time_keyboard': False
    }
    send_message(chat_id, "🗓 Vaqt oralig'ini tanlang:", reply_markup=json.dumps(payload))


def get_balance(chat_id):
    customer = Debtor.objects.filter(tg_id=chat_id).first()
    if not customer:
        return "Mijoz topilmadi."

    debts = Wallet.objects.filter(customer=customer).select_related("valyuta")
    if not debts.exists():
        return f"{customer.fio} uchun hech qanday qarz topilmadi."

    text = f"👤 {customer.fio}:\n"
    for debt in debts:
        text += f"💱 {debt.valyuta.name}: {intcomma(debt.summa)} Bugungi holatiga\n"
    return text


def get_order(period, chat_id):
    try:
        today = datetime.date.today()
        if period == 'bir oy':
            start_date = today.replace(day=1)
        else:
            start_date = today.replace(month=1, day=1)

        orders = Shop.objects.filter(
            date__date__gte=start_date,
            date__date__lte=today,
            debtor__tg_id=chat_id
        )

        if not orders.exists():
            return ["📝 Hech qanday buyurtma topilmadi."]

        messages = []
        for order in orders:
            text = f"{order.debtor.fio} - {intcomma(order.total_price)} {order.valyuta.name if order.valyuta else '-'}\n"
            if order.date:
                text += f"📅 Buyurtma vaqti: {order.date.strftime('%Y-%m-%d %H:%M')}\n"
            if order.debt_return:
                text += f"🚚 Yetkazib berish vaqti: {order.debt_return.strftime('%Y-%m-%d')}\n"

            for x in Cart.objects.filter(shop=order):
                text += f"\t 📦 {x.product.name}\n"
                text += f"\t\t{intcomma(x.quantity)} x {intcomma(x.price)} = {intcomma(x.total_price)}\n"

            messages.append(text.strip())
        return messages
    except Exception as ex:
        return [f"❌ Xatolik yuz berdi: {ex}"]


# === 3️⃣ Polling jarayoni ===
def run_bot():
    print("🤖 Bot ishga tushdi... polling rejimida")
    offset = 0

    while True:
        try:
            # Telegramdan yangi xabarlarni olish
            url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"
            response = requests.get(url, params={"offset": offset + 1, "timeout": 20})
            result = response.json().get("result", [])

            for update in result:
                offset = update["update_id"]
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text", "").strip().lower()

                if not chat_id or not text:
                    continue

                print(f"📩 {chat_id}: {text}")

                # === Buyruqlar ===
                if text == "/start":
                    send_menu(chat_id)
                elif text in ["balans", "💰 balans", "💰 balans".lower()]:
                    send_message(chat_id, f"📊 Sizning balansingiz:\n{get_balance(chat_id)}")
                elif text in ["buyurtmalar", "📝 buyurtmalar", "📝 buyurtmalar".lower()]:
                    send_order_period_menu(chat_id)
                elif text in ["buyurtma berish", "🛒 buyurtma berish", "🛒 buyurtma berish".lower()]:
                    web_app_url = f"https://ecomaruf.kabinett.uz/abot/abot_index/{chat_id}/"
                    reply_markup = json.dumps({
                        "inline_keyboard": [[{
                            "text": "🛒 Buyurtma berish",
                            "web_app": {"url": web_app_url}
                        }]]
                    })
                    send_message(chat_id, " ", reply_markup=reply_markup)
                elif text == "30 kun":
                    for msg in get_order("bir oy", chat_id):
                        send_message(chat_id, msg)
                elif text == "1 yil":
                    for msg in get_order("bir yil", chat_id):
                        send_message(chat_id, msg)
                elif text == "🔙 orqaga":
                    send_menu(chat_id)
                else:
                    send_message(chat_id, "Menyudan foydalaning yoki 'balans' deb yozing.")

        except Exception as e:
            print("❌ Xatolik:", e)

        time.sleep(2)


# === 4️⃣ Ishga tushirish ===
if __name__ == "__main__":
    run_bot()
