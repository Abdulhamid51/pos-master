from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import requests
from api.models import Wallet, Debtor, Cart, Shop, Kirim, MOrder
import datetime
from django.contrib.humanize.templatetags.humanize import intcomma
from .views import abot_index
from django.urls import reverse

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip().lower()

        if 'callback_query' in data:
            callback = data['callback_query']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']  

            callback_data = json.loads(callback['data'])  
            remove_inline_buttons(chat_id, message_id)

            if callback_data['action'] == "confirm_payment":
                send_message(chat_id, "✅ To'lov tasdiqlandi!")
            elif callback_data['action'] == "reject_payment":
                kirim_id = callback_data.get('kirim_id')
                if kirim_id:
                    confirim_kirim(kirim_id)
                    send_message(chat_id, "⛔ To'lov rad etildi!")
                else:
                    send_message(chat_id, "⚠️ ID topilmadi.")
            
            return JsonResponse({"status": "ok"})
        
        if text == '/start':
            send_menu(chat_id)
        elif text in ['balans', '💰 balans', '💰 balans'.lower()]:
            balance_data = get_balance(chat_id)
            send_message(chat_id, f"📊 Sizning balansingiz:\n{balance_data}")
        elif text in ['buyurtmalar', '📝 buyurtmalar', '📝 buyurtmalar'.lower()]:
            send_order_period_menu(chat_id)
        elif text in ['buyurtma berish', '🛒 buyurtma berish', '🛒 buyurtma berish'.lower()]:
            mobile_cart_send(request, chat_id)  
        elif text == '30 kun':
            messages = get_order('bir oy', chat_id)
            for msg in messages:
                send_message(chat_id, msg)
        elif text == '1 yil':
            messages = get_order('bir yil', chat_id)
            for msg in messages:
                send_message(chat_id, msg)
        elif text == '🔙 orqaga':
            send_menu(chat_id)
        else:
            send_message(chat_id, "Menyudan foydalaning yoki 'balans' deb yozing.")

        return JsonResponse({"status": "ok"})
    else:
        return JsonResponse({"message": "Webhook ishlayapti"}, status=200)


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, json=payload)
    print(response.json())

import json

def remove_inline_buttons(chat_id, message_id):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/editMessageReplyMarkup"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": {}
    }
    response = requests.post(url, json=payload)
    print(response.json())


def send_kirim_message(chat_id, text, kirim_id):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id, 
        'text': text,
        'reply_markup':{
            "inline_keyboard": [
                [
                    {
                        "text": "✅ Tasdiqlash", 
                        "callback_data": json.dumps({"action": "confirm_payment"})
                    },
                    {
                        "text": "⛔ Notogri summa", 
                        "callback_data": json.dumps({"action": "reject_payment", "kirim_id": kirim_id})
                    }
                ]
            ]
        }
    }
    response = requests.post(url, json=payload)
    print(response.json())



def send_menu(chat_id):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': "Asosiy menyu:",
        'reply_markup': {
            'keyboard': [
                [{'text': '💰 Balans'}, {'text': '📝 Buyurtmalar'}, {'text':'🛒 Buyurtma berish'}]
            ],
            'resize_keyboard': True,
            'one_time_keyboard': False
        }
    }
    response = requests.post(url, json=payload)


def send_order_period_menu(chat_id):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': "🗓 Vaqt oralig'ini tanlang:",
        'reply_markup': {
            'keyboard': [
                [{'text': '30 kun'}, {'text': '1 yil'}],
                [{'text': '🔙 Orqaga'}]
            ],
            'resize_keyboard': True,
            'one_time_keyboard': False
        }
    }
    response = requests.post(url, json=payload)


def get_balance(chat_id):
    text = ""
    customer = Debtor.objects.filter(tg_id=chat_id).first()
    if not customer:
        return "Mijoz topilmadi."

    debts = Wallet.objects.filter(customer=customer).select_related("valyuta")

    if not debts.exists():
        return f"{customer.fio} uchun hech qanday qarz topilmadi."

    text += f"👤 {customer.fio}:\n"

    for debt in debts:
        text += f"💱 {debt.valyuta.name}: {intcomma(debt.summa)} Bugungi holatiga\n"

    return text


def confirim_kirim(kirim_id):
    kirim =  Kirim.objects.get(id=kirim_id)
    kirim.is_approved = False
    kirim.save()
    return True

import logging

logger = logging.getLogger(__name__)

def get_order(period, chat_id):
    try:
        today = datetime.date.today()
        if period == 'bir oy':
            start_date = today.replace(day=1)
        else:
            start_date = today.replace(month=1, day=1)

        orders = Shop.objects.filter(date__date__gte=start_date, date__date__lte=today, debtor__tg_id=chat_id)

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
                text += f"\t 📦 {x.product.name} \n"
                text += f"\t\t\t\t\t    {intcomma(x.quantity)} x {intcomma(x.price)} = {intcomma(x.total_price)}\n"
            messages.append(text.strip())

        return messages
    except Exception as ex:
        logger.error(f"Error fetching orders: {ex}")
        return [f"❌ Xatolik yuz berdi, keyinroq urinib ko'ring.\n{ex}"]


def send_order_url_only(order_id):
    path = reverse('abot_index', args=[order_id])
    full_url = f"https://ecomaruf.kabinett.uz/bot/{path}"
    return full_url



def mobile_cart_send(request, chat_id): 
    customer = Debtor.objects.filter(tg_id=chat_id).first()
    if not customer:
        send_message(chat_id, "❌ Mijoz topilmadi.")
        return

    m_order = MOrder.objects.create(debtor=customer)
    order_url = send_order_url_only(m_order.id)

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': "🛒 Buyurtma berish uchun tugmani bosing:",
        'reply_markup': {
            "inline_keyboard": [
                [
                    {
                        "text": "🛒 Buyurtma berish",
                        "url": order_url
                    }
                ]
            ]
        }
    }
    requests.post(url, json=payload)


    
    

    