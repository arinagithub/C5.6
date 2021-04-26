import telebot
import requests
import json

TOKEN = '1737742191:AAECLC161dJhI4iqyrq9WsMGp8F-zcAyBZw'

keys = {
    "евро": "EUR",
    "доллар": "USD",
    "рубль": "RUB",
}

class APIException(Exception):
    pass

class CryptoConverterBot:
    @staticmethod
    def get_price(base: str, quote: str, amount: str):
        if quote == base:
            raise APIException(f"Нельзя перевести одинаковые валюты! {base}")

        try:
            base_ticker = keys[base]
        except KeyError:
            raise APIException(f"Не удалось обработать валюту {base}")

        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise APIException(f"Не удалось обработать валюту {quote}")

        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f"Неправилно задано количество целевой валюты! {amount}")

        r = requests.get(f'https://api.exchangeratesapi.io/latest?symbols={quote_ticker}&base={base_ticker}')
        result = json.loads(r.content)['rates'][keys[quote]] * amount
        return result

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def assistance(message: telebot.types.Message):
    text = 'Привет! Я могу показать вам курсы обмена. Чтобы начать работу дайте команду боту в следующем формате:\n' \
           '<целевая валюта> <исходная валюта> <сумма перевода>\n' \
           'Между валютами один пробел и название валюты с маленькой буквы, например: "доллар рубль 1" \n '\
           'Чтобы узнать курсы обмена, нажмите: /values'
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:\n'
    for key in keys.keys():
        text += key + '\n'
    bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['text'])
def convert(message: telebot.types.Message):
    try:
        params = message.text.split(' ')

        if len(params) != 3:
            raise APIException('Слишком много или мало параметров \n /help')

        base, quote, amount = params

        total_result = CryptoConverterBot.get_price(base, quote, amount)
    except APIException as e:
        bot.send_message(message.chat.id, f'Ошибка пользователя.\n{e}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Не удалось обработать команду\n{e}')
    else:
        text = f'Цена {amount} {base} = {total_result} {quote}'
        bot.send_message(message.chat.id, text)

bot.polling(none_stop=True)
